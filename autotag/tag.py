from mutagen.id3 import ID3NoHeaderError,ID3,error,TIT2,TPE1,TALB,APIC,TPE2,TDRC
from BeautifulSoup import BeautifulSoup
import urllib
import json
import requests
from musicbrainz import MusicUtils

def trialtag(FILE , metadata ):
    tags = ID3(FILE)
    tags['TIT2']  = TIT2(encoding = 3 ,text = metadata['title']) #title
    tags['TPE1'] = TPE1(encoding = 3 , text = metadata['artist']) #artist
    tags['TALB'] = TALB(encoding = 3 , text = metadata['album']) #album
    tags['TDRC'] = TDRC(encoding = 3 , text = metadata['date'])
    location,header = MusicUtils.album_art(metadata['album-art-mbid'])
    tags['APIC'] = APIC(
        encoding = 3 ,
        mime = header['content-type'],
        type = 3,
        desc=u'Used By AutoTagger',
        data = open(location).read()
    )#picture
    tags.save()
