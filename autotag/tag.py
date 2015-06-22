from mutagen.id3 import ID3NoHeaderError
from mutagen.easyid3 import EasyID3

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
    #imagedata = open(albumart,'rb').read()
    #audiofile.tag.images.set(3,imagedata,"image/jpeg","Tagged with autotagger")
    #audiofile.tag.save()
