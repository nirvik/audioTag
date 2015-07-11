import acoustid
import musicbrainzngs
from  fingerprint import FingerPrinter
import datetime
import random
import operator
import requests
import urllib
import json
from BeautifulSoup import BeautifulSoup
from tag import *


class MusicUtilsException(Exception):
    def __init__(self,code,msg):
        self.msg = msg
        self.code = code

    def __str__(self):
        return '[Error :{0}] => {1}'.format(self.code , self.msg)

class MusicUtils(object):

    __doc__ = 'A bunch of utilities provided to extract information from the musicbrainzngs'
    __version__ = '0.0.1'
    base_image_url = 'http://coverartarchive.org/release/'
    musicbrainz_image_url = 'https://musicbrainz.org/release/{0}/cover-art'
    API_KEY = 'S0xa1BKE'
    musicbrainzngs.auth('','')  # username  , password
    musicbrainzngs.set_useragent('Auto Tagger', '0.1', 'nirvik1993@gmail.com')

    def __init__(self , fingerprint = None ,
            duration = None,
            mbid = None,
            mbid_dates = None,
            song_details = None,
            backup_date= None,
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

        self._mbid = mbid # The MBID
        self._mbid_dates = mbid_dates # mbid to release dates
        self._mbids = mbids # Recording id to release id's
        self._song_details = song_details # Bunch of details about the music that we can use in the future
        self._backup_date = {}
        self._fingerprint = fingerprint
        self.duration = duration
        self.song_title = song_title
        self.artist = artist
        self.album = album
        self.date = date
        # We dont want this to have public access
        self._scores = scores
        self._recording_ids = recording_ids
        self._best_acoustid = best_acoust_id
        self._best_score = best_score
        self.cover_art_url = cover_art_url

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

    def _extractdates(self,details):
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


    def _latestmbid(self,details):
        '''
        Gets the information about the latest track of the song and returns the song's mbid
        '''
        self._extractdates(details)
        try:
            mbid , date =  max(self._mbid_dates.iteritems(),key = operator.itemgetter(1))
        except:
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
    def recording_details(recording_ids):
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
                raise FingerPrinterException('Something wrong with the request. ',3)
        return (mbids,song_details)


    @staticmethod
    def bestacoustid(scores):
        return max(scores.iteritems(),key=operator.itemgetter(1))

    def lookup(self):
        json_file = acoustid.lookup(MusicUtils.API_KEY , self._fingerprint , self.duration)
        self._scores , self._recording_ids , temp_song, temp_artist =  parse_result(json_file)
        self.song_title , self.artist =  max(temp_song.iteritems(), key = operator.itemgetter(1))[0].encode('utf-8') , max(temp_artist.iteritems(), key = operator.itemgetter(1))[0].encode('utf-8')
        self._best_acoust ,self._best_score = self.bestacoustid(self._scores)
        self._mbids,self._song_details = self.recording_details(self._recording_ids[self._best_acoust])
        self._mbid ,self.date = self._latestmbid(self._song_details)
        self.album = self._extract_album_name(self._mbid)
        return MusicUtils(scores = self._scores,
                recording_ids = self._recording_ids,
                song_title = self.song_title,
                artist = self.artist ,
                best_acoust_id = self._best_acoustid,
                best_score = self._best_score,
                mbids = self._mbids,
                song_details= self._song_details,
                mbid= self._mbid,
                date= self.date,
                album=self.album,
                backup_date = self._backup_date,
                fingerprint = self._fingerprint,
                duration = self.duration,
                cover_art_url = MusicUtils.base_image_url + self._mbid
                )

if __name__ == '__main__':
    import sys
    from tag import *
    FILE = sys.argv[1]
    finger = FingerPrinter(FILE)
    music = MusicUtils.feedfingerprint(finger.fingerprint , finger.duration)
    query = music.lookup()
    metadata = {}
    metadata['title'] = unicode(query.song_title)
    metadata['artist'] = unicode(query.artist)
    metadata['date'] = unicode(query.date)
    metadata['album-art-mbid'] = unicode(query.mbid)
    metadata['album'] = query.album
    metadata['duration'] = query.duration
    metadata['cover-art-url'] = query.cover_art_url
    print ' Artist :{0} \n Album  :{1} \n Song   :{2} \n Date   :{3} \n Duration:{4} \n mbid   :{5}'.format(query.artist,query.album,query.song_title,query.date,query.duration,query.mbid)
    trialtag(FILE,metadata)
