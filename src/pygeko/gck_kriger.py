"""Open a Python REPL ready for interactive use with relevant files imported"""

import code
import sys

sys.path.append(".")  # To allow imports of working directory files

from pygeko.__about__ import __version__ as VERSION
from pygeko.gplot import Gplot  # noqa: F401
from pygeko.kdata import Kdata, Kgrid  # noqa: F401
from pygeko.utils import get_data_path  # noqa: F401

message = f"""\nWelcome to pyGEKO-Kriger {VERSION}
    
Classes Kdata, Kgrid and Gplot imported.

Use exit() or Ctrl-D (i.e. EOF) to exit.
"""

sys.ps1 = "--> "


def main():
    """Entry point for pyGCK kriger app"""

    local_vars = globals().copy()  # Start with all global variables
    local_vars.update(locals())  # Add all local variables at this point

    code.interact(
        banner=message,
        local=local_vars,
        exitmsg="\n--- Exiting GCK-Kriger, Bye! ---\n",
    )


if __name__ == "__main__":
    main()
