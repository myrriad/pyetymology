import warnings
from typing import Tuple, List

from pyetymology import wikt_api as ety, etyobjects
import networkx as nx #rumored to be slow, but I'm just using it temporarily


from pyetymology.etyobjects import Originator

#https://iconscout.com/blog/15-classic-color-scheme-generators-to-pick-the-perfect-palette

# online = True
from pyetymology.tests import test_


def mainloop(test_queries:List[Tuple[str, str]] = None):
    original_query = ""  # lleno#Spanish"#llenar#Spanish"#"conflate#English"#"llegar#Spanish"#"Reconstruction:Proto-Italic/feiljos#"
    etyobjects.reset_global_o_id()  # TODO: avoid global state in Originator
    test_fetch_idx = 0
    _EXIT = object()
    def test_safe_query(original_query):
        nonlocal test_fetch_idx
        nonlocal test_queries
        nonlocal _EXIT
        if test_queries:
            if test_fetch_idx >= len(test_queries):
                return _EXIT
            _q1 = test_.fetch_query(*test_queries[test_fetch_idx])
            test_fetch_idx += 1
        else:
            _q1 = ety.query(original_query)
        return _q1

    #_q1 = test_safe_query(original_query)
    #if _q1 is _EXIT:  # exit condition
    #    return None
    #GG = ety.graph(_q1)
    #ety.draw_graph(GG)
    #_ = [print(x) for x in GG.nodes]
    GG = None
    total_queries = 0
    while True:
        assert True
        _Q = test_safe_query("") # ask for another query from the user
        total_queries += 1
        if _Q is _EXIT:  # exit condition
            return GG

        query_origin = _Q.origin
        if GG:
            GG_origin = ety.contains_originator(GG, query_origin)
        else:
            GG_origin = None
        # We want to connect these two graphs,
        # so we take our query's origin and try to find
        # a node from our big, working tree GG.

        G = ety.graph(_Q, replacement_origin=GG_origin)
        ety.draw_graph(G, pause=True)
        _ = [print(x) for x in G.nodes]

        if GG_origin:
            # good, we found a connection
            # fuse the graphs, which should now be connected because we fused and forced our tree G to use a preexisting origin.
            GG2 = nx.compose(GG, G)
        else:
            if total_queries != 1:  # warn unconnected queries, unless it's the initial query in which it's OK
                warnings.warn("Unconnected query " + str(_Q.origin))
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
        ety.draw_graph(GG2)
        GG = GG2

    # TODO: Offline mode using a dump at https://dumps.wikimedia.org/enwiktionary/

if __name__ == "__main__":
    mainloop()

