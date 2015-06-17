import musicbrainzngs
import fingerprint

musicbrainzngs.auth('','')  # username  , password
musicbrainzngs.set_useragent('Auto Tagger', '0.1', 'nirvik1993@gmail.com')
release_id = 'e387ac45-4be6-4b4f-a957-ed0fe0afa3ca'

def get_recording_by_id(release_id):
    result = [] 
    for ids in release_id:
	print ids
	try:
            result.append(musicbrainzngs.get_recording_by_id(ids))
    	except musicbrainzngs.WebServiceError as exc:
            print("Something went wrong with the request: %s" % exc)
	    raise fingerprint.FingerPrinterException('Something wrong with the request. ',2)
    print result
    return result 



