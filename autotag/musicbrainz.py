import musicbrainzngs
import fingerprint

musicbrainzngs.auth('','')  # username  , password
musicbrainzngs.set_useragent('Auto Tagger', '0.1', 'nirvik1993@gmail.com')


def show_release_details(rel):
    """Print some details about a release dictionary to stdout.
    """
    # "artist-credit-phrase" is a flat string of the credited artists
    # joined with " + " or whatever is given by the server.
    # You can also work with the "artist-credit" list manually.
    try:
        print("{}".format(str(rel['title'])))
    except:
        pass
    if 'date' in rel:
	try:
            print("Released {} ({})".format(rel['date'], rel['status']))
        except:
	    pass
	print("MusicBrainz ID: {}".format(rel['id']))


def get_recording_by_id(release_id):
    
    # We need to store more information . As of now , storing only release id to get the album art in future 
    mbids = {} 
    song_details = {} 
    for ids in release_id:
        temp_mbids = [] 
        try:
	    records = musicbrainzngs.get_recording_by_id(ids,includes=['releases'])['recording']
	    for i in records['release-list']:
		try:
                    if i['status'] == 'Official':
                        temp_mbids.append(i['id'])
                    mbids[ids] = temp_mbids
		except:
		    pass
  	    song_details[ids] = records['release-list']
    	except musicbrainzngs.WebServiceError as exc:
            print("Something went wrong with the request: %s" % exc)
	    raise fingerprint.FingerPrinterException('Something wrong with the request. ',2)
    #print song_details
    return (mbids,song_details) 

def get_album_art(release_id):
    result = get_recording_by_id(release_id)
