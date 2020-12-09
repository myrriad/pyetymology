from typing import List

import dill

import networkx as nx
import networkx.algorithms.isomorphism as iso
import pytest
from _pytest import monkeypatch
from mwparserfromhell.wikicode import Wikicode

from pyetymology import wikt_api as wx, etyobjects
from pyetymology.etyobjects import MissingException
from pyetymology.tests import assets, asset_llevar
import mwparserfromhell as mwp

from pyetymology.tests.assets import asset_llegar
from pyetymology.tests.test_ import fetch_resdom, fetch_query, fetch_wikitext, is_eq__repr, patch_multiple_input

G_llegaron = nx.DiGraph()
nx.add_path(G_llegaron, ['$0L{es-verb form of|Spanish|llegar}', 'llegaron#Spanish$0'])
G_llegar = nx.DiGraph()
nx.add_path(G_llegar, ["$0{der|Proto-Indo-European|*pleḱ- ['', 'to plait, to weave']}", "$0{m|Latin|plicō ['I fold']}",
                       '$0{inh|Latin|plicāre}', 'llegar#Spanish$0'])
class TestLlegar:
    # https://en.wiktionary.org/wiki/llevar
    def test_all_lang_sections(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "Spanish")

        res, dom = fetch_resdom("llegar")
        sections = list(wx.all_lang_sections(dom)) #type: List[List[Wikicode]] # This has been changed, b/c the removal of antiredundance
        assert sections == ['==Asturian==\n\n', '==Catalan==\n\n', '==Old Irish==\n\n', '==Spanish==\n\n']


    def test_graph(self, monkeypatch):
        # monkeypatch.setattr('builtins.input', lambda _: "1") #Multiple Definitions
        etyobjects.reset_global_o_id()
        _Q = fetch_query("llegar", "Spanish")
        G = wx.graph(_Q)
        global G_llegar
        G2 = G_llegar
        assert nx.is_isomorphic(G, G2)

        assert [repr(s) for s in G.nodes] == [s for s in reversed(list(G2.nodes))] # nx reversed the nodes for some reason
        assert [(repr(l), repr(r)) for l, r in G.edges] == [e for e in reversed(list(G2.edges))]
    # G: {llevar#Spanish$0: {}, $0{inh|Old Spanish|levar}: {llevar#Spanish$0: {}}, $0{inh|Latin|levāre}: {$0{inh|Old Spanish|levar}: {}}, $0{m|Latin|levō}: {$0{inh|Latin|levāre}: {}}}
    # edges: [($0{inh|Old Spanish|levar}, llevar#Spanish$0), ($0{inh|Latin|levāre}, $0{inh|Old Spanish|levar}), ($0{m|Latin|levō}, $0{inh|Latin|levāre})]
    # nodes: [llevar#Spanish$0, $0{inh|Old Spanish|levar}, $0{inh|Latin|levāre}, $0{m|Latin|levō}]

    def test_lemma_llegaron(self):
        etyobjects.reset_global_o_id()
        _Q = fetch_query("llegaron", "Spanish")
        G = wx.graph(_Q)
        assert True
        G2 = G_llegaron # this is the repr() version of each node
        assert nx.is_isomorphic(G, G2)

        assert [repr(s) for s in G.nodes] == [s for s in reversed(list(G2.nodes))] # nx reversed the nodes for some reason
        assert [(repr(l), repr(r)) for l, r in G.edges] == [e for e in reversed(list(G2.edges))]

    def test_connection(self, monkeypatch):
        etyobjects.reset_global_o_id()
        # patch_multiple_input(monkeypatch, ["llevaron, llevar"]) # TODO: this actually isn't used

        fetched_Q = fetch_query("llegaron", "Spanish")
        GG = wx.graph(fetched_Q)
        # wx.draw_graph(GG, origin)
        # _ = [print(x) for x in GG.nodes]
        #while not original_query:  # if original query is "", then keep repeating it
        #    assert True
        if True:
            _Q = fetch_query("llegar", "Spanish") # accept one input
            query_origin = _Q.origin  # extract from origin of query from variable scope dump.
            GG_origin = wx.contains_originator(GG, query_origin)

            # See main.py on connection
            G = wx.graph(_Q, replacement_origin=GG_origin)
            # ety.draw_graph(G, origin)
            assert GG_origin # llevaron should contain llevar

            global G_llegaron
            assert is_eq__repr(GG, G_llegaron)

            G_llegar_with_rorigin = nx.DiGraph()
            nx.add_path(G_llegar_with_rorigin,
                        ["$0{der|Proto-Indo-European|*pleḱ- ['', 'to plait, to weave']}", "$0{m|Latin|plicō ['I fold']}",
                         "$0{inh|Latin|plicāre}", "$0L{es-verb form of|Spanish|llegar}"])

            assert is_eq__repr(G, G_llegar_with_rorigin)

            # fuse the graphs, which should now be connected because we fused and forced our tree G to use a preexisting origin.
            GG2 = nx.compose(GG, G)
            G_composed = nx.DiGraph()
            nx.add_path(G_composed, ["$0{der|Proto-Indo-European|*pleḱ- ['', 'to plait, to weave']}",
                                     "$0{m|Latin|plicō ['I fold']}",
                                     '$0{inh|Latin|plicāre}',
                                     '$0L{es-verb form of|Spanish|llegar}',
                                     'llegaron#Spanish$0'])

            # wx.draw_graph(G_composed) # DID: this fails. Why? Answer: blank node_colors.
            # wx.draw_graph(GG2)
            assert is_eq__repr(GG2, G_composed)
            # TODO: origin indexing is broken with lemmas
# [$0L{es-verb form of|Spanish|llevar}, $0{inh|Old Spanish|levar}, $0{inh|Latin|levāre}, $0{m|Latin|levō}]
# GG2.nodes [llevaron#Spanish$0, $0L{es-verb form of|Spanish|llevar}, $0{inh|Old Spanish|levar}, $0{inh|Latin|levāre}, $0{m|Latin|levō}]
# G_composed.nodes ['$0{m|Latin|levō}', '$0{inh|Latin|levāre}', '$0{inh|Old Spanish|levar}', '$0L{es-verb form of|Spanish|llevar}', 'llevaron#Spanish$0']


