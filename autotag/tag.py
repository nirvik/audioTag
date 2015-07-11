from mutagen.mp3 import MP3
from mutagen.id3 import ID3,APIC,error,TIT2,TPE1,TALB
#from musicbrainz import MusicUtilsException
import requests
import json
from BeautifulSoup import BeautifulSoup
import urllib

def album_art(url):
    '''
        Takes MBID as the argument and downloads the image for the music
    '''
    cover_art_json = requests.get(url).text
    try:
        response = json.loads(cover_art_json)
        pic = response['images'][0]['image']
    except:
        try:
            cover_art_response = requests.get(MusicUtils.musicbrainz_image_url.format(art_mbid)).text
            soup=BeautifulSoup(cover_art_response)
            pic = soup.find('div',{'class':'cover-art'}).find('img')['src'] #From amazon
            print pic
        except:
            location , header = '' , {'content-type':'failed','content-length':0}
            print '3'
            return (location , header )
    try:
        location , header = urllib.urlretrieve(pic,"filename.jpeg")
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
        pass
        #raise MusicUtilsException('1','Image not found')


def trialtag(FILE , metadata):
    location,header = album_art(metadata['cover-art-url'])
    audio=MP3(FILE,ID3=ID3)
    print audio
    audio.delete()
    audio.tags.add(TIT2(encoding=3, text=metadata['title']))
    audio.tags.add(TPE1(encoding=3 , text = metadata['artist']))
    audio.tags.add(TALB(encoding=3 , text = metadata['album']))
    audio.tags.add(APIC(encoding=3, mime=header['content-type'], type=3,desc=u'Used by Auto tagger', data=open(location).read()))
    audio.save()


def parse_result(json_file):
    '''
    Parses the response
    Aggregates the necessary scores , recording ids , mbids , artist and song title
    '''
    temp_song  = {}
    temp_artist = {}
    scores = {}
    recording_ids = {}
    if json_file['status'] != u'ok' or len(json_file['results'])==0:
        raise MusicUtilsException('2','Bad look up, ended with a bad status report')
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
        recording_ids[result['id']] = rids
    return (scores , recording_ids , temp_song , temp_artist)

