import networkx as nx
from networkx.classes.reportviews import NodeView, EdgeView


class GraphIdentifier:
    def __init__(self, nodes: NodeView, edges: EdgeView):
        self.nodes = sorted(str(n) for n in nodes)
        self.edges = sorted(str(e) for e in nodes)
def graph2id(G: nx.DiGraph) -> str:
    id = GraphIdentifier(G.nodes, G.edges)



