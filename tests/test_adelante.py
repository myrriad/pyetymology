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

from pyetymology.tests.test_ import fetch_wikitext, fetch_resdom, fetch_query



class TestAdelante:
    def test_all_lang_sections(self):
        res, dom = fetch_resdom("adelante")
        ls = list(wx.all_lang_sections(dom, flat=False)) #type: List[List[Wikicode]]
        sections = ls[0]
        wikicode = sections[0]
        a = str(wikicode)
        b = fetch_wikitext("adelante")
        b = b[b.index("\n")+1:]
        assert len(ls) == 1 # we only got one lang
        assert len(sections) == 1
        assert a == b
        assert a.startswith("==Spanish==")

    def test_all_lang_sections_flat(self):
        res, dom = fetch_resdom("adelante")
        sections = list(wx.all_lang_sections(dom, flat=True)) #type: List[Wikicode]
        spanish = sections[0]
        a = str(spanish)
        b = fetch_wikitext("adelante")[18:]
        assert len(sections) == 1 # we only got one lang
        assert a == b
        assert a.startswith("==Spanish==")

    def test_section_detect(self):
        res, dom = fetch_resdom("adelante")
        secs = list(wx.sections_by_level(dom, 3))
        assert secs == [['===Pronunciation===\n* {{es-IPA}}\n* {{hyph|es|a|de|lan|te}}\n\n'], ['===Etymology 1===\nFrom {{m|es|delante||in front}}.\n\n====Adverb====\n{{es-adv}}\n\n# [[forward]] {{gloss|toward the front}}\n# [[forward]] {{gloss|into the future}}\n\n=====Alternative forms=====\n* {{l|es|alante}} {{q|colloquial}}\n\n====Derived terms====\n{{der3|es\n|adelantar\n|de aquí en adelante\n|en adelante\n|Gran Salto Adelante\n|llevar adelante\n|más adelante\n|sacar adelante\n|salir adelante\n|seguir adelante}}\n\n====Interjection====\n{{head|es|interjection}}\n\n# [[come in]]\n# [[go ahead]]\n\n', '====Adverb====\n{{es-adv}}\n\n# [[forward]] {{gloss|toward the front}}\n# [[forward]] {{gloss|into the future}}\n\n=====Alternative forms=====\n* {{l|es|alante}} {{q|colloquial}}\n\n', '=====Alternative forms=====\n* {{l|es|alante}} {{q|colloquial}}\n\n', '====Derived terms====\n{{der3|es\n|adelantar\n|de aquí en adelante\n|en adelante\n|Gran Salto Adelante\n|llevar adelante\n|más adelante\n|sacar adelante\n|salir adelante\n|seguir adelante}}\n\n', '====Interjection====\n{{head|es|interjection}}\n\n# [[come in]]\n# [[go ahead]]\n\n'], ['===Etymology 2===\n{{nonlemma}}\n\n====Verb====\n{{head|es|verb form}}\n\n# {{es-verb form of|person=first-person|number=singular|tense=present|mood=subjunctive|ending=ar|adelantar}}\n# {{es-verb form of|person=third-person|number=singular|tense=present|mood=subjunctive|ending=ar|adelantar}}\n# {{es-verb form of|formal=yes|person=second-person|number=singular|sense=affirmative|mood=imperative|ending=ar|adelantar}}\n\n', '====Verb====\n{{head|es|verb form}}\n\n# {{es-verb form of|person=first-person|number=singular|tense=present|mood=subjunctive|ending=ar|adelantar}}\n# {{es-verb form of|person=third-person|number=singular|tense=present|mood=subjunctive|ending=ar|adelantar}}\n# {{es-verb form of|formal=yes|person=second-person|number=singular|sense=affirmative|mood=imperative|ending=ar|adelantar}}\n\n'], ['===Further reading===\n* {{R:DRAE}}']]



    def test_auto_lang(self, monkeypatch):
        res, dom = fetch_resdom("adelante")
        monkeypatch.setattr('builtins.input', lambda _: "dummy_input")

        v = (list1 := wx.auto_lang(dom, "unused#unused", "arbitrary", "")) == \
            (list2 := (list(wx.sections_by_lang(dom, "Spanish")), "arbitrary#Spanish", "arbitrary", "Spanish"))
        assert v

    def test_graph(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "1") #Multiple Definitions
        query, wres, origin = fetch_query("adelante", "Spanish")
        _, wtxt, dom = wres
        wres = None, wtxt, dom
        G, origin = wx.graph(query, wres, origin, "test-temp-1", "test-temp-2")
        G2 = nx.DiGraph()
        nx.add_path(G2, ["adelante#Spanish$0", "$0{m|Spanish|delante ['in front']}"])
        assert nx.is_isomorphic(G, G2)

        assert [repr(s) for s in G.nodes] == [s for s in G2.nodes]
        # G nodes: [adelante#Spanish$0, $0{m|Spanish|delante ['in front']}]
        # G2 nodes: ['adelante#Spanish$0', "$0{m|Spanish|delante ['in front']}"]
