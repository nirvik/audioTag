import musicbrainzngs 
import fingerprint 
import sys
import musicbrainz
import operator

if __name__ == '__main__':
    
    FILE = sys.argv[1]
    finger = fingerprint.FingerPrinter(FILE)
    finger.parse_result()
    print finger.scores
    # send the acoustid with the maximum score value
    best_mbids = max(finger.scores.iteritems(), key = operator.itemgetter(1))
    #print finger.mbids[best_mbids[0]]
    print finger.artists[best_mbids[0]]
    musicbrainz.get_recording_by_id(finger.mbids[best_mbids[0]])
    #musicbrainz.get_recording_by_id(finger.mbids.values()[0])
