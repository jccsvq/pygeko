"""
pyGEKO Kgrid Module
-------------------
Handles grid definition and Kriging estimation.
"""

from pygeko.kdata import Kdata
from pygeko.utils import (
    export_grid,
    fast_preview,
    report_models,
)


class Kgrid:
    """Manages grid definition and interpolation workflow."""

    def __init__(
        self,
        kdata: "Kdata",
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        bins: int,
        hist: int,
    ):
        """Class constructor

        :param kdata: Kdata object
        :type kdata: Kdata
        :param xmin: estimation window X min
        :type xmin: float
        :param xmax: estimation window X max
        :type xmax: float
        :param ymin: estimation window Y min
        :type ymin: float
        :param ymax: estimation window Y max
        :type ymax: float
        :param bins: number of X bins
        :type bins: int
        :param hist: number of Y bins
        :type hist: int
        """
        assert isinstance(kdata, Kdata)
        self.kdata = kdata
        # Estimation window parameters
        if kdata.normalized:
            self._xmin, self._ymin, _, _ = kdata.norm_coord(xmin, ymin)
            self._xmax, self._ymax, _, _ = kdata.norm_coord(xmax, ymax)
        else:
            self._xmin = xmin
            self._xmax = xmax
            self._ymin = ymin
            self._ymax = ymax

        # Grid resolution
        self.bins = bins  # X axis
        self.hist = hist  # Y axis
        # Model
        self._model = None
        self.zk_final = None

    @property
    def xmin(self):
        """
        X min getter
        """
        return self._xmin

    @property
    def xmax(self):
        """
        X max getter
        """
        return self._xmax

    @property
    def ymin(self):
        """
        Y min getter
        """
        return self._ymin

    @property
    def ymax(self):
        """
        Y max getter
        """
        return self._ymax

    @property
    def status(self):
        """
        Print the status of the object
        """
        print(f"Data from: {self.kdata.title}")
        print(f"ntot = {self.kdata.shape[0]}")
        print("Columns:")
        print(f"   x_col = {self.kdata.x_col}")
        print(f"   y_col = {self.kdata.y_col}")
        print(f"   z_col = {self.kdata.z_col}")
        if self.kdata.normalized:
            print("Mode: Normalized (0-1000 range)")
        else:
            print("Mode: Raw (Original units)")
        print("Window:")
        print(f"xmin = {self._xmin}")
        print(f"xmax = {self._xmax}")
        print(f"ymin = {self._ymin}")
        print(f"ymax = {self._ymax}")
        print("Grid:")
        print(f"bins = {self.bins}")
        print(f"hist = {self.hist}")
        if self.model:
            print(f"Model = {self.model}")
            print(f"   zk = {self.zk_final} ")

    @property
    def models(self):
        """
        Print a detailed report of all tested models.
        """
        report_models(self.kdata)

    @property
    def model(self):
        """
        Selected model getter
        """
        return self._model

    @model.setter
    def model(self, value):
        """
        Selected model setter

        :param value: model to set
        :type value: int
        """
        self._model = value
        final_model = next(
            m for m in self.kdata.crossvaldata if m["model_idx"] == value
        )
        self.zk_final = final_model["zk"]

    def ask_model(self):
        """
        Method to ask interactivel for the model to use for the final map.
        """
        self._model = int(
            input("\nEnter the model number (MOD) you want to use for the final map: ")
        )

        final_model = next(
            m for m in self.kdata.crossvaldata if m["model_idx"] == self._model
        )
        self.zk_final = final_model["zk"]

    def estimate_grid(self, preview=False, filename="result"):
        """
        Run the grid estimation using the parent Kdata model.

        :param preview: plot a contour map preview if True, defaults to False
        :type preview: bool, optional
        :param filename: grid result filename base, defaults to "result"
        :type filename: str, optional
        """
        print(f"\n[GRID] Generating map with Model #{self.model}...")
        if preview:
            fast_preview(self.kdata, self.zk_final)
        export_grid(
            self,
            self.zk_final,
            filename=f"{filename}_{self.kdata.nork}_{self.kdata.nvec}_mod_{self.model}",
            res_x=self.bins,
            res_y=self.hist,
        )

    def __repr__(self):
        # Determine if the model has been fitted
        model_str = f"| Model: {self.model}" if self.model else "| Model: Not fitted"
        status = (
            "Normalized (0-1000 range)"
            if self.kdata.normalized
            else "Raw (Original units)"
        )
        # Build a multi-line informational string or a single compact one
        return (
            f"<pyGEKO.Kgrid | Source: '{self.kdata.title}' | Status: {status} >\n"
            f"  Window: x[{self.xmin}, {self.xmax}], y[{self.ymin}, {self.ymax}]\n"
            f"  Grid: bins={self.bins}, hist={self.hist} {model_str} >"
        )
