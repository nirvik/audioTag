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
    # send the acoustid with the maximum score value
    best_mbids = max(finger.scores.iteritems(), key = operator.itemgetter(1))
    print finger.artists[best_mbids[0]]
    result = musicbrainz.get_recording_by_id(finger.mbids[best_mbids[0]])
    print result
    #print len(result)
    mbid_rec = result[1] 
    mbid_dates = {} 
    temp = {} 
    for i,k in result[1].iteritems():
        for j in k:
	    print j['id'] , j['date']
	    mbid_dates[j['id']] = datetime.strptime(j['date'],'%Y-%M-%d')
	    temp[j['id']] = i
    coverart_mbid = max(mbid_dates.iteritems(),key=operator.itemgetter(1))
    print 'The cover art mbid is {0}'.format(coverart_mbid[0])
    print 'The details of the songs are follows {0}'.format(mbid_rec[temp[coverart_mbid[0]]])

    
    '''
    '''
    #musicbrainz.get_recording_by_id(finger.mbids.values()[0])
