import musicbrainzngs
from  fingerprint import * 
import sys
import musicbrainz
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
            query = AcoustQuery(finger.fingerprint , finger.duration)
            query.parse_result()
	except : 
	    print ' Invalid Song '
	    continue

    	best_acoustid,score = query.bestacoustid() # get the acoustid that has the maximum score

   	try:
	    mbids,details = musicbrainz.get_recording_by_id(query.recording_ids[best_acoustid])
	except:
            print 'seriously ! this shit happend '
	    continue
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
	    	temp[j['id']] = key

        # Let's say if date is not there 
	try:
    	    coverart_mbid,date = max(mbid_dates.iteritems(),key=operator.itemgetter(1)) # Get the latest cover track 
	except:
	    coverart_mbid = random.choice(temp.keys())
	    date = '2015'
            
    	print 'The cover art mbid is {0}'.format(coverart_mbid)
    	print 'This was released in {0}'.format(date)

        artist = query.artist
	song = query.song_title
	
    	print 'Song : {0}'.format(song)
        print 'Artist: {0}'.format(artist)
	
	key = ''
	for i,j in mbids.iteritems():
    	    for k in j:
	    	if coverart_mbid in j:
	    	    key = i
		    break
    	
	metadata['title'] = unicode(song)
	try:
	    metadata['album'] = unicode(details[key][0]['title'])
	except:
	    metadata['album']= unicode(song)
	metadata['artist'] = unicode(artist)
	metadata['date'] = unicode(date)
	metadata['album-art-mbid'] = unicode(coverart_mbid) 
	try:
	    #tag.tagit(FILE , metadata)
	    tag.trialtag(FILE , metadata)
	except:
	    pass
