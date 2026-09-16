import csv
import json
import urllib.request

# independent recomputation (no shared code with Q1.py)
airports = json.loads(urllib.request.urlopen('http://localhost:3000/airports').read())
flights = json.loads(urllib.request.urlopen('http://localhost:3000/flights').read())
iwtf = json.loads(urllib.request.urlopen('http://localhost:3000/iwt_flights').read())

# full graph
nodes = {a['iata'] for a in airports}
edges = set()
for f in flights:
    edges.add(tuple(sorted((f['airport_a'], f['airport_b']))))
deg = {a: 0 for a in nodes}
for a, b in edges:
    deg[a] = deg.get(a, 0) + 1
    deg[b] = deg.get(b, 0) + 1
n = len(nodes)
full = {k: round(v / (n - 1), 6) for k, v in deg.items()}

# iwt graph
iwtnodes = {a['iata'] for a in airports if a['iwt_incidents_observed_count']}
legs = set()
for r in iwtf:
    stops = [r.get('airport_' + c) for c in 'abcde']
    stops = [s for s in stops if s]
    for i in range(len(stops) - 1):
        legs.add((stops[i], stops[i + 1]))
iwt_edges = {tuple(sorted((a, b))) for a, b in legs}
ideg = {a: 0 for a in iwtnodes}
for a, b in iwt_edges:
    ideg[a] = ideg.get(a, 0) + 1
    ideg[b] = ideg.get(b, 0) + 1
nn = len(iwtnodes)
iwt = {k: round(v / (nn - 1), 6) for k, v in ideg.items()}


def load(path):
    with open(path, encoding='utf-8') as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


hdr, rows = load('full_centrality.csv')
assert hdr == ['iata', 'degree_centrality'], hdr
got = {r[0]: float(r[1]) for r in rows}
print('full: file rows', len(rows), '| expected keys', len(full), '| match:', got == full)

hdr, rows = load('iwt_centrality.csv')
got = {r[0]: float(r[1]) for r in rows}
print('iwt: file rows', len(rows), '| expected keys', len(iwt), '| match:', got == iwt)


def sorted_ok(rows):
    vals = [(-float(r[1]), r[0]) for r in rows]
    return vals == sorted(vals)


_, r_full = load('full_centrality.csv')
_, r_iwt = load('iwt_centrality.csv')
print('full sorted correctly:', sorted_ok(r_full))
print('iwt sorted correctly:', sorted_ok(r_iwt))

hdr, rows = load('cleaned_iwt.csv')
exp = sorted(legs)
print('cleaned_iwt: file rows', len(rows), '| expected', len(exp),
      '| header ok:', hdr == ['iata_a', 'iata_b'],
      '| content match:', [tuple(r) for r in rows] == exp)

print()
print('full top 5:', r_full[:5])
print('iwt top 5:', r_iwt[:5])
print('iwt nodes:', nn, '| iwt unique undirected edges:', len(iwt_edges), '| directed legs:', len(legs))
