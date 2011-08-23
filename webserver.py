import urllib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import api

HOST = "localhost"
PORT = 4242
URL = "http://%s:%s/" %(HOST, PORT)


def sanitize(song):
    artist = song.artist.replace(' ', '_')
    title = song.title.replace(' ', '_')
    name = '%s/%s' % (urllib.quote(artist),  urllib.quote(title))
    return '%s%s/%s.mp3' % (URL, name, song.id)

class Musicuo(BaseHTTPRequestHandler):
    def do_GET(self):
        ext = self.path[-3:]
        if ext == "pls":
            query = self.path[:-4].split('/')[1]

            self.send_response(200)
            self.send_header('Content-Type', 'audio/x-scpls')
            self.end_headers()

            self.wfile.write("[playlist]\n\n")
            for i, song in enumerate(api.search(query.replace('+', ' ')), 1):
                self.wfile.write("File%s=%s\n" % (i, sanitize(song)))
                self.wfile.write("Title%s=%s\n" % (i, 
                    song.artist + " - " +  song.title))
                self.wfile.write("Lenght%s=-1\n\n" % i)
            self.wfile.write("NumberOfEntries=%s\n" % (i+1))
            self.wfile.write("Version=2")

        elif ext == 'mp3':
            id = self.path[:-4].rsplit('/', 1)[1]
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.end_headers()

            song = api.Song(id=id)

            for data in song.data:
                self.wfile.write(data)
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)


def main():
    try:
        server = HTTPServer(('', PORT), Musicuo)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
