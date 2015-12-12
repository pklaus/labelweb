#!/usr/bin/env python

"""
Amazon DHL Label Converter -

Convert Amazon DHL shipping labels to a size
suitable for Dymo or Brother label printers.
The label can be printed with 100% scaling
on a page size of 62 mm x 152 mm (of endless
62mm label rolls by Brother for example).

This software requires ImageMagick and pdfimages
to be installed and available in your PATH.
"""

import subprocess, re, os, logging

from helpers import cmd_line_to_args

logger = logging.getLogger(name=__name__)

def convert(filename):
    cmds = []
    input_file = filename
    if filename.endswith('.pdf'):
        cmds += ['pdfimages -all "{pdf_file}" /tmp/pdfimages']
        input_file = '/tmp/pdfimages-000.png'
    elif filename.endswith('.gif') or filename.endswith('.png'):
        pass
    else:
        raise NotImplementedError()
    cmds += [
      'convert -rotate 90 -crop 700x300+50+0 "{input_file}" a.png',
      'convert -rotate 90 -crop 700x350+230+350 "{input_file}" b.png',
      'convert -rotate 90 -crop 700x350+00+700 "{input_file}" c.png',
      'convert -rotate 90 -crop 650x450+0+1050 "{input_file}" d.png',
      'convert -rotate 90 -crop 900x350+150+1450 -resize 700 "{input_file}" e.png',
      'convert -append -gravity Center +repage a.png b.png c.png d.png e.png output.png',
      'convert -density 288 -set units PixelsPerInch output.png output.pdf',
    ]
    for cmd in cmds:
        cmd = cmd.format(input_file=input_file, pdf_file=filename)
        cmd = cmd_line_to_args(cmd)
        try:
            logger.debug('running the following command: ' + ' '.join(cmd))
            subprocess.check_call(cmd, cwd='/tmp')
        except subprocess.CalledProcessError as e:
            raise NameError('Could not convert the PDF file: ' + str(e))
    return os.path.join(wd, 'output.pdf')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('label_file', nargs='+', help='.pdf or .png file containing the Amazon.de return label')
    args = parser.parse_args()
    if args.debug: logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    for label_file in args.label_file:
        conv_file = convert(label_file)
        print(conv_file)
