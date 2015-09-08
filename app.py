#!/usr/bin/env python

import os
import logging

import bottle

view = bottle.jinja2_view

logger = logging.getLogger(__name__)

PATH = './'
bottle.TEMPLATE_PATH.insert(0, os.path.join(PATH, 'views'))

class LabelPi(bottle.Bottle):

    TMP_FILE = '/tmp/labelpi-tmpfile'
    MAX_FILESIZE = 10 * 1024**2

    def __init__(self):
        """
        The LabelPi web server
        """
        super(LabelPi, self).__init__()
        self.route('/',                       callback=self._index)
        self.post('/upload',                  callback=self._upload)
        self.route('/static/<filename:path>', callback = self._serve_static)

    @view('dragdrop.jinja2')
    def _index(self):
        return {}

    def _upload(self):
        bufsize = 1024
        actread, maxread = 0, max(0, bottle.request.content_length)
        if maxread > self.MAX_FILESIZE: bottle.abort(500, 'file bigger than MAX_FILESIZE')
        with open(self.TMP_FILE, 'wb') as tmp_file:
            while actread < maxread:
                part = bottle.request.environ['wsgi.input'].read(min(maxread - actread, bufsize))
                if not part: break
                actread += len(part)
                tmp_file.write(part)
        if actread == 0: bottle.abort(500, 'expecting a file payload')
        return {'total_length': actread}

    def _serve_static(self, filename):
        return bottle.static_file(filename, root=os.path.join(PATH, 'static'))

