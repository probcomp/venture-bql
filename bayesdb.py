# -*- Mode: Python; coding: utf-8; python-indent-offset: 2 -*-

import bayeslite

import venture.lite.psp as psp
import venture.lite.sp_help as sp
import venture.lite.types as t
import venture.lite.value as vv

class BayesDB_PSP(psp.DeterministicPSP):
  def simulate(self, args):
    pathname = args.operandValues()[0]
    bdb = bayeslite.bayesdb_open(pathname)
    return vv.VentureForeignBlob(bdb)

class MML_PSP(psp.DeterministicPSP):
  def simulate(self, args):
    bdb = args.operandValues()[0].datum
    phrase = args.operandValues()[1]
    if len(args.operandValues()) == 2:
      parameters = args.operandValues()[2].asPythonList()
    else:
      parameters = None
    bdb.execute(phrase, parameters)

class BQL_PSP(psp.DeterministicPSP):
  def simulate(self, args):
    bdb = args.operandValues()[0].datum
    phrase = args.operandValues()[1]
    if len(args.operandValues()) == 3:
      parameters = tuple(venture2bql(x) for x in args.operandValues()[2])
    else:
      parameters = None
    results = bdb.execute(phrase, parameters).fetchall()
    return tuple(bql2venture(x) for row in results for x in row)

def bql2venture(x):
  if isinstance(x, float):
    return vv.VentureNumber(x)
  if isinstance(x, int):
    return vv.VentureInteger(x)
  if isinstance(x, unicode):
    return vv.VentureString(x.encode('UTF-8'))
  if x is None:
    return vv.VentureNil()
  raise ValueError('Unrepresentable value from BQL: %r' % (x,))

def venture2bql(x):
  if isinstance(x, vv.VentureNumber):
    return x.getNumber()
  if isinstance(x, vv.VentureInteger):
    return x.getInteger()
  if isinstance(x, vv.VentureString):
    return unicode(x.getString(), 'UTF-8')
  if isinstance(x, vv.VentureNil):
    return None
  raise ValueError('Unrepresentable value from BQL: %r' % (x,))

BAYESDB_SPS = [
  ('bayesdb_population',
    sp.typed_nr(PopulationPSP(), [t.StringType()], t.AnyType('population'))),
  ('bayesdb_bql',
    sp.typed_nr(BQL_PSP(),
      [t.AnyType('population'), t.StringType(), t.ArrayType()],
      t.ArrayType(),
      min_req_args=2)),
  ('bayesdb_mml',
    sp.typed_nr(MML_PSP(),
      [t.AnyType('population'), t.StringType(), t.ArrayType()],
      t.ArrayType(),
      min_req_args=2)),
]
