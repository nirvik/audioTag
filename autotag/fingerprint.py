import acoustid
import musicbrainzngs
import subprocess
import sys
import json


class FingerPrinterException(Exception):

    def __init__(self, mesg, error_code):
        self.mesg = mesg
        self.code = error_code

    def __str__(self):
        return self.code + ':' + self.message


class FingerPrinter(object):

    def __init__(self, file_name):
        self.fingerprint = None
        self.duration = None
        self.recording_ids = {}
        self.acoustids = []
        self.scores = {}
	self.artists = {} 
	self.song = {} 
        try:
            fpprocess = subprocess.Popen(
                ['fpcalc', file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            raise FingerPrinterException('Chromaprint not found', 1)

        answer, error = fpprocess.communicate()
        if error != '':
            raise FingerPrinterException('Invalid song/file', 2)
        length, score = answer.split('\n')[1], answer.split('\n')[-2]
        self.fingerprint, self.duration = score[
            score.find('=') + 1:], length[length.find('=') + 1:]


    def parse_result(self):

        json_file = acoustid.lookup('S0xa1BKE', self.fingerprint, self.duration)
	for result in json_file['results']:
            self.acoustids.append(result['id'])
            self.scores[result['id']] = result['score']
	   
            if 'recordings' in result:
                rids = [] # Recording Ids 
		artists = []
		song_name = [] 
                for recording in result['recordings']:
                    rids.append(recording['id'])
		    song_name.append(recording['title'])
                    for person in recording['artists']:
                        artists.append(person['name'])
                self.recording_ids[result['id']] = rids
                self.artists[result['id']] = set(artists)
		self.song[result['id']] = set(song_name)



if __name__ == '__main__':
    FILE = sys.argv[1]
    finger = FingerPrinter(FILE)
    finger.parse_result()
    print finger.recording_ids.keys()#,finger.acoustids,finger.score
    print finger.scores
    print finger.artists
    print finger.song
    for i in finger.recording_ids.items():
        print i

'''
Get the fingerprint 
Use the acoustid web service to get enter the fingerprint 
The webservice will query the fingerprint in the musicbrainz database 
'''
