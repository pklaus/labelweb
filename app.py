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
        total_len = 0
        with open(self.TMP_FILE, 'wb') as tmp_file:
            data = bottle.request.body.read()
            if data == b'': bottle.abort(500, 'expected a file payload')
            total_len += len(data)
            if total_len > self.MAX_FILESIZE: bottle.abort(500, 'MAX_FILESIZE reached')
            tmp_file.write(data)
        return {'total_len': total_len}

    def _serve_static(self, filename):
        return bottle.static_file(filename, root=os.path.join(PATH, 'static'))

