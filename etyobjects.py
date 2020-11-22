import string
import warnings
from typing import Tuple

import networkx as nx

import mwparserfromhell

from pyetymology.langcode import langcodes

originator_id_incrementer = 0
class Originator:

    def __init__(self, me: string, o_id: int = None):
        self.me = me

        if o_id is None:
            global originator_id_incrementer
            self.o_id = originator_id_incrementer
            originator_id_incrementer += 1
        else:
            self.o_id = o_id

    def __str__(self):
        return self.me

    def __repr__(self):
        return self.me + "$" + str(self.o_id)


    @property
    def color_id(self):
        return self.o_id
class Affixal:
    def __init__(self, template: mwparserfromhell.wikicode.Template, rtype: string):
        params = template.params
        self.template = template
        if rtype == "pre":
            self.root = params[2]
        elif rtype == "suf":
            self.root = params[1]
        # elif rtype == "con":
        else:
            self.root = ""
            # TODO: Everything


class EtyRelation:
    ety_abbrs = {"derived": "der",
                 "inherited": "inh",
                 "borrowed": "bor",
                 "orthographic borrowing": "obor",
                 "learned borrowing": "lbor",
                 "calque": "cal",
                 "semantic loan": "sl",
                 }
    cog_abbrs = {"cognate": "cog",
                 "noncognate": "ncog",
                 "noncog": "ncog",
                 "nc": "ncog",
                 "doublet": "doublet",
                 "piecewise doublet": "piecewise doublet"
                 }
    sim_abbrs = {"mention": "m"}

    aff_abbrs = {"affix": "af",
                 "prefix": "pre",
                 "confix": "con",
                 "suffix": "suf",
                 "compound": "com"}

    # lemma_ = {}
    # https://en.wiktionary.org/wiki/Category:Form-of_templates
    # https://en.wiktionary.org/wiki/Module:form_of/data

    def __init__(self, origin: Originator, template: mwparserfromhell.wikicode.Template):
        self.origin = origin  # type: Originator

        rtype = str(template.name)
        params = template.params
        lang = word = _selflang = None

        ety_abbrs = EtyRelation.ety_abbrs
        cog_abbrs = EtyRelation.cog_abbrs
        aff_abbrs = EtyRelation.aff_abbrs
        sim_abbrs = EtyRelation.sim_abbrs
        if rtype in ety_abbrs:  # use the abbreviations
            rtype = ety_abbrs[rtype]
        if rtype in cog_abbrs:  # use the abbreviations
            rtype = cog_abbrs[rtype]
        if rtype in aff_abbrs:
            rtype = aff_abbrs[rtype]
        if rtype in sim_abbrs:
            rtype = sim_abbrs[rtype]

        # TODO: shift to using template.get("1") instead of template.params[0]
        self.null = False
        self.affixal = None
        if rtype in ety_abbrs.values():  # if it's an etymological relation
            _selflang = str(params[0])
            lang = str(params[1])
            word = str(params[2])


        elif rtype in cog_abbrs.values() or rtype in sim_abbrs.values():
            # if it's a cognate relation
            # or affix, prefix, suffix, etc.
            # or mention
            lang = str(params[0])
            word = str(params[1])
        elif rtype in aff_abbrs.values(): # this is really complicated
            lang = str(params[0])
            # word = str(params[1])
            self.affixal = Affixal(template, rtype)
            word = self.affixal.root
        else:
            self.null = True  # if it's none that are recognized, mark self as null

        self.params = params
        self.rtype = rtype
        self.lang = lang
        self.langname = langcodes.name(lang, use_ety=True, use_fam=True)
        if lang and not self.langname:
            print(f"{lang} is None")
        self._selflang = _selflang
        self._selflangname = langcodes.name(_selflang)
        self.word = word

    def matches_query(self, me) -> bool:
        terms = me.split("#")
        def_id = None
        if len(terms) == 1:
            word = me
            warnings.warn("Language not detected for query " + me)
            return self.word == word
        elif len(terms) == 2:
            word, lang = terms
            return self.word == word and self.langname == lang
        elif len(terms) == 3:
            warnings.warn("definition ids not supported yet")
            word, lang = terms
            return self.word == word and self.langname == lang

    def __str__(self):
        if not self:
            return "{{" + self.rtype + " null " + repr(self.params) + "}}"
        if self.affixal:
            return str(self.affixal.template)
        assert self.word is not None
        assert self.langname is not None
        paramsc = repr(self.params[3:])  # slice off the first 3 args
        paramsc = "" if paramsc == "[]" else " " + paramsc  # convert []s to ""

        return "{" + self.rtype + "|" + self.langname + "|" + self.word + paramsc + "}"

    def __repr__(self):
        return "$" + str(self.origin.o_id) + str(self)

    def __bool__(self):
        return not self.null

    @property
    def color_id(self):
        return self.origin.o_id


