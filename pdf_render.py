#!/usr/bin/env python

import subprocess
import re
import os
import logging

logger = logging.getLogger(__name__)

def cmd_line_to_args(cmd_line):
    """
    Split a command line into space-separated arguments.
    But leave quoted arguments (possibly containing spaces) alone.

    :param str cmd_line: The command line to split into single arguments
    :returns: args
    :rtype: list of str
    """
    SPACE_SEP = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
    # split while respecting quotes: http://stackoverflow.com/a/2787064/183995
    args = SPACE_SEP.split(cmd_line)[1::2]
    args = [arg.strip('"') for arg in args]
    return args

def render(pdf_filename):
    ret = {'success': False, 'pages': [], 'pdf': pdf_filename}
    wd = '/tmp'
    resolution = 72

    # get info on pages
    cmd = 'identify -verbose "{pdf}"'
    cmd = cmd.format(pdf=pdf_filename)
    args = cmd_line_to_args(cmd)
    logger.debug(cmd)
    logger.debug(str(args))
    try:
        info_text = subprocess.check_output(args, cwd=wd).decode('utf-8')
    except subprocess.CalledProcessError as e:
        logger.error("Running the command '{}' failed with the return code {}.".format(cmd, e.returncode))
        return ret
    size_matcher = re.compile(r'\s*Print size:\s+(?P<size>(\d+(\.\d*)?)x(\d+(\.\d*)?))\s*')
    sizes = [match[0].split('x') for match in size_matcher.findall(info_text)]
    sizes = [(float(size[0]), float(size[1])) for size in sizes] # parse floats
    sizes = [(size[0] * 25.4, size[1] * 25.4) for size in sizes] # inch to mm
    num_pages = len(sizes)

    # render pages
    cmd = """
    convert             \
       -verbose         \
       -density {res}   \
       -quality 00      \
       "{pdf}"          \
       -background white\
       -alpha remove    \
       -sharpen 0x1.0   \
        "{outfile_tpl}"
    """.replace('\n', ' ')
    cmd = cmd.format(pdf=pdf_filename, res=resolution, outfile_tpl='single%03d.png')
    args = cmd_line_to_args(cmd)
    logger.debug(cmd)
    logger.debug(str(args))
    try:
        subprocess.check_call(args, cwd=wd)
    except subprocess.CalledProcessError as e:
        logger.error("Running the command '{}' failed with the return code {}.".format(' '.join(cmd), e.returncode))
        return ret
    for i in range(num_pages):
        img_file = os.path.join(wd, 'single{:03d}.png'.format(i))
        ret['pages'].append({'size': sizes[i], 'img_file': img_file})
    ret['success'] = True

    return ret

if __name__ == "__main__":
    import argparse, pprint
    parser = argparse.ArgumentParser(description='Render Pages from a PDF file to PNG Images')
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    parser.add_argument('pdf_filename', nargs='+', help='The PDF file(s) to render')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    results = {'conversions': []}
    for pdf_filename in args.pdf_filename:
        results['conversions'].append(render(pdf_filename))
    pprint.pprint(results)

