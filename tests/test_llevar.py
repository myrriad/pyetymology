from typing import List

import dill

import networkx as nx
import networkx.algorithms.isomorphism as iso
import pytest
from _pytest import monkeypatch
from mwparserfromhell.wikicode import Wikicode

from pyetymology import wikt_api as wx
from pyetymology.tests import assets, asset_llevar
import mwparserfromhell as mwp

from pyetymology.tests.test_ import fetch_resdom, fetch_query


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
    def test_graph(self, monkeypatch):
        # monkeypatch.setattr('builtins.input', lambda _: "1") #Multiple Definitions
        query, wres, origin = fetch_query("llevar", "Spanish")
        _, wtxt, dom = wres
        wres = None, wtxt, dom
        # TODO: investigate the effect of flattening on this line
        G, origin = wx.graph(query, wres, origin, "test-temp-1", "test-temp-2")
        G2 = nx.DiGraph()
        nx.add_path(G2, ['$0{m|Latin|levō}', '$0{inh|Latin|levāre}', '$0{inh|Old Spanish|levar}', 'llevar#Spanish$0'])
        assert nx.is_isomorphic(G, G2)

        assert [repr(s) for s in G.nodes] == [s for s in reversed(list(G2.nodes))] # nx reversed the nodes for some reason
        assert [(repr(l), repr(r)) for l, r in G.edges] == [e for e in reversed(list(G2.edges))]
    # G: {llevar#Spanish$0: {}, $0{inh|Old Spanish|levar}: {llevar#Spanish$0: {}}, $0{inh|Latin|levāre}: {$0{inh|Old Spanish|levar}: {}}, $0{m|Latin|levō}: {$0{inh|Latin|levāre}: {}}}
    # edges: [($0{inh|Old Spanish|levar}, llevar#Spanish$0), ($0{inh|Latin|levāre}, $0{inh|Old Spanish|levar}), ($0{m|Latin|levō}, $0{inh|Latin|levāre})]
    # nodes: [llevar#Spanish$0, $0{inh|Old Spanish|levar}, $0{inh|Latin|levāre}, $0{m|Latin|levō}]
