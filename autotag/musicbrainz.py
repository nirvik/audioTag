import acoustid
import musicbrainzngs
from  fingerprint import FingerPrinter
from datetime import datetime
import random
import operator
import requests
import urllib
import json
from BeautifulSoup import BeautifulSoup
from tagutils import *



class MusicUtilsException(Exception):
    def __init__(self,code,msg):
        self.msg = msg
        self.code = code

    def __str__(self):
        return '[Error :{0}] => {1}'.format(self.code , self.msg)

def parse_result(json_file):
    '''
    Parses the response
    Aggregates the necessary scores , recording ids , mbids , artist and song title
    '''
    temp_song  = {}
    temp_artist = {}
    scores = {}
    recording_ids = {}
    rids = []
    if json_file['status'] != u'ok' or len(json_file['results'])==0:
        raise MusicUtilsException('3','Bad look up, ended with a bad status report')
    for result in json_file['results']:
        scores[result['id']] = result['score']
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
        if rids == []:
            raise MusicUtilsException(5,'Not a good response')
        recording_ids[result['id']] = rids
    return (scores , recording_ids , temp_song , temp_artist)



class MusicUtils(object):

    __doc__ = 'A bunch of utilities provided to extract information from the musicbrainzngs'
    __version__ = '0.0.1'
    base_image_url = 'http://coverartarchive.org/release/'
    musicbrainz_image_url = 'https://musicbrainz.org/release/{0}/cover-art'
    musicbrainzngs.auth('','')  # username  , password
    musicbrainzngs.set_useragent('Auto Tagger', '0.1', 'nirvik1993@gmail.com')

    def __init__(self ,
            API_KEY,
            fingerprint = None ,
            duration = None,
            mbid = None,
            song_details = None,
            song_title = None,
            artist = None,
            album = None,
            date = None,
            scores = None,
            recording_ids = None,
            mbids = None,
            best_acoust_id = None,
            best_score = None,
            cover_art_url = None):

        if API_KEY == None or len(API_KEY) == 0:
            raise MusicUtilsException('1','Invalid API KEY')
        self.API_KEY = API_KEY
        self.mbid = mbid # The MBID
        self.duration = duration
        self.song_title = song_title
        self.artist = artist
        self.album = album
        self.date = date
        self.cover_art_url = cover_art_url
        self.best_acoustid = best_acoust_id #The one with the best score
        self.best_score = best_score # The score accuracy
        # We dont want this to have public access
        self._scores = scores
        self._recording_ids = recording_ids
        self._backup_date = {}
        self._fingerprint = fingerprint
        self._mbid_dates = {} # mbid to release dates
        self._mbids = mbids # Recording id to release id's
        self._song_details = song_details # Bunch of details about the music that we can use in the future

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
    def recording_ids(self):
        return self._recording_ids

    def _extractdates(self,details):
        '''
        Extract all the dates.
        Basically populates the mbid_dates with the apporpriate data , i.e mbid => date
        '''
        for key,value in details.iteritems():
            for j in value:
                try:
                    self._mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M-%d')
                except:
                    try:
                        self._mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M')
                    except:
                        try:
                            self._mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y')
                        except:
                            pass

                self._backup_date[j['id']] = key


    def _latestmbid(self,details):
        '''
        Gets the information about the latest track of the song and returns the song's mbid
        '''
        self._extractdates(details)
        try:
            mbid , date =  max(self._mbid_dates.iteritems(),key = operator.itemgetter(1))
        except Exception as e:
            print e
            mbid ,date =  (random.choice(self._backup_date.keys()),'2015')
        return (mbid , date)


    def _extract_album_name(self,coverart_mbid):
        ''' Get the album name  '''
        key = ''
        for i,j in self._mbids.iteritems():
            for k in j :
                if coverart_mbid in j:
                    key = i
                    break
        try:
            album =  self._song_details[key][0]['title'].encode('utf-8')
        except:
            album = ''
        return album

    @staticmethod
    def _recording_details(recording_ids):
        '''
        We need to store more information . As of now , storing only release id to get the album art in future
        '''
        mbids = {}
        song_details = {}
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
                    mbids[rid] = release_ids
                    song_details[rid] = data['release-list']
            except musicbrainzngs.WebServiceError as exc:
                print("Something went wrong with the request: %s" % exc)
                raise MusicUtilsException('4','Something wrong with the request. ')
        return (mbids,song_details)


    @staticmethod
    def _bestacoustid(scores):
        return max(scores.iteritems(),key=operator.itemgetter(1))

    def lookup(self):
        json_file = acoustid.lookup(self.API_KEY , self._fingerprint , self.duration)
        if 'error' in json_file:
            raise MusicUtilsException(json_file['error']['code'],json_file['error']['message'])
        self._scores , self._recording_ids , temp_song, temp_artist =  parse_result(json_file)
        self.song_title , self.artist =  max(temp_song.iteritems(), key = operator.itemgetter(1))[0].encode('utf-8') , max(temp_artist.iteritems(), key = operator.itemgetter(1))[0].encode('utf-8')
        self._best_acoust ,self._best_score = self._bestacoustid(self._scores)
        self._mbids,self._song_details = self._recording_details(self._recording_ids[self._best_acoust])
        self.mbid ,self.date = self._latestmbid(self._song_details)
        self.album = self._extract_album_name(self.mbid)
        return MusicUtils(API_KEY= self.API_KEY,
                scores = self._scores,
                recording_ids = self._recording_ids,
                song_title = self.song_title,
                artist = self.artist ,
                best_acoust_id = self._best_acoust,
                best_score = self._best_score,
                mbids = self._mbids,
                song_details= self._song_details,
                mbid= self.mbid,
                date= self.date,
                album=self.album,
                #backup_date = self._backup_date,
                fingerprint = self._fingerprint,
                duration = self.duration,
                cover_art_url = MusicUtils.base_image_url + self.mbid
                #mbid_dates=self._mbid_dates
                )

if __name__ == '__main__':
    import sys
    import os
    API = os.environ.get('ACOUSTID_API_KEY')
    FILE = sys.argv[1]
    finger = FingerPrinter(FILE)
    music = MusicUtils(API_KEY=API,fingerprint=finger.fingerprint , duration=finger.duration)
    query = music.lookup()
    print ' Artist :{0} \n Album  :{1} \n Song   :{2} \n Date   :{3} \n Duration:{4} \n mbid   :{5}'.format(query.artist,query.album,query.song_title,query.date,query.duration,query.mbid)
