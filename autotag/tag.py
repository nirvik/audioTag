from musicbrainz import MusicUtils
from mutagen.mp3 import MP3
from mutagen.id3 import ID3,APIC,error,TIT2,TPE1,TALB

def trialtag(FILE , metadata ):

    location,header = MusicUtils.album_art(metadata['album-art-mbid'])
    print 'Location {0}'.format(location)
    audio=MP3(FILE,ID3=ID3)
    audio.delete()
    audio.tags.add(TIT2(encoding=3, text=metadata['title']))
    audio.tags.add(TPE1(encoding=3 , text = metadata['artist']))
    audio.tags.add(TALB(encoding=3 , text = metadata['album']))
    audio.tags.add(APIC(encoding=3, mime=header['content-type'], type=3,desc=u'Used by Auto tagger', data=open(location).read()))
    audio.save()
