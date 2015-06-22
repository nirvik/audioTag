from mutagen.id3 import ID3NoHeaderError,ID3,APIC,error 
from mutagen.easyid3 import EasyID3
from BeautifulSoup import BeautifulSoup
import urllib
from mutagen.mp3 import MP3
from mutagen import File

def get_album_art(mbid):
    cover_art_html = urllib.urlopen('https://musicbrainz.org/release/'+mbid).read()
    cover_art_soup = BeautifulSoup(cover_art_html)
    try:
    	picture = cover_art_soup.find('img')['src'].replace('//','http://www.')
    	location , header = urllib.urlretrieve(picture,"filename.jpeg")
    except:
	try:
            picture = cover_art_soup.find('img')['src']
            location , header = urllib.urlretrieve(picture,"filename.jpeg")
	except :
	    print 'There is no album art for this file '
	    location = ''
	    header = {'content-type':'failed','content-length':0}
        
    print ' Image located in {0} and downloaded {1} '.format(location,header['content-length'])
    return (location , header) 



def tagit(FILE,metadata):    
    audio = MP3(FILE)
    try:
	audio.delete()
        audio.add_tags()
    except :
	print 'Too bad nothing will happen'
        try:
            audio = MP3(FILE)
	    audio.delete()
	    audio.add_tags()
	    print 'finally yeah '
	except:
	    print 'Now definitely it wont happen'
	    pass
    location,header = get_album_art(metadata['album-art-mbid'])
    if header['content-type'] ==  'image/jpg':
	header['content-type'] = 'image/jpeg'
    if header['content-type'] != 'failed':
        audio.tags.add(
            APIC(
                encoding = 3,
                mime =header['content-type'],
                type = 3 ,
                desc = u'Used by AutoTagger',
                data = open(location).read()
                )
        )
        audio.save()
	print 'Image added'
    try:
        audiofile = EasyID3(FILE)
    except ID3NoHeaderError:
        audiofile = File(FILE,easy = True)
        audiofile.add_tags()

    audiofile['artist'] = metadata['artist']
    audiofile['album'] = metadata['album']
    audiofile['title'] = metadata['title'] 
    audiofile['originaldate']  = metadata['date']
    audiofile.save()
