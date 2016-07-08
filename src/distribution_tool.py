# -*- coding: utf-8 -*-
import csv
import json
import itertools

PANEL = '1a'
ATTR_FILE = 'data/attribute.json'
SAMPLE_FILE = 'data/sample_panel_{}.csv'.format(PANEL)
RESULT_FILE = 'data/result_panel_{}.csv'.format(PANEL)
DISTRIBUTION_FILE = 'data/result_distibution_{}.csv'.format(PANEL)

GROUP_COUNT = 8

g_index = range(GROUP_COUNT)
g_samples = {i: [] for i in g_index}

attribute_list = []
with open(ATTR_FILE) as attr_json:
    attr = json.load(attr_json)
    for (k, v) in attr.items():
        attribute_list += map(lambda x: (k, x), v.keys())

with open(SAMPLE_FILE) as csvfile:
    samples = csv.DictReader(csvfile)

    for i, s in enumerate(samples):
        i = i % GROUP_COUNT
        g_samples[i].append(map(lambda (a, b): (a, b.decode('utf-8')), list(s.items())))

def attr_checker(attr, group_a, group_b):
    count_a = len(filter(lambda s: attr in s, group_a))
    count_b = len(filter(lambda s: attr in s, group_b))
    return count_a < count_b + 2 and count_b < count_a + 2

def sample_swapper(group_a, group_b, sample_a, sample_b):
    group_a.remove(sample_a)
    group_b.remove(sample_b)
    group_a.append(sample_b)
    group_b.append(sample_a)


attribute_complete = []
for attr in attribute_list:
    evently = False
    while not evently:
        dist = map(lambda k: (k, len(filter(lambda s: attr in s, g_samples[k]))), g_index)
        g_max, g_max_v = max(dist, key=lambda (k, v): v)
        g_min, g_min_v = min(dist, key=lambda (k, v): v)
        if g_max_v - g_min_v > 1 :
            g_max_list = filter(lambda i: dict(dist)[i] == g_max_v, g_index)
            g_min_list = filter(lambda i: dict(dist)[i] == g_min_v, g_index)
            
            swap = False
            for (g_max, g_min) in itertools.product(g_max_list, g_min_list):
                s_exp_list = filter(lambda s: attr in s, g_samples[g_max])
                s_imp_list = filter(lambda s: attr not in s, g_samples[g_min])
                
                swap = False
                for (s_exp, s_imp) in itertools.product(s_exp_list, s_imp_list):
                    sample_swapper(g_samples[g_min], g_samples[g_max], s_imp, s_exp)
                    if all(map(lambda a: attr_checker(a, g_samples[g_min], g_samples[g_max]), attribute_complete)):
                        swap = True
                        break
                    else:
                        sample_swapper(g_samples[g_min], g_samples[g_max], s_exp, s_imp)

                if swap:
                    break
            if not swap:
                evently = True
        else:
            evently = True
    attribute_complete.append(attr)


with open(RESULT_FILE, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=dict(g_samples[0][0]).keys() + ['Block', 'Order'])
    writer.writeheader()
    for g in g_index:
        for i, s in enumerate(g_samples[g]):
            s = {k: v.encode('utf-8') for (k, v) in s}
            s['Order'] = g * 6 + 1 + i % 6
            s['Block'] = chr(g + 65)
            writer.writerow(s)


with open(DISTRIBUTION_FILE, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['Panel', 'Attribute'] + map(lambda g: 'Block ' + chr(g + 65), g_index))
    writer.writeheader()
    for attr in attribute_complete:
        row = {'Panel': PANEL, 'Attribute': attr[1].encode('utf-8')}
        row.update({'Block ' + chr(g + 65): len(filter(lambda s: attr in s, g_samples[g])) for g in g_index})
        writer.writerow(row)
