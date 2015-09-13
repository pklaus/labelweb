#!/usr/bin/env python

"""
DHL Label Converter –

Convert DHL PDF shipping labels to a size
suitable for Dymo or Brother label printers.
The label size will be 59 mm x 144 mm.

This software requires ImageMagick to be
installed and available in your PATH.
"""

import subprocess
import re
import os

def convert(pdf_filename):
    wd = '/tmp'
    resolution = 300
    cmds = [
      "convert -rotate 90 -crop 1134x680+1694+168 -quality 00 -density 270 {input_file} A.png",
      "convert -rotate 90 -crop  810x115+1700+850 -quality 00 -density 270 {input_file} B.png",
      "convert -rotate 90 -crop 560x688+1815+1215 -quality 00 -density 250 {input_file} C.png",
      "composite -geometry +13+567 B.png A.png AB.png",
      "convert +append +repage AB.png C.png out.png",
      "convert -density 300 out.png out.pdf"
    ]
    for cmd in cmds:
        cmd = cmd.format(input_file=pdf_filename)
        cmd = cmd.split()
        try:
            subprocess.check_call(cmd, cwd=wd)
        except subprocess.CalledProcessError as e:
            raise NameError('Could not convert the PDF file: ' + str(e))
    return os.path.join(wd, 'out.pdf')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label_pdf', nargs='+', help='')
    args = parser.parse_args()
    for label_pdf in args.label_pdf:
        conv_file = convert(label_pdf)
        print(conv_file)
