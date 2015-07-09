import acoustid
import musicbrainzngs
from  fingerprint import *
import datetime
import random
import operator
import requests
import urllib
import json

class MusicUtilsException(Exception):
    def __init__(self,code,msg):
        self.msg = msg
        self.code = code

    def __str__(self):
        return '[Error :{0}] => {1}'.format(self.code , self.msg)

class MusicUtils(object):

    __doc__ = 'A bunch of utilities provided to extract information from the musicbrainzngs'
    __version__ = '0.0.1'
    imageurl = 'http://coverartarchive.org/release/'
    API_KEY = 'S0xa1BKE'
    musicbrainzngs.auth('','')  # username  , password
    musicbrainzngs.set_useragent('Auto Tagger', '0.1', 'nirvik1993@gmail.com')

    def __init__(self , fingerprint = None , duration = None ):
        self._mbid = None # The MBID
        self._mbid_dates = {} # mbid to release dates
        self._mbids = {} # Recording id to release id's
        self._song_details = {} # Bunch of details about the music that we can use in the future
        self._backup_date = {}
        self._fingerprint = fingerprint
        self.duration = duration
        self.song_title =None
        self.artist = None
        self.album = None
        self.date = None
        # We dont want this to have public access
        self._scores = {}
        self._recording_ids = {}

    @classmethod
    def feedfingerprint(cls,fingerprint,duration):
        return cls(fingerprint , duration)


    @property
    def mbids(self):
	'''
	Keys : recording ids
	Values : bunch of MBIDS
	'''
        return self._mbids

    @property
    def song_details(self):
	'''
	Contains response about the song from musicbrainz
	'''
        return self._song_details

    @property
    def mbid(self):
	'''
	The final decided MBID
	'''
        return self._mbid


    @property
    def recording_ids(self):
        return self._recording_ids

    @property
    def mbid_dates(self):
        '''
        Say you want to view the original date of the respective mbid
        key : mbid
        value : release date
        '''
        return self._mbid_dates


    @mbid_dates.setter
    def mbid_dates(self,val):
        '''
        Having the setter properties , so that you dont mess much with the mbid_dates
        '''
        if isinstance(val,dict) :
            self._mbid_dates = val

    def extractdates(self,details):
        '''
        Extract all the dates.
        Basically populates the mbid_dates with the apporpriate data , i.e mbid => date
        '''
        for key,value in details.iteritems():
            for j in value:
                try:
                    self.mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M-%d')
                except:
                    try:
                        self.mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M')
                    except:
                        try:
                            self.mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y')
                        except:
                            pass
                self._backup_date[j['id']] = key


    def latestmbid(self,details):
        '''
        Gets the information about the latest track of the song and returns the song's mbid
        '''
        self.extractdates(details)
        try:
            self._mbid , self.date =  max(self._mbid_dates.iteritems(),key = operator.itemgetter(1))
        except:
            self._mbid ,self.date =  (random.choice(self._backup_date.keys()),'2015')
        return (self._mbid , self.date)


    def extract_album_name(self,coverart_mbid):
        ''' Get the album name  '''
        key = ''
        for i,j in self._mbids.iteritems():
            for k in j :
                if coverart_mbid in j:
                    key = i
                    break
        try:
            self.album =  self._song_details[key][0]['title'].encode('utf-8')
        except:
            self.album = ''
        return self.album


    def recording_details(self,recording_ids):
        '''
        We need to store more information . As of now , storing only release id to get the album art in future
        '''
        for rid in recording_ids:
            release_ids = []
            try:
                data  = musicbrainzngs.get_recording_by_id(rid,includes=['releases'])['recording']
                for i in data['release-list']:
                    try:
                        if i['status'] == 'Official':
                            release_ids.append(i['id'])
                    except:
                        pass
                    self._mbids[rid] = release_ids
                    self._song_details[rid] = data['release-list']
            except musicbrainzngs.WebServiceError as exc:
                print("Something went wrong with the request: %s" % exc)
                raise FingerPrinterException('Something wrong with the request. ',3)
        return (self._mbids,self._song_details)


    @staticmethod
    def album_art(art_mbid):
        '''
            Takes MBID as the argument and downloads the image for the music
        '''
        cover_art_json = requests.get(MusicUtils.imageurl+art_mbid).text
        try:
            response = json.loads(cover_art_json)
        except:
            location , header = '' , {'content-type':'failed','content-length':0}
            return (location , header )
        try:
            picture = response['images'][0]['image']
            print picture
            location , header = urllib.urlretrieve(picture,"filename.jpeg")
        except :
            print response
            print cover_art_json
            print 'There is no album art for this file '
            location = ''
            header = {'content-type':'failed','content-length':0}
        print ' Image located in {0} and downloaded {1} '.format(location,header['content-length'])
        if header['content-type'] == 'image/jpg':
            header['content-type'] = 'image/jpeg'
        if header['content-type'] != 'failed':
            return (location , header)
        else :
            raise MusicUtilsException('1','Image not found')

    def bestacoustid(self):
        return max(self._scores.iteritems(),key=operator.itemgetter(1))


    def parse_result(self):
        '''
        Makes a request to acoustid web service
        Parses the response
        Aggregates the necessary scores , recording ids , mbids , artist and song title
        '''
        acoustids = []
        json_file = acoustid.lookup(MusicUtils.API_KEY , self._fingerprint , self.duration)
        temp_song  = {}
        temp_artist = {}
        if json_file['status'] != u'ok' or len(json_file['results'])==0:
            raise MusicUtilsException('2','Bad look up, ended with a bad status report')
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
        self.song_title , self.artist =  max(temp_song.iteritems(), key = operator.itemgetter(1))[0].encode('utf-8') , max(temp_artist.iteritems(), key = operator.itemgetter(1))[0].encode('utf-8')

if __name__ == '__main__':
    import sys
    from tag import *
    music = sys.argv[1]
    finger = FingerPrinter(music)
    query = MusicUtils.feedfingerprint(finger.fingerprint , finger.duration)
    query.parse_result()
    best_acoust , score = query.bestacoustid()
    mbids , details = query.recording_details(query.recording_ids[best_acoust])
    coverart_mbid , date = query.latestmbid(details)
    album_name = query.extract_album_name(coverart_mbid)
    metadata = {}
    metadata['title'] = unicode(query.song_title)
    metadata['artist'] = unicode(query.artist)
    metadata['date'] = unicode(query.date)
    metadata['album-art-mbid'] = unicode(coverart_mbid)
    metadata['album'] = query.album
    metadata['duration'] = query.duration
    trialtag(music,metadata)
    print ' Artist :{0} \n Album  :{1} \n Song   :{2} \n Date   :{3} \n Duration:{4} \n mbid   :{5}'.format(query.artist,query.album,query.song_title,query.date,query.duration,query.mbid)
