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

from pyetymology.tests.test_ import fetch_resdom, fetch_query

class TestStatt:
    def test_missing_definition_graph(self):
        fetched_q = fetch_query("statt", "German")
        # TODO: investigate the effect of flattening on this line
        G, origin = wx.graph(fetched_q)
        G2 = nx.DiGraph()
        G2.add_node(origin)
        assert nx.is_isomorphic(G, G2)
        assert len(G.nodes) == 1
        assert [s for s in G.nodes] == [s for s in G2.nodes]