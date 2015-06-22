from mutagen.id3 import ID3NoHeaderError,ID3,APIC,error 
from mutagen.easyid3 import EasyID3
from BeautifulSoup import BeautifulSoup
import urllib
from mutagen.mp3 import MP3

def get_album_art(mbid):
    cover_art_html = urllib.urlopen('https://musicbrainz.org/release/'+mbid).read()
    cover_art_soup = BeautifulSoup(cover_art_html)
    picture = cover_art_soup.find('img')['src'].replace('//','http://www.')
    location , header = urllib.urlretrieve(picture)
    return (location , header) 
    

def tagit(FILE,metadata):
    try:
        audiofile = EasyID3(FILE)
    except ID3NoHeaderError:
        audiofile = mutagen.File(FILE,easy = True)
        audiofile.add_tags()
    
    audiofile['artist'] = metadata['artist']
    audiofile['album'] = metadata['album']
    audiofile['title'] = metadata['title'] 
    audiofile['originaldate']  = metadata['date']
    audiofile.save()
    audio = MP3(FILE,ID3 = ID3)
    location,header = get_album_art(metadata['album-art-mbid'])
    audio.tags.add(
        APIC(
            encoding = 3,
            mime = header['content-type'],
            type = 3 ,
            desc = u'Used by AutoTagger',
            data = open(location).read()
            )
    )
    audio.save()
    #imagedata = open(albumart,'rb').read()
    #audiofile.tag.images.set(3,imagedata,"image/jpeg","Tagged with autotagger")
    #audiofile.tag.save()
