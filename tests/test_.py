from typing import List, Tuple

import dill
import networkx as nx
from mwparserfromhell.wikicode import Wikicode

from pyetymology import wikt_api as wx, etyobjects
from pyetymology.etyobjects import Originator
from pyetymology.helperobjs import querying
from pyetymology.helperobjs.querying import ThickQuery


def fetch_wikitext(topic):
    try:
        with open("assets/wtxt_" + topic + ".txt", encoding="utf-8") as f:
            txt = f.read()
            return txt
    except FileNotFoundError as error:
        print('Asset not found! Creating...')
        # query, wikiresponse, origin = wx.query(topic).to_tupled()
        wikitext = wx.query(topic).wikitext
        # me, word, lang, def_id = query
        # _, wikitext, _ = wikiresponse
        with open("assets/wtxt_" + topic + ".txt", "w+", encoding="utf-8") as f2:
            f2.write(wikitext)
        return wikitext

def fetch_query(topic: str, lang: str) -> ThickQuery:
    # monkeypatch.setattr('builtins.input', lambda _: lang)
    try:
        with open("assets/query_" + topic + "_" + lang + ".txt", 'rb') as f:
            pickleme = dill.load(f)
            query, wikiresponse, origin = pickleme
            _, wikitext, dom = wikiresponse

            """
            # wikitext and dom aren't pickled properly
            # what we need to mimic:
            res, dom = wikitextparse(wikitext)

            dom, me, word, lang = auto_lang(dom, me, word, lang, mimic_input=mimic_input)
            The following mimics the function auto_lang()
            """
            res, dom = wx.wikitextparse(wikitext, redundance=True)
            dom = list(wx.sections_by_lang(dom, lang))  # expanded auto_lang()

            wikiresponse = None, res, dom
            bigQ = querying.from_tupled(query, wikiresponse, origin)
            # TODO eliminate global state
            return bigQ
    except FileNotFoundError as error:
        print('Asset not found! Creating...')
        query, wikiresponse, origin = wx.query(topic, mimic_input=lang).to_tupled()
        _, wikitext, dom = wikiresponse
        wikiresponse = None, str(wikitext), str(dom)
        pickleme = query, wikiresponse, origin
        with open("assets/query_" + topic + "_" + lang + ".txt", "wb") as output:
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
        bigQ = querying.from_tupled(query, wikiresponse, origin)
         # don't do it over here because it is already done
        return bigQ
def fetch_resdom(topic, redundance=False) -> Tuple[Wikicode, List[Wikicode]]:
    wt = fetch_wikitext(topic)
    res, dom = wx.wikitextparse(wt, redundance=redundance)
    return res, dom

def is_eq__repr(G, G__repr):
    # wx.draw_graph(G)
    # wx.draw_graph(G__repr)
    assert nx.is_isomorphic(G, G__repr)

    assert set([repr(s) for s in G.nodes]) == set([s for s in G__repr.nodes])  # nx usually reverses the nodes, probably b/c of nx.add_path
    assert set((repr(l), repr(r)) for l, r in G.edges) == set(e for e in G__repr.edges)
    return True # if there hasn't been an assertion error

def is_eq__str(G, G__str):
    assert nx.is_isomorphic(G, G__str)

    assert set([str(s) for s in G.nodes]) == set([s for s in G__str.nodes])  # nx usually reverses the nodes, probably b/c of nx.add_path
    assert set((str(l), str(r)) for l, r in G.edges) == set(e for e in G__str.edges)
    return True # if there hasn't been an assertion error

class MockInput:
    def __init__(self, inputs: List[str]):
        self.inputs = inputs
        self.idx = 0
    def next(self):
        if self.idx >= len(self.inputs):
            raise Exception(f"Not enough mock inputs supplied! The function called {self.idx+1} user inputs, but only {self.inputs} was supplied!")
        self.idx += 1
def patch_multiple_input(monkeypatch, inputs: List[str]):
    mock_input = MockInput(inputs)
    monkeypatch.setattr('builtins.input', lambda _: mock_input.next())


class Test:
    def test_exact_prefix(self):
        assert wx.has_exact_prefix("==Spanish==", "==")
        assert not wx.has_exact_prefix("===Etymology===", "==")
    def test_null_sections_by_level(self):
        dom = fetch_resdom("llevar")[1]
        assert list(wx.sections_by_level(dom, 6)) == []
    def test_fetch(self):
        return  # don't make too many API queries
        Q1 = fetch_query("adelante", "Spanish")
        Q2 = wx.query("adelante#Spanish", redundance=True)
        query1, wres1, o1 = Q1.to_tupled()
        query2, wres2, o2 = Q2.to_tupled()
        assert query1 == query2
        assert str(o1) == str(o2)
        _, wtxt1, dom1 = wres1
        _, wtxt2, dom2 = wres2
        dom2: List[Wikicode]
        assert wtxt1 == wtxt2
        assert dom1 == dom2


def graph_to_str(G):
    return repr(nx.to_dict_of_lists(G))
# TODO: Test Unsupported Titles
