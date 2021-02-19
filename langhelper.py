import warnings

from pyetymology.langcode import langcodes


class Language:
    def __init__(self, langcode: str=None, langname: str=None, langqstr: str=None, is_reconstr: bool=False, warn=True):
        """
        langcode: Wikt Language Code            ie. es, ine-pro
        langname: Name of Language              ie. Spanish, Proto-Indo-European
        langqstr: Query string for language     ie. Spanish, R:Proto-Indo-European

        WARNING: Reconstruction assumption only works one way!
        langqstr                                Proto-Indo-European -> R:Proto-Indo-European
        BUT
        langqstr                                Old English does not get inferred!
        """
        analyze_lname=False
        if langcode: # if we're given a langcode, we can generate everything else
            if not is_reconstr:
                is_reconstr = langcodes.is_reconstr(langcode)
            if not langname:
                langname = langcodes.name(langcode)
            self.langcode = langcode
            self.langname = langname
            self.reconstr = is_reconstr
        elif langqstr: # if we're not given a langcode, but we're given a langqstr
            self.langcode = None
            if langqstr.startswith("R:"):
                self.langname = langqstr[2:]
                self.reconstr = True
            elif langqstr.startswith("Reconstruction:"):
                self.langname = langqstr[15:]
                self.reconstr = True
            else:
                if not langname:
                    langname = langqstr
                    analyze_lname = True
        else:
            analyze_lname = True
        if analyze_lname:
            # if we're not given a langcode nor langqstr, but we may/may not have been given a langname
            # this is tricky
            self.langcode = None
            self.langname = langname

            if is_reconstr is None:
                if self.langname.startswith("Proto"):
                    self.reconstr = True
                else:
                    self.reconstr = False
                    # !!! If we're given only the langname, it is usual that it is not reconstructed
                    # TODO: Some languages, such as Old English, have reconstructed terms yet are not proto-languages!
                    # TODO: HUGE ASSUMPTION! - that all non-proto languages are not reconstructed, and that the user properly formatted those langs right!
            else:
                self.reconstr = is_reconstr
                # langcodes.is_name_reconstr(self.langname)
            if not langname:
                if warn:
                    warnings.warn("Neither langcode nor langname received.")
        self.langqstr = ("R:" + self.langname) if self.reconstr and self.langname else (self.langname)

    def __bool__(self):
        return bool(self.langcode or self.langname)

    def __eq__(self, other):
        return isinstance(other, Language) and self.langcode == other.langcode and self.langname == other.langname and self.reconstr == other.reconstr

    def __str__(self):
        return self.langqstr if self else ""

    def __repr__(self):
        return self.langqstr if self else ""