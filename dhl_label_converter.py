#!/usr/bin/env python

"""
DHL Label Converter -

Convert DHL PDF shipping labels to a size
suitable for Dymo or Brother label printers.
The label size will be 59 mm x 148 mm.

This software requires ImageMagick to be
installed and available in your PATH.
"""

import subprocess
import re
import os

from helpers import cmd_line_to_args

def convert(pdf_filename, variant='normal'):
    wd = '/tmp'
    resolution = 300
    if variant == 'normal':
        cmds = [
          'convert -rotate 90 -crop 1170x688+1658+160 -quality 00 -density 270 "{input_file}" A.png',
          'convert -rotate 90 -crop  810x115+1700+850 -quality 00 -density 270 "{input_file}" B.png',
          'convert -rotate 90 -crop 560x696+1815+1207 -quality 00 -density 250 "{input_file}" C.png',
          'composite -geometry +49+575 B.png A.png AB.png',
          'convert +append +repage AB.png C.png out.png',
          'convert -density 300 out.png out.pdf',
        ]
    elif variant == 'extended':
        cmds = [
          'convert -rotate 90 -crop 1270x634+1880+180  -quality 00 -density 300 "{input_file}" A.png',
          'convert -rotate 90 -crop 1270x650+1880+811  -quality 00 -density 300 "{input_file}" B.png',
          'convert -rotate 90 -crop 1240x696+1895+1550 -quality 00 -density 300 "{input_file}" C.png',
          'convert +append +repage A.png B.png AB.png',
          'convert +append +repage AB.png C.png out.png',
          'convert -density 300 out.png out.pdf',
        ]
    else:
        raise ValueError('unknown variant: ' + str(variant))
    for cmd in cmds:
        cmd = cmd.format(input_file=pdf_filename)
        cmd = cmd_line_to_args(cmd)
        try:
            subprocess.check_call(cmd, cwd=wd)
        except subprocess.CalledProcessError as e:
            raise NameError('Could not convert the PDF file: ' + str(e))
    return os.path.join(wd, 'out.pdf')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=('normal', 'extended'), default='normal',
        help='Choose the variant for your output. "normal" is a narrow version. "extended" works even for big (international) labels.')
    parser.add_argument('label_pdf', nargs='+', help='The labels (PDF files) you want to convert')
    args = parser.parse_args()
    for label_pdf in args.label_pdf:
        conv_file = convert(label_pdf, variant=args.variant)
        print(conv_file)
