import warnings

from pyetymology.langcode import langcodes


class Lang:
    def __init__(self, langcode: str=None, langname: str=None, langqstr: str=None, is_deconstr: bool=False):
        """
        langcode: Wikt Language Code            ie. es, ine-pro
        langname: Name of Language              ie. Spanish, Proto-Indo-European
        langqstr: Query string for language     ie. Spanish, R:Proto-Indo-European
        """
        if langcode: # if we're given a langcode, we can generate everything else
            if not is_deconstr:
                is_deconstr = langcodes.is_deconstr(langcode)
            if not langname:
                langname = langcodes.name(langcode)
            self.langcode = langcode
            self.langname = langname
            self.reconstr = is_deconstr
        elif langqstr: # if we're not given a langcode, but we're given a langqstr
            self.langcode = None
            if langqstr.startswith("R:"):
                self.langname = langqstr[2:]
                self.reconstr = True
            elif langqstr.startswith("Reconstruction:"):
                self.langname = langqstr[15:]
                self.reconstr = True
            else:
                self.langname = langqstr
                self.reconstr = False

        else:
            # if we're not given a langcode nor langqstr, but we may/may not have been given a langname
            # this is tricky
            if not langname:
                warnings.warn("Neither langcode nor langname received; not enough information!")
            self.langcode = None
            self.langname = langname
            self.reconstr = False

        self.langqstr = ("R:" + self.langname) if self.reconstr and self.langname else (self.langname)

    def __bool__(self):
        return bool(self.langcode or self.langname)

    def __eq__(self, other):
        return isinstance(other, Lang) and self.langcode == other.langcode and self.langname == other.langname and self.reconstr == other.reconstr