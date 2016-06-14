# -*- Mode: Python; coding: utf-8; python-indent-offset: 2 -*-

import Queue
import StringIO
import threading

import bayeslite

from bayeslite.parse import bql_string_complete_p

import venture.plex as Plex
import venture.value.dicts as vv

class VentureBQLScanner(Plex.Scanner):
  def __init__(self, stream):
    Plex.Scanner.__init__(self, self.LEXICON, stream)
    self._name = None
    self._name_position = None
    self._bql = StringIO.StringIO()
    self._bql_start = None

  def _scan_population_name(self, text):
    #print 'scan: population name %s @ %s' % (text, self.cur_pos)
    self._name = text
    self._name_position = [self.cur_pos, self.cur_pos + len(text) - 1]
    self.begin('2')

  def _scan_bql_start(self, text):
    #print 'scan: bql start @ %s' % (self.cur_pos,)
    self._bql_start = self.cur_pos
    self.begin('4')

  def _scan_bql_body(self, text):
    #print 'scan: bql body @ %s' % (self.cur_pos,)
    self._bql.write(text)

  def _scan_bql_maybe_end(self, text):
    assert text == '}'
    #print 'scan: bql maybe end @ %s' % (self.cur_pos,)
    if bql_string_complete_p(self._bql.getvalue()):
      #print 'end!!!'
      def located(loc, value):
        # XXX Refer to Venture's definition.
        return {'loc': loc, 'value': value}
      operator = located([0, self.cur_pos - 1], vv.symbol('bayesdb_bql'))
      population = located(self._name_position, vv.symbol(self._name))
      bql = located(
        [self._bql_start, self.cur_pos - 1],
        vv.string(self._bql.getvalue()))
      self.produce(located([0, self.cur_pos - 1], [operator, population, bql]))
      #print 'scan: produced and done'
    else:
      #print 'scan: incomplete: %r' % (self._bql.getvalue())
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

HUNGRY_TOKEN = ['hungry']
DEAD_CHAR = ['dead']

class Dead:
  pass

class Reader(object):
  def __init__(self, char_queue, token_queue):
    self._char_queue = char_queue
    self._token_queue = token_queue

  def read(self, _n):
    #print 'reader: put hungry'
    self._token_queue.put(HUNGRY_TOKEN)
    #print 'reader: get char'
    char = self._char_queue.get()
    #print 'reader: got char %r' % (char,)
    if char is DEAD_CHAR:
      #print 'reader: dead and done'
      raise Dead
    return char

def _scan_bql_thread(char_queue, token_queue):
  try:
    reader = Reader(char_queue, token_queue)
    scanner = VentureBQLScanner(reader)
    #print 'scanner: read'
    token, _text = scanner.read()
    #print 'scanner: read %r, putting' % (token,)
    token_queue.put(token)
    #print 'scanner: put and done'
  except Dead:
    #print 'scanner: dead'
    pass

class VentureBQL(object):
  def __init__(self):
    char_queue = Queue.Queue()
    token_queue = Queue.Queue()
    self._thread = threading.Thread(
      target=_scan_bql_thread, args=(char_queue, token_queue))
    self._char_queue = char_queue
    self._token_queue = token_queue

    self._thread.start()
    #print 'bql init: get token'
    token = self._token_queue.get()
    #print 'bql init: got token %r' % (token,)
    assert token is HUNGRY_TOKEN

  def __del__(self):
    if self._thread is not None:
      #print 'bql del: put dead'
      self._char_queue.put(DEAD_CHAR)
      #print 'bql del: join'
      self._thread.join()
      #print 'bql del: joined'
      self._thread = None

  def __call__(self, text):
    #print 'bql call: put char'
    self._char_queue.put(text)
    #print 'bql call: get token'
    token = self._token_queue.get()
    #print 'bql call: got token %r' % (token,)
    if token is HUNGRY_TOKEN:
      return False, None
    else:
      #print 'bql call: join'
      self._thread.join()
      #print 'bql call: joined'
      self._thread = None
      return True, token
