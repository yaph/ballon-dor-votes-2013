# -*- coding: utf-8 -*-
import json, itertools, re
import networkx as nx
from collections import defaultdict

G = nx.DiGraph()
nodemap = {}
edges = []
gexf = 'ballon-dor-votes-2012.gexf'
re_pagenum = re.compile(r'\d+/\d+')

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
    if '' == p: continue
    text = p.decode('utf-8')
    for i, h in enumerate(headings[1:]):
        fields = text.split(h)
        col = fields[0].strip('\n')
        values = col.split('\n')
        # remove page num from 1st col
        last = values[-1]
        if re_pagenum.match(last):
            values.pop()
        cols[headings[i]] += values
        text = fields[1]
    cols[headings[-1]] += text.strip('\n').split('\n')

records = zip(*[cols[h] for h in headings])
for r in records:
    voter = r[2]
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

nx.write_gexf(G, gexf, encoding='utf-8', version='1.2draft')
