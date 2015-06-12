import acoustid 
import musicbrainzngs 
import subprocess as sbp
import sys

FILE  = sys.argv[1] 
p = sbp.Popen(['fpcalc',FILE],stdout=sbp.PIPE, stderr=sbp.PIPE)
output,err = p.communicate()
print output
#Get the fingerprint 
#Use the acoustid web service to get enter the fingerprint 
#The webservice will query the fingerprint in the musicbrainz database 
#acoustid.lookup('S0xa1BKE',fingerprint,duration)
