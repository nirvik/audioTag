import acoustid 
import musicbrainzngs 
import subprocess 
import sys
import json

class FingerPrinterException(Exception):
    def __init__(self,mesg,error_code ):
    	self.mesg = mesg
	self.code = error_code 

    def __str__(self):
    	return self.code + ':' + self.message 

class FingerPrinter(object):

    def __init__(self,FILE):
        self.fingerprint = None
        self.duration = None
	try:
            fpprocess = subprocess.Popen(['fpcalc',FILE],stdout=subprocess.PIPE, stderr = subprocess.PIPE)
	except:
	    raise FingerPrinterException('Chromaprint not found',1)
	
        answer , error  = fpprocess.communicate()
	if error != '':
	    raise FingerPrinterException('Invalid song/file',2)
        length , score = answer.split('\n')[1] , answer.split('\n')[-2]
        self.fingerprint,self.duration = score[score.find('=')+1:],length[length.find('=')+1:]

class ParserResult(object):

    def __init__(self,json_file):
        self.mbids = {}
        self.acoustids = []
        self.score =  {}

        for result in json_file['results']:
            self.acoustids.append(result['id'])
            self.score[result['id']] = result['score']
            if 'recordings' in result:
                mbids = []
                for recording in result['recordings']:
                    mbids.append(recording['id'])
                self.mbids[result['id']] = mbids
        
    def __repr__(self):
        print ' ParsedResult of the acoustid file'


if __name__ == '__main__':    
    FILE  = sys.argv[1]
    finger = FingerPrinter(FILE)
    json_acoustid_result  =  acoustid.lookup('S0xa1BKE',finger.fingerprint,finger.duration)
    #Parsing
    #Collect all the acoustids and the respective scores ... collect all the recording mbids

    parsed_output = ParserResult(json_acoustid_result)
    print parsed_output.mbids,parsed_output.score,parsed_output.acoustids
    
'''
Get the fingerprint 
Use the acoustid web service to get enter the fingerprint 
The webservice will query the fingerprint in the musicbrainz database 
'''
