from typing import List

import networkx as nx
import grandalf as gf
from grandalf.graphs import Vertex


def pos(G: nx.DiGraph, roots=None, g=None, xspace=20, yspace=20):
    if g is None:
        g = gf.utils.convert_nextworkx_graph_to_grandalf(G)
    V = G.nodes
    E = G.edges
    gc = g.C[0]
    assert gc
    layers = []  # type: List[List[Vertex]]
    roots = [v for v in gc.sV if len(v.e_in()) == 0]  # taken from SugiyamaLayout.init_all()
    layers.append(roots)
    scanning = roots

    while len(scanning) > 0:
        builder = []
        for node in scanning:  # type: Vertex
            builder += node.N(f_io=1)
        layers.append(builder)
        scanning = builder

    dict = {}

    i = j = 0
    for j, layer in enumerate(layers):
        for i, node in enumerate(layer):
            dict[node.data] = (i * xspace, -j * yspace)
    return dict

