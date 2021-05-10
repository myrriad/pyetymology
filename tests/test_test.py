from pyetymology.eobjects.wikikey import WikiKey


def test():
    wkey = WikiKey.from_query("*per-#Proto-Indo-European")
    wkey.load_result()
    wkey.load_wikitext()
    print(wkey)