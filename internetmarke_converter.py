#!/usr/bin/env python

"""
Internetmarke Label Converter -

Convert Internetmarke PDF stamp labels to a size
suitable for Brother label printers.

Select "Leitz 39mm endless" as format when purchasing
the stamps. The PDF pages of the stamps will be of the dimensions:
mm:            39.0   x  34.0
inch:           1.54  x   1.34
dots @72dpi:  110.551 x  96.377
dots @300dpi: 460.629 x 401.571

After the conversion, the output labels will be
566 x 165 px^2 big. This is equivalent to the
printable area of 17x54mm Brother labels.

This software requires ImageMagick to be
installed and available in your PATH.
"""

import subprocess
import re
import os

from helpers import cmd_line_to_args

def convert(pdf_filename):
    wd = '/tmp'
    number_of_pages = "identify -ping -format %n\n \"{input_file}\"".format(input_file=pdf_filename)
    number_of_pages = cmd_line_to_args(number_of_pages)
    number = int(subprocess.check_output(number_of_pages, cwd=wd).decode('ascii').split('\n')[0])
    for i in range(number):
        cmds = [
          "convert -density 300 -crop 158x132+029+142 -quality 00 \"{input_file}[{i}]\" A{i}.png",
          "convert -density 300 -crop 217x117+190+170 -quality 00 \"{input_file}[{i}]\" B{i}.png",
          "convert -density 400 -crop 150x110+420+41  -quality 00 \"{input_file}[{i}]\" C{i}.png",
          "convert +append +repage A{i}.png B{i}.png C{i}.png ABC{i}.png",
          "convert ABC{i}.png -background white -gravity center -extent 566x165 out{i}.png",
        ]
        for cmd in cmds:
            cmd = cmd.format(input_file=pdf_filename, i=i)
            cmd = cmd_line_to_args(cmd)
            try:
                subprocess.check_call(cmd, cwd=wd)
            except subprocess.CalledProcessError as e:
                raise NameError('Could not convert the PDF file: ' + str(e))
    in_files = ' '.join('out{0}.png'.format(i) for i in range(number))
    cmd = "convert {in_files} out.pdf".format(in_files=in_files)
    cmd = cmd_line_to_args(cmd)
    subprocess.check_call(cmd, cwd=wd)
    return os.path.join(wd, 'out.pdf')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label_pdf', nargs='+', help='')
    args = parser.parse_args()
    for label_pdf in args.label_pdf:
        conv_file = convert(label_pdf)
        print(conv_file)
