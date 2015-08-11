import subprocess
import sys

class FingerPrinterException(Exception):

    def __init__(self, mesg, error_code):
        self.mesg = mesg
        self.code = error_code

    def __str__(self):
        return '[Error {0}] => {1}'.format(self.code , self.mesg)

class FingerPrinter(object):

    '''
    Get the fingerprint
    Uses the acoustid web service to get enter the fingerprint
    The webservice will query the fingerprint in the musicbrainz database
    '''
    __version__ = '0.0.1'
    __doc__ = ' Fingerprinting the audio file '

    def __init__(self, file_name):
        self._fingerprint = None
        self._duration = None
        try:
            fpprocess = subprocess.Popen(
                ['fpcalc', file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            raise FingerPrinterException('Chromaprint not found , kindly install fpcalc for your system..', 1)

        answer, error = fpprocess.communicate()
        if answer == '':
            raise FingerPrinterException('Invalid File','4')
        self._fingerprint , self._duration = self.fingerprintoutput(answer)

    @staticmethod
    def fingerprintoutput(answer):
        length, score = answer.split('\n')[1], answer.split('\n')[-2]
        fingerprint_value, duration = score[
            score.find('=') + 1:], length[length.find('=') + 1:]
        return (fingerprint_value , duration)

    @property
    def fingerprint(self):
        return self._fingerprint

    @fingerprint.setter
    def fingerprint(self,val):
        if val is None or len(val)==0:
            raise FingerPrinterException('Invalid FingerPrint',2)
        self._fingerprint = val

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self,val):
        if val is None or len(val)==0:
            raise FingerPrinterException('Invalid Duration' , 3 )
        self._duration = val

