import musicbrainzngs 
import fingerprint 
import sys
import musicbrainz
import operator
from datetime import datetime
if __name__ == '__main__':
    
    FILE = sys.argv[1]
    finger = fingerprint.FingerPrinter(FILE)
    finger.parse_result()
    print finger.scores
    best_mbids = max(finger.scores.iteritems(), key = operator.itemgetter(1))
    result = musicbrainz.get_recording_by_id(finger.mbids[best_mbids[0]])
    mbid_rec = result[1] 
    print result[1]
    mbid_dates = {} 
    temp = {} 
    for i,k in result[1].iteritems():
        for j in k:
#	    print j['id'] , j['date']
	    #print j
	    try:
	        mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M-%d')
	    except:
		pass
	    temp[j['id']] = i
    coverart_mbid = max(mbid_dates.iteritems(),key=operator.itemgetter(1))
    print 'The cover art mbid is {0}'.format(coverart_mbid[0])
    #print 'The details of the songs are follows {0}'.format(mbid_rec[temp[coverart_mbid[0]]])
	
    for artist in finger.artists[best_mbids[0]]:
	print 'Artist: {0}'.format(artist)
    
    key = ''
    for i,j in result[0].iteritems():
    	for k in j:
	    if coverart_mbid[0] in j:
	    	key = i
		break
    #print key
    print 'Title {0}'.format(result[1][key][0]['title'])
