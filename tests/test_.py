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

def fetch_wikitext(topic):
    try:
        with open("wtxt_" + topic + ".txt", encoding="utf-8") as f:
            txt = f.read()
            return txt
    except FileNotFoundError as error:
        print('Asset not found! Creating...')
        query, wikiresponse, origin, _, _ = wx.query(topic)
        me, word, lang, def_id = query
        _, wikitext, _ = wikiresponse
        with open("wtxt_" + topic + ".txt", "w+", encoding="utf-8") as f2:
            f2.write(wikitext)
        return wikitext

def fetch_query(topic: str, lang: str):
    # monkeypatch.setattr('builtins.input', lambda _: lang)
    try:
        with open("query_" + topic + "_" + lang + ".txt", 'rb') as f:
            pickleme = dill.load(f)
            query, wikiresponse, origin = pickleme
            _, wikitext, dom = wikiresponse

            """
            # wikitext and dom aren't pickled properly
            # what we need to mimic:
            res, dom = wikitextparse(wikitext)

            dom, me, word, lang = auto_lang(dom, me, word, lang, mimic_input=mimic_input)
            """
            res, dom = wx.wikitextparse(wikitext, redundance=True)
            dom = list(wx.sections_by_lang(dom, lang))  # expanded auto_lang()

            wikiresponse = None, res, dom
            return query, wikiresponse, origin
    except FileNotFoundError as error:
        print('Asset not found! Creating...')
        query, wikiresponse, origin, _, _ = wx.query(topic, mimic_input=lang)
        _, wikitext, dom = wikiresponse
        wikiresponse = None, str(wikitext), str(dom)
        pickleme = query, wikiresponse, origin
        with open("query_" + topic + "_" + lang + ".txt", "wb") as output:
            dill.dump(pickleme, output, dill.HIGHEST_PROTOCOL)

        """
        # wikitext and dom aren't pickled properly
        # what we need to mimic:
        res, dom = wikitextparse(wikitext)

        dom, me, word, lang = auto_lang(dom, me, word, lang, mimic_input=mimic_input)
        """
        res, dom = wx.wikitextparse(wikitext, redundance=True)
        dom = list(wx.sections_by_lang(dom, lang))  # expanded auto_lang()
        wikiresponse = None, res, dom
        return query, wikiresponse, origin
def fetch_resdom(topic, redundance=False):
    wt = fetch_wikitext(topic)
    res, dom = wx.wikitextparse(wt, redundance=redundance)
    return res, dom

class Test:
    def test_exact_prefix(self):
        assert wx.has_exact_prefix("==Spanish==", "==")
        assert not wx.has_exact_prefix("===Etymology===", "==")
    def test_fetch(self):
        return # don't make too many API queries
        q1 = fetch_query("adelante", "Spanish")
        q2 = wx.query("adelante#Spanish", redundance=True)
        query1, wres1, o1 = q1
        query2, wres2, o2, _, _ = q2
        assert query1 == query2
        assert str(o1) == str(o2)
        _, wtxt1, dom1 = wres1
        _, wtxt2, dom2 = wres2
        dom2: List[Wikicode]
        assert wtxt1 == wtxt2
        assert dom1 == dom2



# TODO: Test Unsupported Titles
