import string
import warnings
from typing import Any

import networkx as nx

import mwparserfromhell
from mwparserfromhell.nodes import Template

import pyetymology.queryobjects
import pyetymology.queryutils
from pyetymology.langcode import langcodes
from pyetymology.emulate import moduleimpl




@property
def originator_id_incrementer():
    raise Exception("Deprecated")


@originator_id_incrementer.setter
def originator_id_incrementer(a):
    raise Exception("Deprecated")
originator_id_incrementer = 0


def reset_global_o_id():
    raise Exception("Deprecated")

    global originator_id_incrementer
    originator_id_incrementer = 0

def try_get(template: Template, key: str, default="", warn=True, throw=False) -> str:
    if template.has(key):
        return str(template.get(key))
    else:
        if throw:
            raise ValueError(f"Template {template} doesn't have value defined at index {key}!")
        if warn:
            warnings.warn(f"Template {template} doesn't have a word defined at index {key}! This is strange but apparently possible.")
    return default

class Originator:


    def __init__(self, me: Any, o_id: int = None):
        self.me = me

        if o_id is None:

            global originator_id_incrementer
            self.o_id = originator_id_incrementer
            originator_id_incrementer += 1
            raise Exception("Deprecated")

        else:
            self.o_id = o_id

    def __str__(self):
        return str(self.me)

    def __repr__(self):
        return str(self.me) + "$" + str(self.o_id)

class Affixal:
    def __init__(self, template: mwparserfromhell.wikicode.Template, rtype: string):
        params = template.params
        self.template = template
        if rtype == "pre":
            self.root = str(template.get("3")) # params[2] lua has 1-indexed arrays
        elif rtype == "suf":
            self.root = str(template.get("2")) # params[1]
        # elif rtype == "con":
        else:
            self.root = ""
            # TODO: Everything


class WordRelation:
    def matches_query(self, me:str, strict=False, ultra_strict=False) -> bool:
        word, biglang, _ = pyetymology.queryutils.query_to_qparts(me)
        return moduleimpl.matches(self.word, self.langname, word, biglang.langname, strict=strict, ultra_strict=ultra_strict)
        # TODO: NOT iterate through entire graph when trying to find a match

    @property
    def o_id(self):
        return self.origin.o_id

    def __bool__(self):
        return not self.null

    def __init__(self, params, rtype, langcode, word, _selflang=None):
        self.params = params
        self.rtype = rtype
        self.langcode = langcode
        self.langname = langcodes.name(langcode, use_ety=True, use_fam=True)
        if langcode and not self.langname:
            print(f"{langcode} is None")
        self.word = word
        if _selflang:
            self._selflang = _selflang
            self._selflangname = langcodes.name(_selflang)



class EtyRelation(WordRelation):
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

        # DID: shift to using template.get("1") instead of template.params[0]
        self.null = False
        self.affixal = None
        if rtype in ety_abbrs.values():  # if it's an etymological relation
            _selflang = str(template.get("1"))  # str(params[0])
            lang = str(template.get("2"))  # https://en.wiktionary.org/wiki/Template:derived
            word = try_get(template, "3")

        elif rtype in cog_abbrs.values() or rtype in sim_abbrs.values():
            # if it's a cognate relation
            # or mention
            lang = str(template.get("1"))

            word = try_get(template, "2")
        elif rtype in aff_abbrs.values():
            # if affix, prefix, suffix, etc. https://en.wiktionary.org/wiki/Template:affix
            # this is really complicated
            lang = str(template.get("1"))
            # word = str(params[1])
            self.affixal = Affixal(template, rtype)
            word = self.affixal.root
        else:
            warnings.warn("Template {rtype} is not recognized!")
            self.null = True  # if it's none that are recognized, mark self as null

        WordRelation.__init__(self, params, rtype, lang, word, _selflang)



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


class LemmaRelation(WordRelation):

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
            word = try_get(template, "1")
            # deprecated. It seems that this has been removed.
            # TODO: Remove this, since it appears that this has bee deprecated AND removed.
        elif template.has("2"):

            lang = str(template.get("1"))
            word = try_get(template, "2")
        else:
            # es-verb form of
            # (unnamed) or verb or inf or infinitive — should be the entry for the infinitive (el infinitivo).
            # TODO: add support for "verb", "inf", "infinitive"
            # TODO: testing
            word = try_get(template, "head")
            word = word if word else try_get(template, "infinitive", warn=False)
            word = word if word else try_get(template, "1", throw=True)
            dashidx = str(template.name).index("-")
            lang = template.name[:dashidx]

        # print(f"Found lemma?: lang: {lang} word: {word}")
        WordRelation.__init__(self, params, rtype, lang, word)

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

    # def __eq__(self, other): This must be made compatable with __hash__() to work w/ nx - not worth it
    #     return self.__repr__() == other.__repr__()


class DescentRelation(WordRelation):
    desc_abbrs = {"descendant": "desc",
                  "see descendants": "see desc"} # https://en.wiktionary.org/wiki/Template:descendant

    def __init__(self, origin: Originator, template: mwparserfromhell.wikicode.Template, query_opt:str=None):



        self.origin = origin  # type: Originator  # TODO: create convenience super() init method

        if query_opt:
            word, _Lang, qflags = pyetymology.queryutils.query_to_qparts(query_opt)
            self.word = word
            self.langname = _Lang.langname
            self.rtype = "custom"
            self.params = []
            self.null = False
            self.affixal = None
            return

        rtype = str(template.name)
        params = template.params
        lang = word = _selflang = None

        abbrs = DescentRelation.desc_abbrs
        if rtype in abbrs:  # use the abbreviations
            rtype = abbrs[rtype]

        self.null = False
        self.affixal = None
        _selflang = None
        if rtype in abbrs.values():  # see https://en.wiktionary.org/wiki/Template:descendant: uses same layout as link and mention
            if rtype != "see desc": # exclude this, which just marks to see for further descendants
                lang = str(template.get("1"))
                word = try_get(template, "2")
                # raise MissingException(f"Template {template} didn't have expected index {str(e)}", missing_thing="template_attribute")
        else:
            self.null = True  # if it's none that are recognized, mark self as null

        WordRelation.__init__(self, params, rtype, lang, word, _selflang)

    def __str__(self):
        if not self:
            return "#{{" + self.rtype + " null " + repr(self.params) + "}}"
        if self.affixal:
            return str(self.affixal.template)
        assert self.word is not None
        assert self.langname is not None
        paramsc = repr(self.params[3:])  # slice off the first 3 args
        paramsc = "" if paramsc == "[]" else " " + paramsc  # convert []s to ""

        return "#{" + self.rtype + "|" + self.langname + "|" + self.word + paramsc + "}"

    def __repr__(self):
        return "$" + str(self.origin.o_id) + str(self)

class MissingException(Exception):

    def __init__(self, message, missing_thing=None, G:nx.DiGraph = None):
        super().__init__(self, message)
        self.G = G
        self.missing_thing = missing_thing
        self.message = message

class MissingInputException(MissingException):
    def __init__(self, *args, **kwargs):
        super(MissingException, self).__init__(*args, **kwargs)

class InputException(Exception):
    """
    When more user info/input is needed, and console input is disabled.
    """

