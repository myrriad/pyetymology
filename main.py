import warnings
from typing import Tuple, List

from pyetymology import wikt_api as ety, etyobjects
import networkx as nx #rumored to be slow, but I'm just using it temporarily


from pyetymology.etyobjects import Originator

#https://iconscout.com/blog/15-classic-color-scheme-generators-to-pick-the-perfect-palette

# online = True
from pyetymology.tests import test_


def mainloop(test_queries:List[Tuple[str, str]] = None, draw_graphs=True) -> List[nx.DiGraph]:
    original_query = ""  # lleno#Spanish"#llenar#Spanish"#"conflate#English"#"llegar#Spanish"#"Reconstruction:Proto-Italic/feiljos#"
    # etyobjects.reset_global_o_id()  # TODO: avoid global state in Originator
    total_queries = 0
    _EXIT = object()
    retn = []
    def test_safe_query(original_query):
        nonlocal total_queries
        nonlocal test_queries
        nonlocal _EXIT
        if test_queries:
            if total_queries >= len(test_queries):
                return _EXIT
            _q1 = test_.fetch_query(*test_queries[total_queries], query_id=total_queries)
        else:
            _q1 = ety.query(original_query, query_id=total_queries)
        total_queries += 1
        return _q1

    #_q1 = test_safe_query(original_query)
    #if _q1 is _EXIT:  # exit condition
    #    return None
    #GG = ety.graph(_q1)
    #ety.draw_graph(GG)
    #_ = [print(x) for x in GG.nodes]
    GG = None
    while True:
        assert True
        _Q = test_safe_query("") # ask for another query from the user
        if _Q is _EXIT:  # exit condition
            retn.append(GG)
            return retn

        query_origin = _Q.origin
        if GG:
            GG_origin = ety.find_originator_node(GG, query_origin)
        else:
            GG_origin = None
        # We want to connect these two graphs,
        # so we take our query's origin and try to find
        # a node from our big, working tree GG.

        G = ety.graph(_Q, replacement_origin=GG_origin)
        if test_queries:
            retn.append(G)
        if draw_graphs:
            ety.draw_graph(G, pause=True)
        _ = [print(x) for x in G.nodes]

        if GG_origin:

            # good, we found a connection
            # fuse the graphs, which should now be connected because we fused and forced our tree G to use a preexisting origin.
            GG = nx.compose(GG, G)
            if draw_graphs:
                ety.draw_graph(GG)
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




if __name__ == "__main__":
    print("main")
    mainloop(None)

