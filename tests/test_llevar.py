from typing import List

import dill

import networkx as nx
import networkx.algorithms.isomorphism as iso
import pytest
from _pytest import monkeypatch
from mwparserfromhell.wikicode import Wikicode

from pyetymology import wikt_api as wx
from pyetymology.etyobjects import MissingException
from pyetymology.tests import assets, asset_llevar
import mwparserfromhell as mwp

from pyetymology.tests.test_ import fetch_resdom, fetch_query, fetch_wikitext, are_graphs_equal, patch_multiple_input


G_llevaron = nx.DiGraph()
nx.add_path(G_llevaron, ['$0L{es-verb form of|Spanish|llevar}', 'llevaron#Spanish$0'])
G_llevar = nx.DiGraph()
nx.add_path(G_llevar, ['$0{m|Latin|levō}', '$0{inh|Latin|levāre}', '$0{inh|Old Spanish|levar}', 'llevar#Spanish$0'])

class TestLlevar:
    # https://en.wiktionary.org/wiki/llevar
    def test_all_lang_sections(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "dummy_input")

        res, dom = fetch_resdom("llevar", redundance=True)
        sections = list(wx.all_lang_sections(dom, flat=False)) #type: List[List[Wikicode]]
        assert len(sections) == 2
        catalan = sections[0][0]
        spanish = sections[1][0]

        catalantxt = asset_llevar.catalan_txt
        spanishtxt = asset_llevar.spanish_txt

        assert str(catalan) == catalantxt
        assert str(spanish) == spanishtxt

        sections = list(wx.all_lang_sections(dom, flat=True)) #type: List[List[Wikicode]]
        assert len(sections) == 2
        catalan = sections[0]
        spanish = sections[1]
        assert str(catalan) == catalantxt
        assert str(spanish) == spanishtxt

        res, dom = fetch_resdom("llevar", redundance=False)
        sections = list(wx.all_lang_sections(dom)) #type: List[List[Wikicode]] # This has been changed, b/c the removal of antiredundance
        assert len(sections) == 2
        catalan = sections[0]
        spanish = sections[1]
        assert str(catalan) == '==Catalan==\n\n'
        assert str(spanish) == '==Spanish==\n\n'

    def test_section_detect(self):
        res, dom = fetch_resdom("llevar", redundance=True)
        secs = list(wx.sections_by_level(dom, 3))
        assert secs == [['===Etymology===\nFrom {{inh|ca|la|levāre}}, present active infinitive of {{m|la|levō}}.\n\n'],
                        ['===Pronunciation===\n* {{ca-IPA}}\n\n'],
                        ['===Verb===\n{{ca-verb}}\n\n# to [[remove]], to [[take out]]\n\n====Conjugation====\n{{ca-conj-ar|llev}}\n\n====Derived terms====\n* {{l|ca|llevaneu}}\n* {{l|ca|llevar-se}}\n\n',
                            '====Conjugation====\n{{ca-conj-ar|llev}}\n\n',
                            '====Derived terms====\n* {{l|ca|llevaneu}}\n* {{l|ca|llevar-se}}\n\n'],
                        ['===Further reading===\n* {{R:IEC2}}\n* {{R:GDLC}}\n* {{R:DNV}}\n* {{R:DCVB}}\n\n----\n\n']]
    def test_flat_dom(self):
        res, dom = fetch_resdom("llevar", redundance=False)
        secs = list(wx.sections_by_level(dom, 3))
        assert secs == [['===Etymology===\nFrom {{inh|ca|la|levāre}}, present active infinitive of {{m|la|levō}}.\n\n'],
                        ['===Pronunciation===\n* {{ca-IPA}}\n\n'],
                        ['===Verb===\n{{ca-verb}}\n\n# to [[remove]], to [[take out]]\n\n',
                         '====Conjugation====\n{{ca-conj-ar|llev}}\n\n',
                         '====Derived terms====\n* {{l|ca|llevaneu}}\n* {{l|ca|llevar-se}}\n\n'],
                        ['===Further reading===\n* {{R:IEC2}}\n* {{R:GDLC}}\n* {{R:DNV}}\n* {{R:DCVB}}\n\n----\n\n']]


