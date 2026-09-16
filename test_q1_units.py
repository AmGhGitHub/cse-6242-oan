"""Unit tests for Q1 Graph class and helper functions."""
import sys
sys.path.insert(0, r"d:\CodingProjects\cse-6242-oan\hw\Q1")
from Q1 import Graph, clean_trafficking_paths

# --- add_node dedup ---
g = Graph()
g.add_node('HKG', 'Hong Kong International Airport')
g.add_node('HKG', 'Duplicate Hong Kong')
g.add_node('ADD', 'Addis Ababa')
g.add_node('JFK', 'John F. Kennedy')
assert g.nodes == [('HKG', 'Hong Kong International Airport'), ('ADD', 'Addis Ababa'), ('JFK', 'John F. Kennedy')], g.nodes

# --- add_edge undirected dedup ---
g.add_edge('HKG', 'ADD')
g.add_edge('ADD', 'HKG')      # same undirected edge, must be ignored
g.add_edge('HKG', 'JFK')
assert g.edges == [('HKG', 'ADD'), ('HKG', 'JFK')], g.edges

# --- degree_centrality: N=3 nodes, HKG degree 2 -> 2/2=1.0; ADD/JFK degree 1 -> 0.5
c = g.degree_centrality()
assert c == {'HKG': 1.0, 'ADD': 0.5, 'JFK': 0.5}, c

# --- airports appearing only as edge endpoints are included ---
g2 = Graph()
g2.add_node('A', 'Alpha')
g2.add_node('B', 'Bravo')
g2.add_edge('A', 'Z')   # Z is not a node but must get a score; N=2 -> denominator 1
c2 = g2.degree_centrality()
assert c2 == {'A': 1.0, 'B': 0.0, 'Z': 1.0}, c2

# --- degree 0 node included ---
g3 = Graph()
g3.add_node('A', 'Alpha')
g3.add_node('B', 'Bravo')
g3.add_node('C', 'Charlie')
g3.add_edge('A', 'B')
assert g3.degree_centrality() == {'A': 0.5, 'B': 0.5, 'C': 0.0}

# --- clean_trafficking_paths ---
# docstring examples
assert clean_trafficking_paths([['JNB', 'DOH', 'KUL', None, None]]) == [('DOH', 'KUL'), ('JNB', 'DOH')]
assert clean_trafficking_paths([['HKG', 'CAN', None, None, None]]) == [('HKG', 'CAN')]
# PDF examples
assert clean_trafficking_paths([['CPH', 'VIE', None, None, None]]) == [('CPH', 'VIE')]
assert clean_trafficking_paths([['LAX', 'DTW', 'IST', 'PVG', None]]) == [('DTW', 'IST'), ('IST', 'PVG'), ('LAX', 'DTW')]
# dedup across itineraries; (A,B) and (B,A) are distinct
res = clean_trafficking_paths([['A', 'B', None, None, None], ['A', 'B', 'C', None, None], ['B', 'A', None, None, None]])
assert res == [('A', 'B'), ('B', 'A'), ('B', 'C')], res
# empty strings ignored (values after gaps are still stops)
assert clean_trafficking_paths([['A', 'B', '', None, 'C']]) == [('A', 'B'), ('B', 'C')]
# sorting: by first then second
res = clean_trafficking_paths([['Z', 'A'], ['A', 'Z'], ['A', 'B']])
assert res == [('A', 'B'), ('A', 'Z'), ('Z', 'A')], res

print("All unit tests passed.")
