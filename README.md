#`Auto Tagger`

**Command Line Python application to autotag your audio files**


Register for acoustid web api key
Install chromaprint 

#Setting up 
**Acoustid Web API key**
`$ export ACOUSTID_API_KEY='<your_API_key>'`

```python
python goose.py --song /home/name/Music/something.mp3
python goose.py --directory /home/name/Music/
```

#Example of the API lookup
```python 
from musicbrainz import *
finger = FingerPrinter(FILE)
music = MusicUtils(API_KEY=API,fingerprint=finger.fingerprint , duration=finger.duration)
query = music.lookup()
```
