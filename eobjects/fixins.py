import builtins
from typing import Any

from matplotlib import pyplot as plt

from pyetymology.etyobjects import InputException

_is_plot_active = False

def input(__prompt: Any) -> str:
    global _is_plot_active
    if _is_plot_active:
        print("Close MatplotLib to Continue")
        plt.show()
    try:
        return builtins.input(__prompt)
    except EOFError as e_info:
        raise InputException("Unable to read from console.") from None