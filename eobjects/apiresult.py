import json
from enum import Enum
from typing import Optional

import requests
from requests import Response

from pyetymology.eobjects.mwparserhelper import wikitextparse, reduce_to_one_lang
# from pyetymology.eobjects.wikikey import WikiKey
from pyetymology.etyobjects import MissingException

session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))  # retry up to 2 times
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))

class APIResult:
    def __init__(self, fullurl, response:Optional[Response]=None, jsn:Optional[Response]=None):
        if not response or not jsn: # if any is missing
            response, jsn = make_http_request(fullurl)
        self.response = response
        self.jsn = jsn
        self.fullurl = fullurl
        check_json(self)
        self.wikitype = None

    def load_wikitext(self, wkey:Optional['WikiKey']):
        jsoninfo = parse_json(self, wkey)
        if jsoninfo[0] == "parse":
            self.wikitype, self.wikitext, self.wikiresponse, self.dom, self.langname = jsoninfo
        elif jsoninfo[0] == "query":
            self.wikitype, self.derivs = jsoninfo
    @property
    def text(self):
        return self.response.text
def make_http_request(fullurl: str, online=True):
    if online:
        global session
        res = session.get(fullurl)
        #cache res TODO: implement better caching with test_'s fetch stuff
    else:
        raise Exception("offline browsing not implemented yet")
    txt = res.text
    # print(txt)
    jsn = json.loads(txt) #type: json
    return res, jsn
def check_json(result: APIResult):
    jsn = result.jsn
    fullurl = result.fullurl
    if "error" in jsn:
        if "info" in jsn["error"]:
            if jsn["error"]["info"] == "The page you specified doesn't exist.":
                raise MissingException(f"No page found for specified url {fullurl}.", missing_thing="page")
            else:
                raise ValueError(f"Unexpected error info {jsn['error']['info']} for url {result.fullurl}")
        raise MissingException(
            f"Unexpected error, info not found. Url: {fullurl} JSON: {str(jsn['error'])}",
            missing_thing="everything")
def parse_json(result: APIResult, wkey: Optional['WikiKey'] = None, mimic_input=None):
    jsn = result.jsn

    # the above will have thrown an error
    # if result.deriv:
    if "query" in jsn:
        # assert deriv NAH we don't need to assert
        assert wkey.deriv
        derivs = [pair["title"] for pair in result.jsn["query"]["categorymembers"]]
        return "query", derivs
        # origin = Originator(me, o_id=query_id)
        # return DummyQuery(me=me, origin=origin, child_queries=derivs, with_lang=Language(langcode="en"))

    # https://en.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:English_terms_derived_from_the_Proto-Indo-European_root_*ple%E1%B8%B1-&cmprop=title
    elif "parse" in jsn:
        wikitext = jsn["parse"]["wikitext"]
        res, dom = wikitextparse(wikitext, redundance=False)
        # Here was the lang detection
        dom, langname = reduce_to_one_lang(dom, use_lang=mimic_input if mimic_input else wkey.Lang.langname)
        return "parse", wikitext, res, dom, langname
    else:
        raise Exception(f"JSON malformed; top-level not found! (neither parse, query, nor error found) JSON: {jsn} URL: {result.fullurl}")




class WikiParsedResult(APIResult):
    pass


