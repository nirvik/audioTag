import acoustid 
import musicbrainzngs 
import subprocess 
import sys

class FingerPrinter(object):

    def __init__(self,FILE):
        self.fingerprint = None
        self.duration = None
        fpprocess = subprocess.Popen(['fpcalc',FILE],stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        answer , error  = fpprocess.communicate()
        length , score = answer.split('\n')[1] , answer.split('\n')[-2]
        self.fingerprint,self.duration = score[score.find('=')+1:],length[length.find('=')+1:]
    

if __name__ == '__main__':    
    FILE  = sys.argv[1]
    finger = FingerPrinter(FILE)
    json_acoustid_result  =  acoustid.lookup('S0xa1BKE',finger.fingerprint,finger.duration)
    for i in json_acoustid_result['results']:
    	print i.keys()

'''
Get the fingerprint 
Use the acoustid web service to get enter the fingerprint 
The webservice will query the fingerprint in the musicbrainz database 
'''
