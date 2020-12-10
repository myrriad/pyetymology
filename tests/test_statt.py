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

from pyetymology.tests.test_ import fetch_resdom, fetch_query

class TestStatt:
    def test_missing_definition_graph(self):
        # etyobjects.reset_global_o_id()

        fetched_Q = fetch_query("statt", "German")
        # TODO: investigate the effect of flattening on this line
        G = wx.graph(fetched_Q)
        G2 = nx.DiGraph()
        G2.add_node(fetched_Q.origin)
        assert nx.is_isomorphic(G, G2)
        assert len(G.nodes) == 1
        assert [n for n in G.nodes] == [n for n in G2.nodes]