import requests

# Credits to Suyash Behera at https://pypi.org/project/wiktionaryparser/
from pyetymology import helper_old

session = requests.Session()
session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))  # retry up to 2 times
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))

me = "llegar#Spanish"

#end api



parents, children = helper_old.fetch(me, session)
# parents is a list of parents in mostly hierarchical order, youngest to oldest

prev = me
parents = list(reversed(parents))

while len(parents) > 0:
    parent = parents.pop() # node's youngest parent
    relatives = parents
    parent_parents, parent_children = helper_old.fetch(parent, session)
    if prev in parent_children:
        # fantastic!
        print("-Parent " + parent)
    else:
        if me in parent_children:
            print("/Parent " + parent)
            # then prev is not child, but I am -
        else:
            print("Father which recognizes me as illegitimate: " + prev + " not in " + parent + str(parent_children))
            #TODO: ad- Latin words prefixed with x
        # one sided relatedness: <I> know that parent is my ancestor, but parent doesn't know that <I> am a descendant



