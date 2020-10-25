from grandalf.graphs import Vertex,Edge,Graph,graph_core
V = [Vertex(data) for data in range(10)]
X = [(0,1),(0,2),(1,3),(2,3),(4,0),(1,4),(4,5),(5,6),(3,6),(3,7),(6,8),(7,8),(8,9),(5,9)]
E = [Edge(V[v],V[w]) for (v,w) in X]
g = Graph(V,E)
print([v.data for v in g.path(V[1],V[9])])
g.add_edge(Edge(V[9],Vertex(10)))
g.remove_edge(V[5].e_to(V[9]))
print([v.data for v in g.path(V[1],V[9])])
g.remove_vertex(V[8])
print(g.path(V[1],V[9]))
for e in g.C[1].E(): print("%s -> %s"%(e.v[0].data,e.v[1].data))
from grandalf.layouts import SugiyamaLayout
class defaultview(object):
    w,h = 10,10
for v in V: v.view = defaultview()
sug = SugiyamaLayout(g.C[0])
sug.init_all(roots=[V[0]],inverted_edges=[V[4].e_to(V[0])])
print("..draw..")
sug.draw()
for v in g.C[0].sV: print("%s: (%d,%d)"%(v.data,v.view.xy[0],v.view.xy[1]))

for l in sug.layers:
    for n in l: print(n.view.xy,end='')
    print('')
for e,d in sug.ctrls.items():
    print('long edge %s --> %s points:'%(e.v[0].data,e.v[1].data))
    for r,v in d.items(): print("%s %s %s"%(v.view.xy,'at rank',r))