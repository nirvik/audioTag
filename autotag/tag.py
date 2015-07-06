from mutagen.id3 import ID3NoHeaderError,ID3,error,TIT2,TPE1,TALB,APIC,TPE2,TDRC 
from BeautifulSoup import BeautifulSoup
import urllib
import json 
import requests

def get_album_art(mbid):
 
    url = 'http://coverartarchive.org/release/' + mbid 
    cover_art_json = requests.get(url).text 
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
    return (location , header) 

def trialtag(FILE , metadata ): 
    tags = ID3()
    tags['TIT2']  = TIT2(encoding = 3 ,text = metadata['title']) #title  
    tags['TPE1'] = TPE1(encoding = 3 , text = metadata['artist']) #artist 
    tags['TALB'] = TALB(encoding = 3 , text = metadata['album']) #album
    #tags['TDRC'] = TDRC(encoding = 3 , text = metadata['date'])
    
    location,header = get_album_art(metadata['album-art-mbid'])
    if header['content-type'] ==  'image/jpg':
	header['content-type'] = 'image/jpeg'
    if header['content-type'] != 'failed':
        tags['APIC'] = APIC(
            encoding = 3 ,
            mime = header['content-type'],
            type = 3,
            desc=u'Used By AutoTagger',
            data = open(location).read()
        )#picture
    tags.save(FILE)
    
