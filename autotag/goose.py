import sys
from fingerprint import FingerPrinter,FingerPrinterException
from musicbrainz import MusicUtils
from tagutils import tag
import os
import time
from  multiprocessing import Pool
import logging
import argparse

API = os.environ.get('ACOUSTID_API_KEY')

def parse_date(date):
    return str(date.year)

def goose((FILE)):
        finger = FingerPrinter(FILE)
        music = MusicUtils(API_KEY=API,fingerprint=finger.fingerprint , duration=finger.duration)
        try:
            query = music.lookup()
            metadata = {}
            metadata['title'] = unicode(query.song_title)
            metadata['artist'] = unicode(query.artist)
            metadata['date'] = unicode(parse_date(query.date))
            metadata['album-art-mbid'] = unicode(query.mbid)
            metadata['album'] = query.album
            metadata['duration'] = query.duration
            metadata['cover-art-url'] = query.cover_art_url
            tag(FILE,metadata)
            print 'Goose tagged => {0} , Artist:{1} , Album :{2}'.format(query.song_title,query.artist,query.album)
        except Exception as e:
            print 'Goose flummoxed  => {0} '.format(FILE)
            print 'Reason => {0}'.format(e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory",help="Enter the directory which contains the music files")
    parser.add_argument("--song" , help="Enter the song path you wish to autotag ")
    args = parser.parse_args()
    if args.directory:
        pool = Pool(processes=4)
        base = args.directory
        FILES = map(lambda x: base+x,os.listdir(base))#sys.argv[1:]
        start = time.time()
        print '**** Starting Main Thread *****'
        pool.map(goose,FILES)
        print '****** Done *******'
        end =time.time()
        print end - start

    elif args.song:
        print '****** Starting *********'
        goose(args.song)
        print '****** Done **********'


if __name__ == '__main__':
    main()
