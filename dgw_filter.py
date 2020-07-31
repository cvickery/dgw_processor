#! /usr/local/bin/python3
""" Function to filter out cruft at the end of requirement blocks.
    Can be used from the command line as a filter.
"""

import re
import sys


# dgw_filter()
# -------------------------------------------------------------------------------------------------
def dgw_filter(src, remove_hide=True, fix_area=True, remove_comments=False):
  """ Remove all text following "END." Optionally, remove comments and text related to hiding
      parts of the requirements from the audit report.
  """
  # Remove all text following END.
  return_str = re.sub(r'[Ee][Nn][Dd]\.(.|\n)*', 'END.\n', src)

  # Fix area lists: ,] has to be followed by [ with possibly intervening whitespace
  if fix_area:
    return_str = re.sub(r'(,\s*])(\s*)([^\s\[])', '\\1\\2[\\3', return_str)

  # Remove {HIDE }, HIDE-FROM-ADVICE, and HIDE-RULE
  if remove_hide:
    return_str = re.sub(r'[Hh][Ii][Dd][Ee]-?(([Ff][Rr][Oo][Mm]-?[Aa][Dd][Vv][Ii][Cc][Ee])|'
                        r'([Rr][Uu][Ll][Ee]))?',
                        '', return_str.replace('{', '').replace('}', ''))

  # Remove all comments
  if remove_comments:
    return_str = re.sub(f'#.*\n', '', return_str)

  return return_str


# As a command, act as a stdin|stdout filter
if __name__ == "__main__":
  print(dgw_filter(sys.stdin.read()))
