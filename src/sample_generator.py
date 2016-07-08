# -*- coding: utf-8 -*-
import csv
import json

from numpy.random import choice

PANEL = 'b'
ATTR_FILE = 'data/attribute_panel_{}.json'.format(PANEL)
SAMPLE_FILE = 'data/sample_panel_{}{}.csv'

with open(ATTR_FILE) as attr_json:
    attr = json.load(attr_json)

for k in attr:
    sample_count = sum(attr[k].itervalues())
    for a in attr[k]:
        attr[k][a] = float(attr[k][a]) / sample_count

for p in range(1, 5):
    samples = []
    for i in range(int(sample_count * 1.1)):
        s = {a: choice(attr[a].keys(), p=attr[a].values()).encode('utf-8') for a in attr}
        s['ID'] = i
        s['Panel'] = str(p) + PANEL
        samples.append(s)

    sample_file = SAMPLE_FILE.format(p, PANEL)
    with open(sample_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['ID'] + attr.keys() + ['Panel'])
        writer.writeheader()
        for s in samples:
            writer.writerow(s)

