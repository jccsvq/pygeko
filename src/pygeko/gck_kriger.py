"""Open a Python REPL ready for interactive use with relevant files imported"""

import code
import os
import readline
import rlcompleter
import sys

sys.path.append(".")  # To allow imports of working directory files

from pygeko.__about__ import __version__ as VERSION
from pygeko.gplot import Gplot  # noqa: F401
from pygeko.kdata import Kdata  # noqa: F401
from pygeko.kgrid import Kgrid  # noqa: F401
from pygeko.utils import get_data_path  # noqa: F401

message = f"""\nWelcome to pyGEKO-Kriger {VERSION}
    
Classes Kdata, Kgrid and Gplot imported.

Use exit() or Ctrl-D (i.e. EOF) to exit.
"""

sys.ps1 = "--> "


def main():
    """Entry point for pyGCK kriger app"""
    # 1. Configure the history file
    history_file = os.path.expanduser("~/.pygeko_history")
    if os.path.exists(history_file):
        readline.read_history_file(history_file)

    # 2. Configure autocomplete with TAB
    # The completer needs to know the local variable dictionary
    local_vars = globals().copy()  # Start with all global variables
    local_vars.update(locals())  # Add all local variables at this point

    readline.set_completer(rlcompleter.Completer(local_vars).complete)
    readline.parse_and_bind("tab: complete")

    # 3. Save history on exit
    import atexit

    atexit.register(readline.write_history_file, history_file)

    # 4. Launch the REPL
    code.interact(
        banner=message,
        local=local_vars,
        exitmsg="\n--- Exiting GCK-Kriger, Bye! ---\n",
    )


if __name__ == "__main__":
    main()
