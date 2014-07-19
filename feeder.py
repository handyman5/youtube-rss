#!/usr/bin/env python

# import gevent for multi-threaded operation if available
try:
    from gevent import monkey, queue; monkey.patch_all()
    import gevent.wsgi
except:
    gevent = None

from bottle import route, run, static_file, ServerAdapter
from bs4 import BeautifulSoup
import os
import urllib2
import youtube_dl

from config import *
# config should contain:
## MYFEED='http://gdata.youtube.com/feeds/api/playlists/XXX'
## HOSTNAME='0.0.0.0'  (whatever you want the URLs to have to reach this host
## PORT=5001

MEDIA_PATH='media'
FORMAT='3gp'  # also try 'bestaudio' for text-only feeds

@route('/')
@route('/feeds')
def index():
    return "<h2>Feed list</h2><br><ul><li><a href='/feeds/test'>My Feed</a></li></ul>"

@route('/feeds/test')
def test_feed():
    data = urllib2.urlopen(MYFEED).read()
    tree = BeautifulSoup(data, features='xml')

    items = tree.find_all('entry')
    for i in items:
        # find the ID
        video = i.find('link', rel='related')['href'].split('/')[-1]

        # remove extraneous gunk
        [q.decompose() for q in i.group.find_all('content')]

        # add or update the enclosure
        enc = tree.new_tag('link')
        enc['rel'] = 'enclosure'
        enc['type'] = 'audio/mpeg'
        enc['title'] = 'mp3'
        enc['href'] = 'http://%s:%s/media/%s' % (HOSTNAME, PORT, video)
        i.append(enc)

        # add the description
        desc = tree.new_tag('description')
        desc.string = i.description.string
        i.append(desc)

    return tree.prettify()

@route('/media/<video>')
def download_media(video):
    print "attempting to download media for ID %s" % video
    lockfile = MEDIA_PATH + "/lock.%s" % video
    try:
	lh = os.open(lockfile, os.O_CREAT | os.O_EXCL)

        ydl = youtube_dl.YoutubeDL({'outtmpl': MEDIA_PATH + '/%(id)s.%(ext)s', 'format': FORMAT, 'nooverwrites': True})
        ydl.add_default_info_extractors()
        info = ydl.extract_info('https://www.youtube.com/watch?v=%s' % video, download=True)
        os.close(lh)
        os.unlink(lockfile)
        return static_file("%(id)s.%(ext)s" % info, root=os.path.realpath(MEDIA_PATH))

    except OSError:
        return

if __name__ == '__main__':
    if gevent:
        class GeventServer(ServerAdapter):
            """ For asynchronous responses. """
            def run(self, handler):
                from gevent.wsgi import WSGIServer
                app = WSGIServer((self.host, self.port), handler)
                app.serve_forever()

        run(host='0.0.0.0', port=PORT, server=GeventServer)
    else:
        run(host='0.0.0.0', port=PORT)
