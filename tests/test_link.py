from pyetymology.emulate import moduleimpl


def test_macron():
    link = moduleimpl.to_link("plicō", "Latin")
    assert link == "http://en.wiktionary.org/w/api.php?action=parse&page=" + "plico" + "&prop=wikitext&formatversion=2&format=json"

