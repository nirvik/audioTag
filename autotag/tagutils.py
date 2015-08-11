from mutagen.mp3 import MP3
from mutagen.id3 import ID3,APIC,error,TIT2,TPE1,TALB,TDRC
import requests
import json
from BeautifulSoup import BeautifulSoup
import urllib
import os
import re

image_extension_regex = re.compile(r'\d+\.(\w+)')
file_format_regex = re.compile(r'\.(\S+)')

class AlbumArtException(Exception):
    def __init__(self,code,msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return '[Error {0}]=> {1}'.format(self.code , self.msg)

def album_art(url,art_mbid,title):
    '''
        Takes MBID as the argument and downloads the image for the music
    '''
    cover_art_json = requests.get(url).text
    try:
        response = json.loads(cover_art_json)
        pic = response['images'][0]['image']
    except:
        try:
            url = 'https://musicbrainz.org/release/{0}/cover-art'
            cover_art_response = requests.get(url.format(art_mbid)).text
            soup=BeautifulSoup(cover_art_response)
            pic = soup.find('div',{'class':'cover-art'}).find('img')['src'] #From amazon
        except:
            location , header = '' , {'content-type':'failed','content-length':0}
            return (location , header )
    try:
        if not os.path.exists('_album_art'):
            os.makedirs('_album_art')
        image_extension = image_extension_regex.search(pic)
        location , header = urllib.urlretrieve(pic,os.path.abspath('_album_art')+'/{0}'.format(title))
    except :
        print 'There is no album art for this file '
        location = ''
        header = {'content-type':'failed','content-length':0}
    if header['content-type'] == 'image/jpg':
        header['content-type'] = 'image/jpeg'
    if header['content-type'] != 'failed':
        return (location , header)
    else :
        raise AlbumArtException('1','Image not found')


def tag(FILE , metadata):
    location,header = album_art(metadata['cover-art-url'],metadata['album-art-mbid'],metadata['title'])
    try:
        audio = ID3(FILE)
        audio.delete()
    except:
        audio = ID3()
    audio['TIT2']=TIT2(encoding=3, text=metadata['title'])
    audio['TPE1']=TPE1(encoding=3 , text = metadata['artist'])
    audio['TALB']=TALB(encoding=3 , text = metadata['album'])
    audio['APIC']=APIC(encoding=3, mime=header['content-type'], type=3,desc=u'Used by Auto tagger', data=open(location).read())
    audio['TDRC'] = TDRC(encoding=3,text=metadata['date'])
    audio.save(FILE)
    #For renaming file and removing the file
    path , filename = os.path.split(FILE)
    os.rename(FILE,path+'/'+metadata['title']+'.'+file_format_regex.search(filename).group(1))
    os.remove(os.path.abspath('_album_art')+'/'+metadata['title'])

