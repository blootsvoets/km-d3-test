import networkx as nx
from networkx.readwrite import json_graph

def read_links(g):
    g.add_node('a', id=1)
    g.add_node('b')
    g.add_node('c')
    g.add_node('d')
    g.add_edge('a', 'b')
    g.add_edge('a', 'c')
    g.add_edge('b', 'd')
    g.add_edge('c', 'd')
    g.add_edge('c', 'a')

def create_graph():
    g = nx.DiGraph()
    read_links(g)
    return g

def get_json():
    return json_graph.node_link_data(create_graph())
