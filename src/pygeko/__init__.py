"""
pyGEKO: Fast Generalized Covariance Kriging for Python.
"""

from .__about__ import __version__
from .kdata import Kdata
from .kgrid import Kgrid
from .gplot import Gplot
from .prep import Calibrator
from .kprofile import Kprofile, KprofileCSV, Pplot, ProfilePicker
from . import utils

Kdata.__module__ = "pygeko"
Gplot.__module__ = "pygeko"
Kgrid.__module__ = "pygeko"
Calibrator.__module__ = "pygeko"
Kprofile.__module__ = "pygeko"
KprofileCSV.__module__ = "pygeko"
ProfilePicker__module__ = "pygeko"
Pplot.__module__ = "pygeko"
utils.__module__ = "pygeko"


__all__ = ["Kdata", "Gplot", "Kgrid", "Calibrator", "Kprofile", "KprofileCSV","Pplot", "utils", "__version__"]

