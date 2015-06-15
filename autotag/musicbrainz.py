import musicbrainzngs
musicbrainzngs.auth('', '')  # username  , password
musicbrainzngs.set_useragent('Auto Tagger', '0.1', 'nirvik1993@gmail.com')
release_id = 'e387ac45-4be6-4b4f-a957-ed0fe0afa3ca'
try:
    result = musicbrainzngs.get_recording_by_id(release_id)
    print result
except WebServiceError as exc:
    print("Something went wrong with the request: %s" % exc)
