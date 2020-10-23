#! /usr/local/bin/python3
"""
    Generate HTML representation of nested lists/dicts.

    Each list will be presented as an unordered list, which will be the contents of a details
    element.

    Each dict will be presented as a definition list, with the keys as definition terms and the
    values as definitions.

    Lists and dicts can be nested within one another to any depth.

    The unordered and definition lists will be contained in details elements.

      If a dict has a "tag" key, it's value will be the summary element of the details element.
      Otherwise the summary will be the word "unnamed."

      The length of each list is appended to the summary element of its containing details element.

"""

import os
import sys

from course_lookup import lookup_course

from dgw_interpreter import dgw_parser

DEBUG = os.getenv('DEBUG_HTML')

quarantine_dict = {}
with open('/Users/vickery/dgw_processor/testing/quarantine_list') as ql_file:
  quarantine_list = ql_file.readlines()
  for line in quarantine_list:
    if line[0] == '#':
      continue
    body, ellucian = line.split('::')
    ellucian = 'y' in ellucian or 'Y' in ellucian
    college, requirement_id, *explanation = body.split(' ')
    explanation = ' '.join(explanation).strip()

    quarantine_dict[(college, requirement_id)] = (explanation.strip('.'), ellucian)


# list_of_courses()
# -------------------------------------------------------------------------------------------------
def list_of_courses(course_tuples: list, title_str: str, highlight=False) -> str:
  """ There are two flavors of course_tuples: scribed courses have just the discipline and catalog
      number, with an optional with clause, so the length of those tuples is 3. Otherwise, the tuple
      consists of the course_id, offer_nbr, discipline, catalog_number, title, and optional with
      clause (length 6).
  """
  assert len(course_tuples) > 0
  suffix = '' if len(course_tuples) == 1 else 's'
  class_str = ' class="error"' if highlight else ''
  return_str = (f'<details><summary{class_str}>{len(course_tuples)} {title_str}{suffix}</summary>')
  for course_tuple in course_tuples:
    if len(course_tuple) == 3:
      return_str += f'<div>{course_tuple[0]} {course_tuple[1]}'
      if course_tuple[2] is not None:
        return_str += f' with {course_tuple[2]}'
      return_str += '</div>\n'
    else:
      return_str += (f'<details><summary>{course_tuple[2]} {course_tuple[3]}: '
                     f'<em>{course_tuple[4]}</em>')
      if course_tuple[-1] is not None:
        return_str += f' with {course_tuple[-1]}'
      return_str += '</summary>'
      return_str += f'{lookup_course(course_tuple[0], offer_nbr=course_tuple[1])[1]}</details>'
  return_str += '</details>\n'
  return return_str


# dict_to_html_details()
# -------------------------------------------------------------------------------------------------
def dict_to_html_details(info: dict, is_head, is_body) -> str:
  """ Convert a dict to a HTML <details> element. The <summary> element is based on the tag/label
      fields of the dict. During development, the context path goes next. Then, if there are remark
      or display fields, they go after that, followed by everything else.
  """

  summary = '<summary class="error">No-tag-or-label Bug</summary>'
  try:
    tag = info.pop('tag')
    summary = f'<summary>{tag.replace("_", " ").title()}</summary>'
  except KeyError as ke:
    tag = None
  try:
    label = info.pop('label')
    summary = f'<summary>{label}</summary>'
  except KeyError as ke:
    label = None

  try:
    remark = info.pop('remark')
    remark = f'<p><strong>{remark}</strong></p>'
  except KeyError as ke:
    remark = ''
  try:
    display = info.pop('display')
    display = f'<p><em>{display}</em></p>'
  except KeyError as ke:
    display = ''
  try:
    context_path = info.pop('context_path')
    if DEBUG:
      return_str += f'<div><strong>Context:</strong>{context_path}</div>'
  except KeyError as ke:
    context_path = ''

  return_str = (f'<details>{summary}{context_path}{remark}{display}')

  for key, value in info.items():

    # Special presentation for course lists, if present
    if key == 'attributes':  # Handled by active_courses
      continue

    if key == 'list_type':
      if value != 'None':
        # AND/OR
        return_str += f'<p>List type: This is an {value} list.</p>'
        continue

    if key == 'scribed_courses':
      assert isinstance(value, list)
      return_str += list_of_courses(value, 'Scribed Course')
      continue

    if key == 'active_courses':
      assert isinstance(value, list)
      if len(value) == 0:
        return_str += '<div class="error">No Active Courses!</div>'
      else:
        attributes_str = ''
        try:
          attributes = info['attributes']
          if attributes is not None:
            attributes_str = ','.join(attributes)
        except KeyError as ke:
          pass
      return_str += list_of_courses(value, f'Active {attributes_str} Course')
      continue

    if key == 'inactive_courses':
      assert isinstance(value, list)
      if len(value) > 0:
        return_str += list_of_courses(value, 'Inactive Course')
      continue

    if key == 'include_courses':
      assert isinstance(value, list)
      if len(value) > 0:
        return_str += list_of_courses(value, 'Include Course')
      continue

    if key == 'except_courses':
      assert isinstance(value, list)
      if len(value) > 0:
        return_str += list_of_courses(value, 'Except Course')
      continue

    if key == 'missing_courses':
      assert isinstance(value, list)
      if len(value) > 0:
        return_str += list_of_courses(value,
                                      'Not-Found-in-CUNYfirst Course', highlight=True)
      continue

    # Key-value pairs not specific to course lists
    if value is None:
      continue  # Omit empty fields

    if isinstance(value, bool):
      # Show booleans only if true
      if value:
        return_str += f'<div>{key}: {value}</div>'

    elif isinstance(value, str):
      try:
        # Interpret numeric and range strings
        if ':' in value and 2 == len(value.split(':')):
          # range of values: check if floats or ints
          range_floor, range_ceil = [float(v) for v in value.split(':')]
          if range_floor != int(range_floor) or range_ceil != int(range_ceil):
            return_str += (f'<div>{key}: between {range_floor:0.1f} and '
                           f'{range_ceil:0.1f}</div>')
          elif int(range_floor) != int(range_ceil):
            return_str += (f'<div>{key}: between {int(range_floor)} and '
                           f'{int(range_ceil)}</div>')
          else:
            # both are ints and are the same
            return_str += f'<div>{key}: {int(range_floor)}</div>'
        else:
          # single value
          if int(value) == float(value):
            return_str += f'<div>{key}: {int(value)}</div>'
          else:
            return_str += f'<div>{key}: {float(value):0.1f}</div>'

      except ValueError as ve:
        # Not a numeric string; just show the text.
        return_str += f'<div>{key}: {value}</div>'

    else:
      # Fall through
      print(f'Fallthrough: {key=} {value=} {is_head=} {is_body=}', file=sys.stderr)
      return_str += to_html(value, is_head, is_body)

  return return_str + '</details>'


