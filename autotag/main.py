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
    result = musicbrainz.get_recording_by_id(finger.mbids[best_mbids[0]])
    print len(result)
    for elements in result:
        #print elements['recording']['release-list']
        for (idx, release) in enumerate(elements['recording']['release-list']):
            print("match #{}:".format(idx+1))
            musicbrainz.show_release_details(release)
            print()
    
    #musicbrainz.get_recording_by_id(finger.mbids.values()[0])
