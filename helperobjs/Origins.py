from typing import Any

from pyetymology.etyobjects import Originator  # TODO: refactor that into this class


class OriginsTracker:
    def __init__(self):
        self.os = []
        self.global_o_id = 0
    def track_obj(self, addme: Any):
        assert type(addme) != Originator
        o = Originator(addme, o_id=self.global_o_id)
        self.global_o_id += 1
        self.os.append(o)