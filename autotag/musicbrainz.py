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
    result = [] 
    for ids in release_id:
	print ids
	try:
            result.append(musicbrainzngs.get_recording_by_id(ids,includes=["releases"]))
    	except musicbrainzngs.WebServiceError as exc:
            print("Something went wrong with the request: %s" % exc)
	    raise fingerprint.FingerPrinterException('Something wrong with the request. ',2)

    return result 



