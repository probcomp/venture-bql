# -*- coding: utf-8; python-indent-offset: 2 -*-

from bayesdb import BAYESDB_SPS
from bql import VentureBQL
from bql import VentureMML
from bql import mk_venture_sql_scanner

def __venture_start__(ripl):
  for name, sp in BAYESDB_SPS:
    ripl.bind_foreign_sp(name, sp)
    ripl.bind_foreign_inference_sp(name, sp)
  ripl.register_language('bql', VentureBQL)
  ripl.register_language('mml', VentureMML)
  ripl.register_language('sql', mk_venture_sql_scanner)
