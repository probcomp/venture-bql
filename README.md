A example of using the VentureScript extensible syntax mechanism to embed MML and BQL.

- The resulting embedding is used (on a trivial example) in test.sh.

- `bayesdb.py` implements the Venture SPs that talk to BayesDB.

- `bql.py` implements the shims needed to parse BQL and MML statements
  in the context of an external VentureScript parser, and the language
  extension objects needed to make the VentureScript parser invoke them.

- `plugin.py` is a Venture plugin that registers the SPs and languages
  from `bayesdb.py` and `bql.py` with Venture.
