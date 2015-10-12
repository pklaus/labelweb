
import re

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

