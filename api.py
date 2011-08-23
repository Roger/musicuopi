import re
import urllib

from util import url_open
from memo import Memoized

HOST = "http://www.musicuo.com/"
SEARCH_URL = HOST + "search?&q=%s"
SONG_URL = HOST + 'include/mp3/get'

RE_SONG = re.compile('m.playlist.push\({id: "(?P<id>[0-9]*?)", '\
        'icon: "", titulo: "(?P<title>.*?)", artista: "(?P<artist>.*?)", '\
        'album: "(?P<album>.*?)", genero: "(?P<gener>.*?)"')


class Song(object):
    def __init__(self, song=None, id=None):
        if song:
            for key, value in song.iteritems():
                setattr(self, key, value)
        elif id:
            self.id = id

    @property
    def url(self):
        params = {'file': self.id,
                  'token': get_token()}
        return url_open(SONG_URL, data=params)

    @property
    def data(self):
        fd = url_open(self.url, handle=True)

        data = fd.read(1024*5)
        while True:
            yield data
            data = fd.read(1024)
            if not data:
                break



def get_token():
    # TODO: should implement cookies to disk too
    #try:
    #    with open('.token') as fd:
    #        token = fd.read()
    #except Exception, error:
    #    data = url_open(HOST)
    #    token = data.split('var ptk = "')[1].split('";')[0]
    #    with open('.token', 'w') as fd:
    #        fd.write(token)
    data = url_open(HOST)
    token = data.split('var ptk = "')[1].split('";')[0]
    return token

@Memoized
def search(query):
    query = urllib.quote(query)
    data = url_open(SEARCH_URL % query)
    songs = []
    for song in RE_SONG.finditer(data):
        song_obj = Song(song.groupdict())
        songs.append(song_obj)
        #yield song_obj

    return songs
