#!/usr/bin/env python

import graphgen
import numpy as np

print "size\tdistance\tstddev"

for sz in range(5, 1001):
    avg_dist = []
    for seed in range(10):
        dist = 0
        size = 0
        graph = graphgen.create_graph(sz, 0, seed)
        for a in graph.edge.values():
            for props in a.values():
                dist += props['distance']
                size += 1
        try:
            avg_dist.append(dist / size)
        except ZeroDivisionError:
            pass
    
    print "%d\t%f\t%f" % (sz, np.mean(avg_dist), np.std(avg_dist))
