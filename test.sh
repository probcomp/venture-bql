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

go <<EOF
load_plugin plugin.py
assume pop = bayesdb_population("foo.bdb")
define rows = run(sample bayesdb_bql(pop, "select * from sqlite_master"))
print(rows)
EOF

go <<EOF
load_plugin plugin.py
assume pop = bayesdb_population("foo.bdb")
assume rows = @bql (pop) { select * from sqlite_master; };
print(sample rows)
EOF

# print(sample rows)
# //define rows = run(sample bayesdb_bql(pop, "select * from sqlite_master"))
# //define begin = proc(x, y) { y() }
# //for_each(rows, proc(row) {
# //  begin(print("row:"), proc() {
# //    for_each(row, proc(value) {
# //      begin(print(" "), proc() { print(value) })
# //    })
# //  })
# //})

