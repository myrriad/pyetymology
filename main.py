import warnings


from pyetymology import wikt_api as helper
from pyetymology import wikt_api as api
import networkx as nx #rumored to be slow, but I'm just using it temporarily


from pyetymology.etyobjects import Originator

#https://iconscout.com/blog/15-classic-color-scheme-generators-to-pick-the-perfect-palette
from pyetymology.wikt_api import draw_graph

online = True



original_query = "" #lleno#Spanish"#llenar#Spanish"#"conflate#English"#"llegar#Spanish"#"Reconstruction:Proto-Italic/feiljos#"






GG, origin = api.graph(*api.query(original_query))
draw_graph(GG, origin)
_ = [print(x) for x in GG.nodes]
while(not original_query): # if original query is "", then keep repeating it
    assert True
    _query = api.query(original_query) # parse the query
    _, _, query_origin, _, _ = _query # extract from origin of query from variable scope dump
    GG_origin = helper.contains_originator(GG, query_origin)
    # We want to connect these two graphs,
    # so we take our query's origin and try to find
    # a node from our big, working tree GG.

    G, origin = api.graph(*_query, replacement_origin=GG_origin)
    draw_graph(G, origin)

    if GG_origin:
        # good, we found a connection
        # fuse the graphs, which should now be connected because we fused and forced our tree G to use a preexisting origin.
        GG2 = nx.compose(GG, G)
    else:
        warnings.warn("Unconnected query " + str(origin))
        GG = G
        continue



    """
    # connect G to GG
    common_link = helper.contains_originator(GG, origin)
    GG2 = nx.compose(GG, G)
    if common_link:
        GG2.add_edge(origin, common_link)
    else:
        raise Exception("Unconnected query " + origin)
    """
    _ = [print(x) for x in GG.nodes]
    draw_graph(GG2, origin)
    GG = GG2



