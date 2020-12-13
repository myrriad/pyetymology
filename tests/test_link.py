from pyetymology.module import module


def test_macron():
    link = module.link("plicō", "Latin")
    assert link == "https://en.wiktionary.com/w/api.php?action=parse&page=" + "plico" + "&prop=wikitext&formatversion=2&format=json"