class LemmaRelation:

    def __init__(self, origin: Originator, template: mwparserfromhell.wikicode.Template):
        self.origin = origin  # type: Originator

        rtype = str(template.name)
        params = template.params
        lang = word = _selflang = None

        self.null = False
        # there are a ton of lemma templates (see
        # https://en.wiktionary.org/wiki/Category:Form-of_templates
        # https://en.wiktionary.org/wiki/Module:form_of
        # https://en.wiktionary.org/wiki/Module:form_of/data
        # Just see if it ends in " of" and call it a day

        assert template.name[-3:] == " of"
        print(template)
        if template.has("lang"):
            lang = str(template.get("lang"))
            word = str(template.get("1"))
            # deprecated
        elif template.has("2"):

            lang = str(template.get("1"))
            word = str(template.get("2"))
        else:
            # es-verb form of
            # TODO: add support for "verb", "inf", "infinitive"
            word = str(template.get("1"))
            dashidx = str(template.name).index("-")
            lang = template.name[:dashidx]

        print(f"Found lemma?: lang: {lang} word: {word}")

        self.params = params
        self.rtype = rtype
        self.lang = lang
        self.langname = langcodes.name(lang, use_ety=True, use_fam=True)
        if lang and not self.langname:
            print(f"{lang} is None")
        self.word = word

    def matches_query(self, me) -> bool:
        terms = me.split("#")
        def_id = None
        if len(terms) == 1:
            word = me
            warnings.warn("Language not detected for query " + me)
            return self.word == word
        elif len(terms) == 2:
            word, lang = terms
            return self.word == word and self.langname == lang
        elif len(terms) == 3:
            warnings.warn("definition ids not supported yet")
            word, lang = terms
            return self.word == word and self.langname == lang

    def matches(self, other):
        return type(other) == LemmaRelation and repr(self) == repr(other)

    def __str__(self):
        if not self:
            return "L{{" + self.rtype + " null " + repr(self.params) + "}}"
        assert self.word is not None
        assert self.langname is not None
        paramsc = repr(self.params[2:])  # slice off the first 2 args
        paramsc = "" if paramsc == "[]" else " " + paramsc  # convert []s to ""

        return "L{" + self.rtype + "|" + self.langname + "|" + self.word + "}" # + paramsc + "}"
        # return f"L{{{self.rtype}|{self.langname}|{self.word}}}"

    def __repr__(self):
        return "$" + str(self.origin.o_id) + str(self)

    def __bool__(self):
        return not self.null

    # def __eq__(self, other): This must be made compatable with __hash__() to work w/ nx - not worth it
    #     return self.__repr__() == other.__repr__()
    @property
    def color_id(self):
        return self.origin.o_id

class MissingException(Exception):

    def __init__(self, message, missing_thing=None, G:nx.DiGraph = None):
        super().__init__(self, message)
        self.G = G
        self.missing_thing = missing_thing