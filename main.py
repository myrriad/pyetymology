import warnings


from pyetymology import wikt_api as ety
import networkx as nx #rumored to be slow, but I'm just using it temporarily


from pyetymology.etyobjects import Originator

#https://iconscout.com/blog/15-classic-color-scheme-generators-to-pick-the-perfect-palette

# online = True



original_query = "" #lleno#Spanish"#llenar#Spanish"#"conflate#English"#"llegar#Spanish"#"Reconstruction:Proto-Italic/feiljos#"


GG, origin = ety.graph(*ety.query(original_query))
ety.draw_graph(GG, origin)
_ = [print(x) for x in GG.nodes]
while not original_query: # if original query is "", then keep repeating it
    assert True
    _query = ety.query(original_query) # parse the query
    _, _, query_origin, _, _ = _query # extract from origin of query from variable scope dump
    GG_origin = ety.contains_originator(GG, query_origin)
    # We want to connect these two graphs,
    # so we take our query's origin and try to find
    # a node from our big, working tree GG.

    G, origin = ety.graph(*_query, replacement_origin=GG_origin)
    ety.draw_graph(G, origin)

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
    common_link = ety.contains_originator(GG, origin)
    GG2 = nx.compose(GG, G)
    if common_link:
        GG2.add_edge(origin, common_link)
    else:
        raise Exception("Unconnected query " + origin)
    """
    _ = [print(x) for x in GG.nodes]
    ety.draw_graph(GG2, origin)
    GG = GG2

# TODO: Offline mode using a dump at https://dumps.wikimedia.org/enwiktionary/


