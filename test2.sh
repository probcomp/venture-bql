#!/bin/sh

set -Ceu

rm -f sprinkler.bdb
BAYESDB_WIZARD_MODE=1 PYTHONPATH=. ../crosscat/pythenv.sh ../bayeslite/pythenv.sh ../Venturecxx/pythenv.sh venture -L plugin.py -f sprinkler-demo.vnts
