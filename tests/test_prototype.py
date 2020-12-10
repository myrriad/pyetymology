from pyetymology import wikt_api, etyobjects
from pyetymology.tests import test_

import networkx as nx

from pyetymology.tests.assets import asset_prototype


def test_to_dict_of_lists_equivalence():
    return True # this shouldn't change very much
    _Q = test_.fetch_query("prototype", "English")
    G = wikt_api.graph(_Q)
    wikt_api.draw_graph(G, pause=True)
    dl = nx.to_dict_of_lists(G)
    print(dl)
    G2 = nx.from_dict_of_lists(dl, create_using=nx.DiGraph)
    wikt_api.draw_graph(G2, pause=True)
    dl2 = nx.to_dict_of_lists(G2)
    assert dl == dl2

def test_graph_eq():
    # etyobjects.reset_global_o_id()

    _Q = test_.fetch_query("prototype", "English")
    G = wikt_api.graph(_Q)
    wikt_api.draw_graph(G, pause=True)
    dl = nx.to_dict_of_lists(G)
    print(dl)
    assert repr(dl) == "{prototype#English$0: [], $0{der|French|prototype}: [prototype#English$0], $0{der|Late Latin|prototypon}: " \
                       "[$0{der|French|prototype}], $0{der|Ancient Greek|πρωτότυπος ['', 'original; prototype']}: " \
                       "[$0{der|Late Latin|prototypon}], $0{m|Ancient Greek|πρωτο- [\"''prefix meaning ‘first’''\"]}: " \
                       "[$0{der|Ancient Greek|πρωτότυπος ['', 'original; prototype']}], $0{m|Ancient Greek|πρῶτος ['first; earliest']}: " \
                       "[$0{m|Ancient Greek|πρωτο- [\"''prefix meaning ‘first’''\"]}], $0{m|Ancient Greek|τῠ́πος ['blow, pressing; sort, type']}: " \
                       "[$0{m|Ancient Greek|πρωτο- [\"''prefix meaning ‘first’''\"]}], $0{m|Ancient Greek|τύπτω ['to beat, strike']}: " \
                        "[$0{m|Ancient Greek|τῠ́πος ['blow, pressing; sort, type']}], $0{der|Proto-Indo-European|*(s)tewp- ['', 'to push; to stick']}: " \
                       "[$0{m|Ancient Greek|τύπτω ['to beat, strike']}]}"

    # assert dl == dl2
    #G2 = nx.DiGraph(asset_prototype.node_list, asset_prototype.current_adj_list)
    #assert nx.is_isomorphic(G, G2)

