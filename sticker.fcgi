#!/usr/bin/env python3

from flup.server.fcgi import WSGIServer
from server import app

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/tmp/sticker-fcgi.sock', umask=0o000).run()
