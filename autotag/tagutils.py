from mutagen.mp3 import MP3
from mutagen.id3 import ID3,APIC,error,TIT2,TPE1,TALB
import requests
import json
from BeautifulSoup import BeautifulSoup
import urllib

class AlbumArtException(Exception):
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return '[Error {0}]=> {1}'.format(self.code , self.msg)

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
        except:
            location , header = '' , {'content-type':'failed','content-length':0}
            return (location , header )
    try:
        location , header = urllib.urlretrieve(pic,'example.jpeg')
    except :
        print 'There is no album art for this file '
        location = ''
        header = {'content-type':'failed','content-length':0}
    print ' Image located in {0} and downloaded {1} '.format(location,header['content-length'])
    if header['content-type'] == 'image/jpg':
        header['content-type'] = 'image/jpeg'
    if header['content-type'] != 'failed':
        return (location , header)
    else :
        raise AlbumArtException('1','Image not found')


def trialtag(FILE , metadata):
    location,header = album_art(metadata['cover-art-url'])
    audio=MP3(FILE,ID3=ID3)
    audio.delete()
    audio.tags.add(TIT2(encoding=3, text=metadata['title']))
    audio.tags.add(TPE1(encoding=3 , text = metadata['artist']))
    audio.tags.add(TALB(encoding=3 , text = metadata['album']))
    audio.tags.add(APIC(encoding=3, mime=header['content-type'], type=3,desc=u'Used by Auto tagger', data=open(location).read()))
    audio.save()



