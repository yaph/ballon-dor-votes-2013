# -*- coding: utf-8 -*-
# Manual preprocessing
#
# Removed page numbers from extracted text and put "St. Vincent and the
# Grenadines" on one line.

import networkx as nx
from collections import defaultdict
import unicodecsv as csv

G = nx.DiGraph()
nodemap = {}
edges = []
records = []
gexf = 'ballon-dor-votes-2013.gexf'


def add_edge(source, target, weight):
    global edges
    # skip 'no vote' values
    if 'no vote' != target:
        edges.append((source, target, {'weight': weight}))


with open('votesraw.txt', 'r') as f:
    content = f.read()


headings = ['Vote', 'Country', 'Name', 'First (5 points)', 'Second (3 points)', 'Third (1 point)']
cols = defaultdict(list)
pages = content.split(headings[0])
for p in pages:
    if '' == p:
        continue

    text = p.decode('utf-8')
    lines = filter(None, text.split('\n'))[5:]  # omit headings

    while lines:
        records.append(lines[:6])
        lines = lines[6:]

for r in records:
    voter = r[2]
    # fix zlatanera caused by messed up data source Ibrahimovic´ Zlatan
    if voter.startswith('Ibrahimovic') and voter.endswith('Zlatan'):
        voter = 'Ibrahimovic Zlatan'
    nodemap[voter] = {
        'category': r[0],
        'votes': '|'.join(r[3:])
    }
    add_edge(voter, r[3], 5)
    add_edge(voter, r[4], 3)
    add_edge(voter, r[5], 1)

for e in edges:
    voter = e[0]
    target = e[1]
    G.add_node(voter, nodemap[voter])
    if target not in nodemap:
        nodemap[target] = {'category': 'Player'}
        G.add_node(target, nodemap[target])
    G.add_edge(voter, target, e[2])

# write graph file and csv
records.insert(0, headings)
nx.write_gexf(G, gexf, encoding='utf-8', version='1.2draft')
with open('ballon-dor-male-players-votes-2013.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(records)