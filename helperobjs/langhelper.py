import warnings

from pyetymology.langcode import langcodes


class Lang:
    def __init__(self, langcode: str=None, langname: str=None, langqstr: str=None, is_deconstr: bool=None):
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
            self.deconstr = is_deconstr
        elif langqstr: # if we're not given a langcode, but we're given a langqstr
            self.langcode = None
            if langqstr.startswith("R:"):
                self.langname = langqstr[2:]
                self.deconstr = True
            elif langqstr.startswith("Reconstruction:"):
                self.langname = langqstr[15:]
                self.deconstr = True
            else:
                self.langname = langqstr
                self.deconstr = False

        elif langname: # if we're not given a langcode nor langqstr, but we're given a langname
            # this is tricky
            self.langcode = None
            self.langname = langname
            self.deconstr = None
        else:
            warnings.warn("Neither langcode nor langname received; not enough information!")
            self.langcode = None
            self.langname = None
            self.deconstr = None
        self.langqstr = ("R:" + self.langname) if self.deconstr and self.langname else (self.langname)


    def __bool__(self):
        return self.langcode or self.langname