#! /usr/local/bin/python3
""" These are the handlers for all the head and body rule types defined in ReqBlock.g4
"""

import sys
from dgw_utils import class_name,\
    build_course_list,\
    num_classes_or_num_credits


# Handlers
# =================================================================================================


# block()
# -------------------------------------------------------------------------------------------------
def block(ctx, institution):
  """
      block           : NUMBER BLOCK expression rule_tag? label;

      The expression will be a {block-type, block-value} pair enclosed in parens and separated by
      an equal sign.
  """
  return_dict = {'tag': 'block', 'number': ctx.NUMBER().getText()}
  # FIXME
  symbols = ctx.expression().expression().SYMBOL()
  assert isinstance(symbols, list) and len(symbols) == 2, (f'Invalid block expression: '
                                                           f'{ctx.expression().getText()}')
  return_dict['block_type'] = symbols[0].getText().upper().strip()
  return_dict['block_value'] = symbols[1].getText().upper().strip()

  if ctx.label():
    return_dict['label'] = ctx.label().string().getText().strip(' "')
  sys.exit(return_dict)
  return return_dict


# blocktype()
# -------------------------------------------------------------------------------------------------
def blocktype(ctx, institution):
  """
      blocktype       : NUMBER BLOCKTYPE expression label;

      The expression is a block type, enclosed in parentheses
  """
  return_dict = {'tag': 'blocktype', 'number': ctx.NUMBER().getText()}
  return_dict['block_type'] = ctx.expression().SYMBOL().getText().upper()

  if ctx.label():
    return_dict['label'] = ctx.label().string().getText().strip(' "')

  return return_dict


# copy_rules()
# -------------------------------------------------------------------------------------------------
def copy_rules(ctx, institution):
  """
      copy_rules      : COPY_RULES expression SEMICOLON?;

      The expression is a rule_id enclosed in parentheses.
  """
  return_dict = {'tag': 'copyrules', 'institution': institution}
  return_dict['rule_id'] = ctx.expression().SYMBOL().getText().upper()

  return return_dict


# class_credit_body()
# -------------------------------------------------------------------------------------------------
def class_credit_body(ctx, institution):
  """
      class_credit_body   : (num_classes | num_credits)
                      (logical_op (num_classes | num_credits))?
                      (course_list_body | IS? pseudo | share | rule_tag | tag)*
                      display* label?;

      Note: rule_tag is used only for audit presentation, and is ignored here.
  """
  return_dict = {'tag': 'class_credit'}
  return_dict['num_classes_credits'] = num_classes_or_num_credits(ctx)

  return_dict['is_pseudo'] = True if ctx.pseudo() else False

  if ctx.share():
    return_dict['share'] = share(ctx.share(), institution)

  if ctx.display():
    display_text = ''
    for item in ctx.display():
      display_text += item.string().getText().strip(' "') + ' '
    return_dict['display'] = display_text.strip()

  if ctx.label():
    return_dict['label'] = ctx.label().string().getText().strip(' "')

  return return_dict


# class_credit_head()
# -------------------------------------------------------------------------------------------------
def class_credit_head(ctx, institution):
  """
      class_credit_head   : (num_classes | num_credits)
                            (logical_op (num_classes | num_credits))?
                            (IS? pseudo | header_tag | tag)*
                            display* label?;
      num_classes         : NUMBER CLASS allow_clause?;
      num_credits         : NUMBER CREDIT allow_clause?;

      Note: header_tag is used only for audit presentation, and is ignored here.
"""
  return_dict = {'tag': 'class_credit'}
  return_dict['num_classes_credits'] = num_classes_or_num_credits(ctx)

  return_dict['is_pseudo'] = True if ctx.pseudo() else False

  if ctx.display():
    display_text = ''
    for item in ctx.display():
      display_text += item.string().getText().strip(' "') + ' '
    return_dict['display'] = display_text.strip()

  return_dict['label'] = None
  if ctx.label():
    return_dict['label'] = ctx.label().string().getText().strip(' "')

  return return_dict


