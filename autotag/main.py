#import musicbrainzngs
from  fingerprint import *
import sys
from  musicbrainz import MusicUtils
import operator
from datetime import datetime
import tag
import random
import os

if __name__=='__main__':
    FILES=sys.argv[1:]
    #base = '/home/nirvik/Music/'
    #FILES = map(lambda x: base + str(x) , os.listdir(base))
    for FILE in FILES:
	print 'Trying out {0}'.format(FILE)
	metadata = {}
    try:
        finger = FingerPrinter(FILE)
        query = MusicUtils.feedfingerprint(finger.fingerprint,finger.duration)
        query.parse_result()
	except :
        print ' Invalid Song '
        continue
        best_acoustid,score = query.bestacoustid() # gets the acoustid that has the maximum score
    try:
        mbids,details = query.recording_details(query.recording_ids[best_acoustid])
	except:
        print 'Something unusual happened ...'
        continue

	coverart_mbid , date = query.latestmbid(details)
	artist = query.artist
	song = query.song_title
	duration = query.duration
	album_name = query.extract_album_name(coverart_mbid)

	metadata['title'] = unicode(song)
	metadata['artist'] = unicode(artist)
	metadata['date'] = unicode(date)
	metadata['album-art-mbid'] = unicode(coverart_mbid)
	metadata['album'] = album_name
	metadata['duration'] = duration
	print metadata
