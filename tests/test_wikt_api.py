from unittest import TestCase

import pytest

from pyetymology import wikt_api as wx
from pyetymology.tests import assets


class Test:
    def test_exact_prefix(self):
        assert wx.has_exact_prefix("==Spanish==", "==")
        assert not wx.has_exact_prefix("===Etymology===", "==")

    @pytest.fixture()
    def delante(self):
        delante = assets.txt_delante

        res, dom = wx.wikitextparse(delante)
        return res, dom

    def test_lang_detect(self, delante):
        res, dom = delante
        d = wx.all_lang_sections(dom)
        a = str(list(d)[0][0])
        b = assets.txt_delante
        b = b[b.index("\n")+1:]
        assert len(list(d)) == 1
        assert a == b