# [['===Etymology===\nFrom {{inh|ca|la|levāre}}, present active infinitive of {{m|la|levō}}.\n\n'], ['===Pronunciation===\n* {{ca-IPA}}\n\n'], ['===Verb===\n{{ca-verb}}\n\n# to [[remove]], to [[take out]]\n\n', '====Conjugation====\n{{ca-conj-ar|llev}}\n\n', '====Derived terms====\n* {{l|ca|llevaneu}}\n* {{l|ca|llevar-se}}\n\n'], ['===Further reading===\n* {{R:IEC2}}\n* {{R:GDLC}}\n* {{R:DNV}}\n* {{R:DCVB}}\n\n----\n\n']]
    def test_auto_lang(self, monkeypatch):
        res, dom = fetch_resdom("llevar", redundance=True)
        monkeypatch.setattr('builtins.input', lambda _: "Spanish")

        v = (list1 := wx.auto_lang(dom, "unused#unused", "arbitrary", "")) == \
            (list2 := (list(wx.sections_by_lang(dom, "Spanish")), "arbitrary#Spanish", "arbitrary", "Spanish"))
        assert v

        monkeypatch.setattr('builtins.input', lambda _: "Catalan")

        v = (list1 := wx.auto_lang(dom, "unused#unused", "arbitrary", "")) == \
            (list2 := (list(wx.sections_by_lang(dom, "Catalan")), "arbitrary#Catalan", "arbitrary", "Catalan"))
        assert v

    def test_auto_lang_failure(self, monkeypatch):

        res, dom = fetch_resdom("llevar", redundance=True)
        monkeypatch.setattr('builtins.input', lambda _: "English")
        with pytest.raises(MissingException) as e_info:
            v = (list1 := wx.auto_lang(dom, "unused#unused", "arbitrary", "")) == \
                (list2 := (list(wx.sections_by_lang(dom, "Spanish")), "arbitrary#Spanish", "arbitrary", "Spanish"))

        assert e_info.value.G is None
        assert e_info.value.missing_thing == "language_section"


    def test_graph(self, monkeypatch):
        # monkeypatch.setattr('builtins.input', lambda _: "1") #Multiple Definitions
        query, wres, origin = fetch_query("llevar", "Spanish")
        # TODO: investigate the effect of flattening on this line
        G, origin = wx.graph(query, wres, origin, "test-temp-1", "test-temp-2")
        global G_llevar
        G2 = G_llevar
        assert nx.is_isomorphic(G, G2)

        assert [repr(s) for s in G.nodes] == [s for s in reversed(list(G2.nodes))] # nx reversed the nodes for some reason
        assert [(repr(l), repr(r)) for l, r in G.edges] == [e for e in reversed(list(G2.edges))]
    # G: {llevar#Spanish$0: {}, $0{inh|Old Spanish|levar}: {llevar#Spanish$0: {}}, $0{inh|Latin|levāre}: {$0{inh|Old Spanish|levar}: {}}, $0{m|Latin|levō}: {$0{inh|Latin|levāre}: {}}}
    # edges: [($0{inh|Old Spanish|levar}, llevar#Spanish$0), ($0{inh|Latin|levāre}, $0{inh|Old Spanish|levar}), ($0{m|Latin|levō}, $0{inh|Latin|levāre})]
    # nodes: [llevar#Spanish$0, $0{inh|Old Spanish|levar}, $0{inh|Latin|levāre}, $0{m|Latin|levō}]

    def test_lemma_llevaron(self):
        query, wres, origin = fetch_query("llevaron", "Spanish")
        G, origin = wx.graph(query, wres, origin, "test-temp-1", "test-temp-2")
        global G_llevaron
        G2 = G_llevaron # this is the repr() version of each node
        assert nx.is_isomorphic(G, G2)

        assert [repr(s) for s in G.nodes] == [s for s in reversed(list(G2.nodes))] # nx reversed the nodes for some reason
        assert [(repr(l), repr(r)) for l, r in G.edges] == [e for e in reversed(list(G2.edges))]

    def test_connection(self, monkeypatch):
        # patch_multiple_input(monkeypatch, ["llevaron, llevar"]) # TODO: this actually isn't used

        fetched_query = fetch_query("llevaron", "Spanish")
        fetched_query = (*fetched_query, "test-temp-1", "test-temp-2")
        GG, origin = wx.graph(*fetched_query)
        # wx.draw_graph(GG, origin)
        # _ = [print(x) for x in GG.nodes]
        #while not original_query:  # if original query is "", then keep repeating it
        #    assert True
        if True:
            _query = fetch_query("llevar", "Spanish") # accept one input
            _query = *_query, "ooga", "booga" # TODO: fetch_query() doesn't return the last 2 values of query()
            _, _, query_origin, _, _ = _query  # extract from origin of query from variable scope dump.
            # TODO: fetch_query() and query() have different footprints
            # TODO: fetch_query() doesn't return the last 2 values of query()
            GG_origin = wx.contains_originator(GG, query_origin)

            # See main.py on connection
            G, origin = wx.graph(*_query, replacement_origin=GG_origin)
            # ety.draw_graph(G, origin)
            assert GG_origin # llevaron should contain llevar

            global G_llevaron
            assert are_graphs_equal(GG, G_llevaron)

            G_llevar_with_rorigin = nx.DiGraph()
            nx.add_path(G_llevar_with_rorigin, ['$0{m|Latin|levō}', '$0{inh|Latin|levāre}', '$0{inh|Old Spanish|levar}', '$0L{es-verb form of|Spanish|llevar}'])
            assert are_graphs_equal(G, G_llevar_with_rorigin)

            # fuse the graphs, which should now be connected because we fused and forced our tree G to use a preexisting origin.
            GG2 = nx.compose(GG, G)
            G_composed = nx.DiGraph()
            nx.add_path(G_composed, ['$0{m|Latin|levō}', '$0{inh|Latin|levāre}', '$0{inh|Old Spanish|levar}', '$0L{es-verb form of|Spanish|llevar}', 'llevaron#Spanish$0'])

            # wx.draw_graph(G_composed) # DID: this fails. Why? Answer: blank node_colors.
            # wx.draw_graph(GG2)
            assert True
            assert are_graphs_equal(GG2, G_composed)
            # TODO: origin indexing is broken with lemmas
# [$0L{es-verb form of|Spanish|llevar}, $0{inh|Old Spanish|levar}, $0{inh|Latin|levāre}, $0{m|Latin|levō}]
# GG2.nodes [llevaron#Spanish$0, $0L{es-verb form of|Spanish|llevar}, $0{inh|Old Spanish|levar}, $0{inh|Latin|levāre}, $0{m|Latin|levō}]
# G_composed.nodes ['$0{m|Latin|levō}', '$0{inh|Latin|levāre}', '$0{inh|Old Spanish|levar}', '$0L{es-verb form of|Spanish|llevar}', 'llevaron#Spanish$0']


