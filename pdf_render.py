#!/usr/bin/env python

import subprocess
import re
import os

def render(pdf_filename):
    ret = {'success': False, 'pages': []}
    wd = '/tmp'
    resolution = 150

    # get info on pages
    cmd = "identify -verbose {pdf}"
    cmd = cmd.format(pdf=pdf_filename)
    cmd = cmd.split()
    try:
        info_text = subprocess.check_output(cmd, cwd=wd).decode('ascii')
    except subprocess.CalledProcessError as e:
        logger.error("Running the command '{}' failed with the return code {}.".format(' '.join(cmd), e.returncode))
        return ret
    size_matcher = re.compile(r'\s*Print size:\s+(?P<size>(\d+(\.\d*)?)x(\d+(\.\d*)?))\s*')
    sizes = [match[0].split('x') for match in size_matcher.findall(info_text)]
    sizes = [(float(size[0]), float(size[1])) for size in sizes] # parse floats
    sizes = [(size[0] * 25.4, size[1] * 25.4) for size in sizes] # inch to mm
    num_pages = len(sizes)

    # render pages
    cmd = "convert -quality 00 -density {res}x{res} {pdf} single%03d.png"
    cmd = cmd.format(pdf=pdf_filename, res=resolution)
    cmd = cmd.split()
    try:
        subprocess.check_call(cmd, cwd=wd)
    except subprocess.CalledProcessError as e:
        logger.error("Running the command '{}' failed with the return code {}.".format(' '.join(cmd), e.returncode))
        return ret
    for i in range(num_pages):
        img_file = os.path.join(wd, 'single{:03d}.png'.format(i))
        ret['pages'].append({'size': sizes[i], 'img_file': img_file})
    ret['success'] = True

    return ret

if __name__ == "__main__":
    import pprint
    #pprint.pprint(render('/tmp/INTERNETMARKE-Testprint.pdf'))
    pprint.pprint(render('/tmp/Briefmarken.2Stk.08.09.2015_2139.pdf'))

