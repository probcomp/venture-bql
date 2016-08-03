# -*- Mode: Python; coding: utf-8; python-indent-offset: 2 -*-

import StringIO

import bayeslite

from bayeslite.parse import bql_string_complete_p

import venture.plex as Plex
import venture.value.dicts as vv
from venture.parser import ast
from venture.parser.venture_script import subscanner

class VentureBQLScanner(Plex.Scanner):
  def __init__(self, stream):
    Plex.Scanner.__init__(self, self.LEXICON, stream)
    self._name = None
    self._name_position = None
    self._bql = StringIO.StringIO()
    self._bql_start = None

  def _scan_population_name(self, text):
    self._name = text
    self._name_position = [self.cur_pos, self.cur_pos + len(text) - 1]
    self.begin('2')

  def _scan_bql_start(self, text):
    self._bql_start = self.cur_pos
    self.begin('4')

  def _scan_bql_body(self, text):
    self._bql.write(text)

  def _scan_bql_maybe_end(self, text):
    assert text == '}'
    if bql_string_complete_p(self._bql.getvalue()):
      operator = ast.Located([0, self.cur_pos - 1], vv.symbol('bayesdb_bql'))
      population = ast.Located(self._name_position, vv.symbol(self._name))
      bql = ast.Located(
        [self._bql_start, self.cur_pos - 1],
        vv.string(self._bql.getvalue()))
      self.produce(ast.Located([0, self.cur_pos - 1], [operator, population, bql]))
    else:
      self._bql.write(text)

  LETTER = Plex.Range('azAZ')
  DIGIT = Plex.Range('09')
  UNDERSCORE = Plex.Str('_')

  NAME = (LETTER | UNDERSCORE) + Plex.Rep(LETTER | UNDERSCORE | DIGIT)

  LINE_COMMENT = Plex.Str('//') + Plex.Rep(Plex.AnyBut('\n'))
  WHITESPACE = Plex.Any(' \f\n\r\t')

  LEXICON = Plex.Lexicon([
    (LINE_COMMENT,              Plex.IGNORE),
    (WHITESPACE,                Plex.IGNORE),
    (Plex.Str('('),             Plex.Begin('1')),
    Plex.State('1', [
      (LINE_COMMENT,            Plex.IGNORE),
      (WHITESPACE,              Plex.IGNORE),
      (NAME,                    _scan_population_name),
    ]),
    Plex.State('2', [
      (LINE_COMMENT,            Plex.IGNORE),
      (WHITESPACE,              Plex.IGNORE),
      (Plex.Str(')'),           Plex.Begin('3')),
    ]),
    Plex.State('3', [
      (LINE_COMMENT,            Plex.IGNORE),
      (WHITESPACE,              Plex.IGNORE),
      (Plex.Str('{'),           _scan_bql_start),
    ]),
    Plex.State('4', [
      (Plex.Str('}'),                   _scan_bql_maybe_end),
      (Plex.Rep1(Plex.AnyBut('}')),     _scan_bql_body),
    ]),
  ])


class VentureBQL(subscanner.Scanner):
  def __init__(self):
    super(VentureBQL, self).__init__(VentureBQLScanner)

# XXX Distinguish me!
class VentureMML(VentureBQL):
  pass
