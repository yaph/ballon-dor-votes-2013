# -*- coding: utf-8 -*-
# Create gexf and csv files from raw votes data manually copied from
# http://www.fifa.com/mm/document/ballond%27or/playeroftheyear%28men%29/02/26/02/68/fboaward_menplayer2013_neutral.pdf
# to a txt file.
#
# Text cleanup:
# Remove page numbers and headings from extracted text and put "St. Vincent and the Grenadines" on one line.

import re
import networkx as nx
import unicodecsv as csv

G = nx.DiGraph()
nodemap = {}
edges = []
records = []
gexf = 'ballon-dor-male-players-votes-2013.gexf'


re_pagetitle = re.compile(r"FIFA Ballon d'Or 2013\n")
re_pagenum = re.compile(r'\d+\s*/\s*\d+\n*')
re_vincent = re.compile(r'St. Vincent and the\s+Grenadines')


def add_edge(source, target, weight):
    # skip 'no vote' values
    if 'no vote' == target:
        print(source, target, weight)
        return
    edges.append((source, target, {'weight': weight}))


with open('malevotesraw.txt', 'r') as f:
    content = f.read().strip()

# cleanup text
content = re.sub(re_pagetitle, '', content)
content = re.sub(re_pagenum, '', content)
content = re.sub(re_vincent, 'St. Vincent and the Grenadines', content)

headings = ['Vote',
            'Country',
            'Name',
            'First (5 points)',
            'Second (3 points)',
            'Third (1 point)']

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