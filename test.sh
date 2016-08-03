#!/bin/sh

set -Ceu

go ()
{
    PYTHONPATH=. \
	~/crosscat/master/pythenv.sh \
	~/bayesdb/master/pythenv.sh \
	~/venture/master/pythenv.sh \
	venture ${1+"$@"}
}

# These two example invocations produce the same output

go <<EOF
load_plugin plugin.py
assume bdb = bayesdb_open("foo.bdb")
define rows = run(sample bayesdb_bql(bdb, "select * from sqlite_master"))
print(rows)
EOF

go <<EOF
load_plugin plugin.py
assume bdb = bayesdb_open("foo.bdb")
assume rows = @{bql (bdb) { select * from sqlite_master; }};
print(run(sample rows))
EOF
