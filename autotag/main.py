import musicbrainzngs 
import fingerprint 
import sys
import musicbrainz
import operator
from datetime import datetime
import tag
if __name__ == '__main__':
    
    FILES = sys.argv[1:]
    for FILE in FILES:
	metadata = {} 
    	finger = fingerprint.FingerPrinter(FILE)
    	finger.parse_result()
    	print finger.scores
    	best_acoustid,score = max(finger.scores.iteritems(), key = operator.itemgetter(1)) # get the acoustid that has the maximum score 
   	mbids,details = musicbrainz.get_recording_by_id(finger.recording_ids[best_acoustid])
    	mbid_rec = details
    	mbid_dates = {} 
    	temp = {} 
    	for key,value in details.iteritems():
            for j in value:
	    	try:
	            mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M-%d')
	    	except:
		    try:
		    	mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M')
		    except:
			try:
		    	    mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y')
			except:
			    pass	
		pass
	    	temp[j['id']] = key
    	coverart_mbid,date = max(mbid_dates.iteritems(),key=operator.itemgetter(1))
    	print 'The cover art mbid is {0}'.format(coverart_mbid)
    	print 'This was released in {0}'.format(date)
	artist = ','.join(finger.artists[best_acoustid])
	print 'Artist: {0}'.format(artist)
	song = '' 
    	for song_name in finger.song[best_acoustid]:
	    print 'Song: {0}'.format(song_name.encode('utf-8'))
	    try:
	        song = song + song_name.encode('utf-8') + ' '
    	    except:
		pass
	# Get the best cover art 
    	key = ''
	for i,j in mbids.iteritems():
    	    for k in j:
	    	if coverart_mbid in j:
	    	    key = i
		    break
    	print 'Album :{0}'.format(details[key][0]['title'])
	metadata['title'] = unicode(song)
	metadata['album'] = unicode(details[key][0]['title'])
	metadata['artist'] = unicode(artist)
	metadata['date'] = unicode(date)
	#tag.tagit(FILE , metadata)
