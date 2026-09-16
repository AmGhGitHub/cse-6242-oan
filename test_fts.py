import sqlite3

print('SQLite version:', sqlite3.sqlite_version)
con = sqlite3.connect(':memory:')
con.execute('CREATE VIRTUAL TABLE t USING fts5(content)')
tests = {
    'a': 'one dead sunda pangolin here',      # 1 token between
    'b': 'one dead a b pangolin here',        # 2 tokens between
    'c': 'one dead a b c pangolin here',      # 3 tokens between
    'd': 'one pangolin x dead here',          # 1 token between, reversed order
    'e': 'one pangolin x y dead here',        # 2 between reversed
    'f': 'deadliest pangolin',                # substring, should not match
}
for k, v in tests.items():
    con.execute('INSERT INTO t(content) VALUES (?)', (v,))

queries = [
    '"dead" NEAR/2 "pangolin"',
    'NEAR(dead pangolin, 2)',
    'dead NEAR/2 pangolin',
    'NEAR("dead" "pangolin", 2)',
]
for q in queries:
    try:
        rows = con.execute('SELECT rowid, content FROM t WHERE t MATCH ? ORDER BY rowid', (q,)).fetchall()
        print(repr(q), '->', [r[0] for r in rows])
    except Exception as e:
        print(repr(q), '-> ERROR:', e)
