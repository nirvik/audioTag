import acoustid
import musicbrainzngs
import subprocess
import sys
import json
import operator 

class FingerPrinterException(Exception):

    def __init__(self, mesg, error_code):
        self.mesg = mesg
        self.code = error_code

    def __str__(self):
        return self.code + ':' + self.message


class FingerPrinter(object):

    __version__ = '0.0.1'
    __doc__ = ' Fingerprinting the audio file '

    def __init__(self, file_name):
        self._fingerprint = None
        self._duration = None
        try:
            fpprocess = subprocess.Popen(
                ['fpcalc', file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            raise FingerPrinterException('Chromaprint not found', 1)

        answer, error = fpprocess.communicate()
	self._fingerprint , self._duration = self.fingerprintoutput(answer)

    @staticmethod
    def fingerprintoutput(answer):	
        length, score = answer.split('\n')[1], answer.split('\n')[-2]
        fingerprint_value, duration = score[
            score.find('=') + 1:], length[length.find('=') + 1:]
	return (fingerprint_value , duration) 

    @property
    def fingerprint(self):
    	return self._fingerprint

    
    @fingerprint.setter
    def fingerprint(self,val):
    	if val is None or len(val)==0:
	    raise FingerPrinterException('Invalid FingerPrint',2)
    	self._fingerprint = val

    @property
    def duration(self):
    	return self._duration 

    @duration.setter
    def duration(self,val):
        if val is None or len(val)==0:
	    raise FingerPrinterException('Invalid Duration' , 3 ) 
	self._duration = val


class AcoustQueryException(Exception):
    
    def __init__(msg,code):
    	self.msg = msg 
	self.code = code 

    def __str__(self):
        return 'Error Code [{0}] : {1}'.format(self.code , self.msg)

class AcoustQuery(object):
    
    __version__ = '0.0.1'
    __doc__ = 'This class will take the fingerprint and duration as argument and perform a lookup operation'
    API_KEY = 'S0xa1BKE'
    
    def __init__(self,fingerprint,duration):
    	self._fingerprint = fingerprint
	self._duration = duration
        self._song_title = None
        self._artist = None 
        self._scores = {}
        self._recording_ids = {} 
    @property
    def song_title(self):
   	return self._song_title.encode('utf-8')

    @property
    def duration(self):
        return self._duration

    @property
    def artist(self):
        return self._artist.encode('utf-8')

    @property
    def recording_ids(self):
        return self._recording_ids
    
    def bestacoustid(self):
        return max(self._scores.iteritems(),key=operator.itemgetter(1))
    
    def parse_result(self):
        acoustids = []
        json_file = acoustid.lookup(AcoustQuery.API_KEY , self._fingerprint , self._duration) 
	temp_song  = {}
        temp_artist = {}
	if json_file['status'] != u'ok' or len(json_file['results'])==0:
	    raise AcoustQueryException('Bad look up, ended with a bad status report','1')
	for result in json_file['results']:
            acoustids.append(result['id'])
            self._scores[result['id']] = result['score']
            if 'recordings' in result:
                rids = [] # Recording Ids 
                for recording in result['recordings']:
                    rids.append(recording['id'])
		    try:
	  	        if recording['title'] in temp_song:
		            temp_song[recording['title']] += 1
		        else:
		    	    temp_song[recording['title']] = 0 
		    except:
			pass	
		    try:
		    	name = '' 
			ok = False
                        for person in recording['artists']:
			    if 'joinphrase' in person:
			    	name +=  person['name'] +person['joinphrase']
				ok = True
				continue
			    			    
			    #adding the last artist 
			    if ok:
			        name = name + ' ' + person['name']
			    else:
				name = person['name']
                            if name in temp_artist :
                                temp_artist[name] +=1
                            else:
                                temp_artist[name] = 0
		    except:
			pass
            self.recording_ids[result['id']] = rids
	self._song_title , self._artist =  max(temp_song.iteritems(), key = operator.itemgetter(1))[0] , max(temp_artist.iteritems(), key = operator.itemgetter(1))[0]


if __name__ == '__main__':
    import os  
    base = '/home/nirvik/Music/'
    for FILE in os.listdir(base):
	print FILE
	try:
            x = FingerPrinter(base+FILE)
            y = AcoustQuery(x.fingerprint,x.duration)
            y.parse_result()
            print y.song_title+ ' ' + y.artist
	    print '**************************'
	except:
	    print 'Exception occured for {0}'.format(FILE)
	    pass
'''
Get the fingerprint 
Use the acoustid web service to get enter the fingerprint 
The webservice will query the fingerprint in the musicbrainz database 
'''
