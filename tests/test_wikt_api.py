from unittest import TestCase

import pytest

from pyetymology import wikt_api as wx
from pyetymology.tests import assets


class Test:
    def test_exact_prefix(self):
        assert wx.has_exact_prefix("==Spanish==", "==")
        assert not wx.has_exact_prefix("===Etymology===", "==")

    @pytest.fixture()
    def resdom(self):
        delante = assets.txt_delante

        res, dom = wx.wikitextparse(delante)
        return res, dom

    @pytest.fixture()
    def test_lang_detect(self, resdom):
        res, dom = resdom
        d = wx.all_lang_sections(dom) #type: Generator[List[Wikicode]]
        ls = list(d)
        sections = ls[0]
        wikicode = sections[0]
        a = str(wikicode)
        b = assets.txt_delante
        b = b[b.index("\n")+1:]
        assert len(ls) == 1 # we only got one lang
        assert len(sections) == 1
        assert a == b
        assert a.startswith("==Spanish==")
        return sections

    def test_section_detect(self, resdom):
        res, dom = resdom
        secs = list(wx.sections_by_level(dom, 3))
        assert secs == [["===Etymology===\nFrom {{inh|es|osp|denante}} ({{m|osp|de}} + {{m|osp|enante}}); ''enante'' from {{inh|es|LL.|inante}}, from {{inh|es|la|in}} + {{m|la|ante}}. Compare also {{cog|ro|înainte}}.\n\n"], ["===Adverb===\n{{es-adv}}\n\n# [[in front of]], [[before]] {{qualifier|spatially}}\n# [[forward]], [[forwards]] {{gloss| with ''hacia'' preceding it}}\n# [[ahead]] {{gloss| with ''por'' preceding it}}\n\n====Derived terms====\n* {{l|es|adelante}}\n* {{l|es|el burro delante, para que no se espante}}\n* {{l|es|delantal}}\n* {{l|es|llevarse por delante}}\n\n====Related terms====\n* {{l|es|antes}}", '====Derived terms====\n* {{l|es|adelante}}\n* {{l|es|el burro delante, para que no se espante}}\n* {{l|es|delantal}}\n* {{l|es|llevarse por delante}}\n\n', '====Related terms====\n* {{l|es|antes}}']]

    def test_auto_lang(self, monkeypatch, adelante):
        res, dom = adelante
        monkeypatch.setattr('builtins.input', lambda _: "dummy_input")

        v = \
            (ls := wx.auto_lang(dom, "unused#unused", "arbitrary", "")) == \
            (lsb := (list(wx.sections_by_lang(dom, "Spanish")), "arbitrary#Spanish", "arbitrary", "Spanish"))
        assert v



