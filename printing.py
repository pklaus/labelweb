#!/usr/bin/env python

"""
Printing functionality
"""

import subprocess
import re
import os
import logging

logger = logging.getLogger(__name__)

def print_label_brother(filename, printer, options):
    default_options = [
      "-o PageSize=62X1",
      "-o BrMargin=3",
      "-o BrPriority=BrQuality",
    ]
    options = list(set(default_options + options))
    lpr(filename, printer, options)

def lpr(filename, printer, options=None):
    print_cmd = """
    lpr -P {printer} \
      {options} \
      {filename}
    """
    if not options: options = []
    options = ' '.join(options)
    cmd = print_cmd.format(printer=printer, options=options, filename=filename)
    cmd = cmd.split()
    logger.debug('printing with those cmd arguments: ' + ' '.join(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        raise NameError('Could not send this print command: ' + ' '.join(cmd))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename', help='File to print')
    parser.add_argument('--printer', required='True', help='The name of the printer (in CUPS)')
    parser.add_argument('--options', nargs='+', help='Options for the lpr printing command')
    args = parser.parse_args()
    #lpr(args.filename, args.printer, ['-o landscape'])
    print_label_brother(args.filename, args.printer, ['-o landscape'])
    print("Printer job for {filename} created.".format(filename=args.filename))