# list_to_html_list()
# -------------------------------------------------------------------------------------------------
def list_to_html_list(info: list, is_head, is_body) -> str:
  """
  """
  num = len(info)
  suffix = '' if num == 1 else 's'
  if num <= 12:
    num_str = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
               'Ten', 'Eleven', 'Twelve'][num]
  else:
    num_str = f'{num:,}'
  return_str = f'<details><summary>{num_str} item{suffix}</summary>'
  return_str += '\n'.join([f'{to_html(element, is_head, is_body)}' for element in info])
  return return_str + '</details>'


# to_html()
# -------------------------------------------------------------------------------------------------
def to_html(info: any, is_head=False, is_body=False) -> str:
  """  Return a nested HTML data structure as described above.
  """
  if info is None:
    return ''
  if isinstance(info, bool):
    return 'True' if info else 'False'
  if isinstance(info, list):
    return list_to_html_list(info, is_head, is_body)
  if isinstance(info, dict):
    return dict_to_html_details(info, is_head, is_body)

  return info


# scribe_block_to_html()
# -------------------------------------------------------------------------------------------------
def scribe_block_to_html(row: tuple, period='all') -> str:
  """ Generate html for the scribe block and interpreted head and body lists objects.
  """
  if row.requirement_html == 'Not Available':
    return '<h1>This scribe block is not available.</h1><p><em>Should not occur.</em></p>'

  if (row.institution, row.requirement_id) in quarantine_dict.keys():
    explanation, ellucian = quarantine_dict[(row.institution, row.requirement_id)]
    print(f'{explanation=} {ellucian=}', file=sys.stderr)
    if ellucian:
      qualifier = 'Although the Ellucian parser does not report an error,'
    else:
      qualifier = 'Neither the Ellucian parser nor'
    disclaimer = f"""
    <p class="disclaimer">
      <span class="error">
        {qualifier} this parser was unable to process this Scribe Block, with the following
        explanation:
      </span>
        “{explanation}.”
    </p>
"""
  else:
   disclaimer = """
   <p class="disclaimer error">
     The following is an <strong>incomplete interpretation</strong> of the above scribe block. The
     interpreter that produces this view is under development.
   </p>
"""

  if len(row.head_objects) == 0 and len(row.body_objects) == 0:
    head_list, body_list = dgw_parser(row.institution,
                                      row.block_type,
                                      row.block_value,
                                      period=period)
  else:
    head_list, body_list = row.head_objects, row.body_objects

  return row.requirement_html + disclaimer + f"""
<section>
  <h1>Head</h1>
  {to_html(head_list, is_head=True)}
  <h1>Body</h1>
  {to_html(body_list, is_body=True)}
</section>
"""