# group()
# -------------------------------------------------------------------------------------------------
def group(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# if_then_body()
# -------------------------------------------------------------------------------------------------
def if_then_body(ctx, institution):
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# if_then_head()
# -------------------------------------------------------------------------------------------------
def if_then_head(ctx, institution):
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# lastres()
# -------------------------------------------------------------------------------------------------
def lastres(ctx, institution):
  """ TODO lastres() not tested yet & course_list not implemented yet
      lastres         : LASTRES NUMBER (OF NUMBER)?
                        class_or_credit
                        course_list? tag? display* label?;
  """
  return_dict = {'tag': 'lastres'}
  if ctx.class_or_credit():
    if 'class' in ctx.class_or_credit().getText().lower():
      return_dict['class_or_credit'] = 'class'
    else:
      return_dict['class_or_credit'] = 'credit'

  numbers = ctx.NUMBER()
  return_dict['number'] = numbers.pop().strip()
  if len(numbers) > 0:
    return_dict['of'] = numbers.pop().strip()
  else:
    return_dict['of'] = None

  assert len(numbers) == 0

  return_dict['course_list'] = 'Not implemented yet'

  return_dict['display'] = None
  if ctx.display():
    display_text = ''
    for item in ctx.display():
      display_text += item.string().getText().strip(' "') + ' '
    return_dict['display'] = display_text.strip()

  return_dict['label'] = None
  if ctx.label():
    return_dict['label'] = ctx.label().string().getText().strip(' "')

  return return_dict


# maxclass()
# --------------------------------------------------------------------------------------------------
def maxclass(ctx, institution):
  """
      maxclass        : MAXCLASS NUMBER course_list? tag?;
  """
  return_dict = {'tag': 'maxclass',
                 'number': ctx.NUMBER().getText().strip()}
  return_dict['course_list'] = build_course_list(ctx.course_list(), institution)
  return return_dict


# maxcredit()
# --------------------------------------------------------------------------------------------------
def maxcredit(ctx, institution):
  """
      maxcredit       : MAXCREDIT NUMBER course_list? tag?;
  """
  return_dict = {'tag': 'maxcredit',
                 'number': ctx.NUMBER().getText().strip()}
  return_dict['course_list'] = build_course_list(ctx.course_list(), institution)
  return return_dict


# maxpassfail()
# --------------------------------------------------------------------------------------------------
def maxpassfail(ctx, institution):
  """
      maxpassfail     : MAXPASSFAIL NUMBER class_or_credit tag?;
  """
  return_dict = {'tag': 'maxpass_fail',
                 'number': ctx.NUMBER().getText(),
                 'class_or_credit': 'class_or_credit(ctx.class_or_credit()'}
  return return_dict


# maxperdisc()
# -------------------------------------------------------------------------------------------------
def maxperdisc(ctx, institution):
  """
      maxperdisc      : MAXPERDISC NUMBER class_or_credit LP SYMBOL (list_or SYMBOL)* RP tag?;
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# maxterm()
# -------------------------------------------------------------------------------------------------
def maxterm(ctx, institution):
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# maxtransfer()
# -------------------------------------------------------------------------------------------------
def maxtransfer(ctx, institution):
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# minclass()
# --------------------------------------------------------------------------------------------------
def minclass(ctx, institution):
  """
      minclass        : MINCLASS NUMBER course_list tag? display* label?;
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# mincredit()
# --------------------------------------------------------------------------------------------------
def mincredit(ctx, institution):
  """
      mincredit       : MINCREDIT NUMBER course_list tag? display* label?;
  """
  return_dict = {'tag': 'mincredit', 'number': ctx.NUMBER().getText()}
  if ctx.display():
    display_text = ''
    for item in ctx.display():
      display_text += item.string().getText().strip(' "') + ' '
    return_dict['display'] = display_text.strip()

  return_dict['course_list'] = build_course_list(ctx.course_list, institution)

  if ctx.display():
    display_text = ''
    for item in ctx.display():
      display_text += item.string().getText().strip(' "') + ' '
    return_dict['display'] = display_text.strip()

  if ctx.label():
    return_dict['label'] = ctx.label().string().getText().strip(' "')

  return return_dict


# mingpa()
# --------------------------------------------------------------------------------------------------
def mingpa(ctx, institution):
  """
      mingpa          : MINGPA NUMBER (course_list | expression)? tag? display* label?;
  """
  return_dict = {'tag': 'mingpa', 'number': ctx.NUMBER().getText()}

  if ctx.course_list():
    return_dict['course_list'] = build_course_list(ctx.course_list, institution)

  if ctx.expression():
    return_dict['expression'] = ctx.expression().getText()

  if ctx.display():
    display_text = ''
    for item in ctx.display():
      display_text += item.string().getText().strip(' "') + ' '
    return_dict['display'] = display_text.strip()

  if ctx.label():
    return_dict['label'] = ctx.label().string().getText().strip(' "')

  return return_dict


# mingrade()
# -------------------------------------------------------------------------------------------------
def mingrade(ctx, institution):
  """
      mingrade        : MINGRADE NUMBER;
  """
  return {'tag': 'mingrade', 'number': ctx.NUMBER().getText()}


# minperdisc()
# -------------------------------------------------------------------------------------------------
def minperdisc(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# minres()
# -------------------------------------------------------------------------------------------------
def minres(ctx, institution):
  """ minres          : MINRES (num_classes | num_credits) display* label? tag?;
  """
  return_dict = num_classes_or_num_credits(ctx)
  return_dict['tag'] = 'minres'
  return return_dict


# noncourse()
# -------------------------------------------------------------------------------------------------
def noncourse(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# optional()
# -------------------------------------------------------------------------------------------------
def optional(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# remark()
# -------------------------------------------------------------------------------------------------
def remark(ctx, institution):
  """
  """
  return_dict = {'tag': 'remark',
                 'text': ' '.join([ctx.string().getText().strip(' "') for ctx in ctx.remark()])}
  return return_dict


# rule_complete()
# -------------------------------------------------------------------------------------------------
def rule_complete(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# share()
# -------------------------------------------------------------------------------------------------
def share(ctx, institution):
  """
      share           : (SHARE | DONT_SHARE) (NUMBER class_or_credit)? expression? tag?;
  """
  return_dict = {'tag': 'share'}

  if ctx.SHARE():
    return_dict['share_type'] = 'share'
  else:
    return_dict['share_type'] = 'exclusive'

  if ctx.NUMBER():
    return_dict['number'] = ctx.NUMBER().getText().strip()
    return_dict['class_or_credit'] = class_or_credit(ctx.class_or_credit())
  if ctx.expression():
    return_dict['expression'] = ctx.expression().getText()

  return return_dict


# standalone()
# -------------------------------------------------------------------------------------------------
def standalone(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# subset_body()
# -------------------------------------------------------------------------------------------------
def subset_body(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# subset_head()
# -------------------------------------------------------------------------------------------------
def subset_head(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return {}


# under()
# -------------------------------------------------------------------------------------------------
def under(ctx, institution):
  """
  """
  print(class_name(ctx), 'not implemented yet', file=sys.stderr)
  return{}


# Dispatch Tables
# =================================================================================================
""" There are two in case If-then and Share need to be handled differently in Head and Body.
"""
dispatch_head = {
    'class_credit_head': class_credit_head,
    'if_then': if_then_head,
    'lastres': lastres,
    'maxclass': maxclass,
    'maxcredit': maxcredit,
    'maxpassfail': maxpassfail,
    'maxperdisc': maxperdisc,
    'maxterm': maxterm,
    'maxtransfer': maxtransfer,
    'mingrade': mingrade,
    'minclass': minclass,
    'mincredit': mincredit,
    'mingpa': mingpa,
    'minperdisc': minperdisc,
    'minres': minres,
    'optional': optional,
    'remark': remark,
    'share': share,
    'standalone': standalone,
    'subset': subset_head,
    'under': under
}

dispatch_body = {
    'block': block,
    'blocktype': blocktype,
    'class_credit_body': class_credit_body,
    'copy_rules': copy_rules,
    'group': group,
    'if_then': if_then_body,
    'noncourse': noncourse,
    'remark': remark,
    'rule_complete': rule_complete,
    'subset': subset_body
}


# dispatch()
# -------------------------------------------------------------------------------------------------
def dispatch(ctx: any, institution: str, which_part: str):
  """ Invoke the appropriate handler given its top-level context.
  """
  if which_part == 'head':
    return dispatch_head[class_name(ctx).lower()](ctx, institution)
  else:
    return dispatch_body[class_name(ctx).lower()](ctx, institution)
