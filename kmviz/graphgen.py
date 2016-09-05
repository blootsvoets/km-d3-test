import networkx as nx
from networkx.readwrite import json_graph
import graphlayout
import numpy as np
import sys
import math

def get_json(size, wifisize, seed):
    graph = create_graph(size, wifisize, seed)
    
    nodes = graph.node
    
    fixed_nodes = dict((a, np.array([nodes[a]['x'], nodes[a]['y']]))
                       for a in nodes
                       if nodes[a].get('fixed'))

    pos = graphlayout.layout(graph, fixed_nodes)
    # pos = nx.spring_layout(g, pos=fixed_nodes, fixed=fixed_nodes.keys(), k=0.25*2/3*1/math.sqrt(size / 10.0), iterations=500)
    # pos.update(fixed_nodes)
    nx.set_node_attributes(graph, 'calculated_x', dict((a, pos[a][0]) for a in pos))
    nx.set_node_attributes(graph, 'calculated_y', dict((a, pos[a][1]) for a in pos))
    
    return json_graph.node_link_data(graph)

def create_room():
    return [(0,0), (0,1), (1,1), (1,0)]

def create_points_in_polygon(n, poly, randState):
    xmin, ymin = np.min(poly, axis=0)
    xmax, ymax = np.max(poly, axis=0)
    pts = randState.uniform(low=xmin, high=xmax, size=(n, 2))
    
    for i in range(n):
        while not ispointinside(pts[i], poly):
            pts[i] = randState.uniform(low=xmin, high=xmax, size=2)

    return pts    

def create_wifi(n, room , randState):
    return create_points_in_polygon(n, room, randState)

def create_agents(n, room, randState):
    a = create_points_in_polygon(n, room, randState)
    return [{'id': str(i), 'pt': x} for i, x in enumerate(a)]

def create_graph(size, wifi_size, seed):
    room = create_room()
    agents = create_points_in_polygon(size, room, np.random.RandomState(seed=seed))
    fixed_spots = create_points_in_polygon(wifi_size, room, np.random.RandomState(seed=seed + 5050))
    
    g = nx.DiGraph()
    
    for i in range(size):
        g.add_node(str(i), x = agents[i,0], y = agents[i,1], nodetype = 1)
        dist = np.linalg.norm(agents - agents[i], axis=1)
        for j in range(size):
            if j == i:
                continue
            if dist[j] < 0.25:
                g.add_edge(str(i), str(j), distance = dist[j])

    for i in range(wifi_size):
        a_id = 'wifi%d' % i
        g.add_node(a_id, x=fixed_spots[i,0], y=fixed_spots[i,1], fixed=True, nodetype = 2)
        dist = np.linalg.norm(agents - fixed_spots[i], axis=1)
        for j in range(size):
            if dist[j] < 0.25:
                g.add_edge(a_id, str(j), distance = dist[j])
                g.add_edge(str(j), a_id, distance = dist[j])

    return g

# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.

_eps = 0.00001
_huge = sys.float_info.max
_tiny = sys.float_info.min
 
def rayintersectseg(p, a, b):
    ''' takes a point p=Pt() and an edge of two endpoints a,b=Pt() of a line segment returns boolean
    '''
    if a[1] > b[1]:
        a, b = b, a
    if p[1] == a[1] or p[1] == b[1]:
        p = (p[0], p[1] + _eps)
        
    if p[1] < a[1] or p[1] > b[1] or p[0] > max(a[0], b[0]):
        return False
    if p[0] < min(a[0], b[0]):
        return True
    
    return (b[0] - a[0])*(p[1] - a[1]) >= (p[0] - a[0])*(b[1] - a[1])

def _odd(x):
    return x%2 == 1
 
def ispointinside(p, poly):
    n = len(poly)
    return _odd(sum(rayintersectseg(p, poly[i], poly[(i + 1) % n])
                    for i in range(n) ))
 

def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / float(p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
        p1x,p1y = p2x,p2y
        
    return inside

def test_point_inside(n):
    a = np.empty((n,n), np.bool)
    for i in range(n):
        for j in range(n):
            a[i,j] = ispointinside((4*i/float(n) - 0.5, 4*j/float(n) - 0.5), [(0,0), (0,2), (3,2), (3,1), (2, 1), (2,0)])
    return a