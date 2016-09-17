#!/usr/bin/env python

import subprocess
import re
import os
import logging

from helpers import cmd_line_to_args

logger = logging.getLogger(__name__)

def render(pdf_filename, wd='/tmp', density = 72):

    ret = {'success': False, 'pages': [], 'pdf': pdf_filename}

    # get info on pages
    cmd = 'gm identify -verbose -density {density} "{pdf}"'
    cmd = cmd.format(pdf=pdf_filename, density=density)
    args = cmd_line_to_args(cmd)
    logger.debug(cmd)
    logger.debug(str(args))
    try:
        info_text = subprocess.check_output(args, cwd=wd).decode('utf-8')
    except subprocess.CalledProcessError as e:
        logger.error("Running the command '{}' failed with the return code {}.".format(cmd, e.returncode))
        return ret
    size_matcher = re.compile(r'\s*Geometry:\s+(?P<size>(\d+(\.\d*)?)x(\d+(\.\d*)?))')
    page_sizes = [match[0].split('x') for match in size_matcher.findall(info_text)]
    page_sizes = [(float(size[0]), float(size[1])) for size in page_sizes] # parse floats
    page_sizes = [(size[0] / density * 25.4, size[1] / density * 25.4) for size in page_sizes] # dots to mm
    num_pages = len(page_sizes)

    # render pages
    cmd = """
    gm convert            \
       -verbose           \
       -density {density} \
       -quality 00        \
       -sharpen 0x1.0     \
       +adjoin            \
       "{pdf}"            \
       "{outfile_tpl}"
    """.replace('\n', ' ')
    cmd = cmd.format(pdf=pdf_filename, density=density, outfile_tpl='single%03d.png')
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
        ret['pages'].append({'size': page_sizes[i], 'img_file': img_file})
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
        results['conversions'].append(render(pdf_filename, wd=os.getcwd()))
    pprint.pprint(results)

