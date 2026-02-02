"""
pyGEKO Kprofile Module
-------------------
Handles profile definition and Kriging estimation.
"""

# import matplotlib.pyplot as plt
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# import pygeko.kdata
from pygeko.utils import calc_res, export_profile, report_models

plt.rcParams['savefig.directory'] = os.getcwd()

class ProfilePicker:
    """
    Interactive tool to select two points on a Gplot map and generate a profile.
    """

    def __init__(self, ax, gplot_obj, n_points=200):
        self.ax = ax
        self.gp = gplot_obj
        self.n_points = n_points
        self.points = []
        self.line = None
        # Connect the click event
        self.cid = ax.figure.canvas.mpl_connect("button_press_event", self.on_click)
        print("📍 Profile Mode: Click two points on the map to define the section.")

    def on_click(self, event):
        # Ignore clicks outside the axes
        if event.inaxes != self.ax:
            return

        self.points.append((event.xdata, event.ydata))

        # Mark the point on the map
        self.ax.plot(event.xdata, event.ydata, "ro", markersize=5)
        self.ax.figure.canvas.draw()

        if len(self.points) == 2:
            # Draw the final line between points
            x_vals = [self.points[0][0], self.points[1][0]]
            y_vals = [self.points[0][1], self.points[1][1]]

            if self.line:
                self.line[0].remove()
            self.line = self.ax.plot(x_vals, y_vals, "r--", lw=2)
            self.ax.figure.canvas.draw()

            # Calculate and plot the profile
            print(
                f"✅ Points selected: ({self.points[0][0]:.2f}, {self.points[0][1]:.2f}) "
                f"to ({self.points[1][0]:.2f}, {self.points[1][1]:.2f})"
            )
            data = self.gp.profile(self.points[0], self.points[1], self.n_points)
            self.gp.plot_profile(data)

            # Reset for next selection or disconnect
            self.points = []


class Kprofile:
    """Manages profile definition and interpolation workflow using Kriging."""

    def __init__(self, kdata, points: list, step: float = None, n_points: int = 100):
        """
        Object Creator

        :param kdata: Kdata object with the source points
        :param points: List of (x, y) tuples defining the polyline vertices
        :param step: Distance between sampling points (in meters/units)
        :param n_points: Number of points if 'step' is not provided
        """
        from .kdata import Kdata  # Local import to avoid circular dependency

        assert isinstance(kdata, Kdata)

        self.kdata = kdata
        # Store original vertices for metadata purposes
        self._vertices = points.copy()

        self._model = None
        self.zk_final = None  # This will store the fitted model info
        self.results = None  # To store dist, z, e after estimation

        # --- Generate Sampling Points along the Polyline ---
        self._x, self._y, self._dist = self._build_path(points, step, n_points)
        self._total_length = self._dist[-1]

        # Normalize the Sampling Points if necessary
        if kdata.normalized:
            self._x, self._y, _, _ = kdata.norm_coord(self._x, self._y)

    def _build_path(self, vertices, step, n_points):
        """
        Discretizes a polyline into equidistant sampling points.
        """
        x_coords, y_coords = zip(*vertices)
        x_coords = np.array(x_coords)
        y_coords = np.array(y_coords)

        # Calculate distances between vertices
        dx = np.diff(x_coords)
        dy = np.diff(y_coords)
        seg_dist = np.sqrt(dx**2 + dy**2)
        cum_dist = np.insert(np.cumsum(seg_dist), 0, 0)
        total_length = cum_dist[-1]

        # Determine sampling distances
        if step:
            sampling_dists = np.arange(0, total_length, step)
            # Ensure the last point is included
            if sampling_dists[-1] < total_length:
                sampling_dists = np.append(sampling_dists, total_length)
        else:
            sampling_dists = np.linspace(0, total_length, n_points)

        # Interpolate X and Y along the path
        path_x = np.interp(sampling_dists, cum_dist, x_coords)
        path_y = np.interp(sampling_dists, cum_dist, y_coords)

        return path_x, path_y, sampling_dists

    @property
    def models(self):
        """
        Print a detailed report of all tested models.
        """
        report_models(self.kdata)

    @property
    def model(self):
        """Selected model getter"""
        return self._model

    @model.setter
    def model(self, value):
        """Selected model setter and logic to link with cross-validation results"""
        self._model = value
        # Link the chosen model from kdata cross-validation
        try:
            final_model = next(
                m for m in self.kdata.crossvaldata if m["model_idx"] == value
            )
            self.zk_final = final_model["zk"]  # Stores range, sill, nugget, etc.
        except StopIteration:
            print(f"⚠️ Model index {value} not found in Kdata cross-validation.")

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
            print("Normalized (0-1000 range)")
        else:
            print("Raw (Original units)")
        print(f"vertices: {self._vertices}")
        print(f"total_length: {self._total_length}")
        print(f"nork: {self.kdata.nork}")
        print(f"nvec: {self.kdata.nvec}")
        if self.model:
            print(f"Model = {self.model}")
            print(f"   zk = {self.zk_final} ")

    def estimate_profile(self, filename="profile"):
        """
        Run the profile estimation using the parent Kdata model.
        """
        if self.model is None or self.zk_final is None:
            raise ValueError("Model must be set before estimation.")

        print(f"\n[PROFILE] Generating profile with model #{self.model}...")

        # We build the filename according to your specification
        full_name = f"{filename}_{self.kdata.nork}_{self.kdata.nvec}_mod_{self.model}"

        export_profile(self, self.zk_final, filename=full_name)


class KprofileCSV(Kprofile):
    """Profile defined by an external CSV file with X, Y coordinates."""

    def __init__(self, kdata, csv_path, **kwargs):
        import pandas as pd

        df = pd.read_csv(csv_path)
        # Assumes CSV has columns 'X' and 'Y'
        points = list(zip(df["X"], df["Y"]))
        super().__init__(kdata, points, **kwargs)


class Pplot:
    """Profile ploting"""

    def __init__(self, filename: str):
        """Object Creator

        :param filename: filename base of the profile
        :type filename: str
        """
        self.title = self.grd_file = os.path.basename(filename)

        # Load grid data
        self.df = pd.read_csv(filename + ".prf", comment="#")

        # Load metadata
        self._meta = {}
        try:
            with open(filename + ".hdr", "r") as f:
                for line in f:
                    if ":" in line:
                        key, val = line.strip().split(": ", 1)
                        self._meta[key] = val
        except FileNotFoundError:
            print(f"Warning: Metadata file not found {filename}.hdr")

        # Parse vertices from string if available in metadata
        if "vertices" in self._meta:
            try:
                # Converts string "[(x1,y1), ...]" back to list
                self.vertices = eval(self._meta["vertices"])
            except Exception:
                self.vertices = None

        # Reshape de los datos (X, Y, Z, Sigma)
        self.X = self.df["X"].values
        self.Y = self.df["Y"].values
        self.Z = self.df["Z_ESTIM"].values
        self.E = self.df["SIGMA"].values

        # --- Calculate cumulative distance along the path ---
        dx = np.diff(self.X)
        dy = np.diff(self.Y)
        segment_distances = np.sqrt(dx**2 + dy**2)
        # We start at distance 0.0
        self.dist = np.insert(np.cumsum(segment_distances), 0, 0.0)

        # Other
        #self._sealevel = None
        self.calib_dic = None

    @property
    def metadata(self):
        """
        Print profile metadata
        """
        print("\nProfile metadata:")
        for _ in self._meta:
            print("    ", _, "=", self._meta[_])

    def calibrate(
        self,
        hmax: float,
        hmin: float,
        lat: float,
        zoom: float,
        invertY: bool = False,
    ):
        """
        Profile calibration if it was obtained from csv data from `png2csv` that were not previously calibrated.

        :param hmax: Maximun elevation
        :type hmax: float
        :param hmin: Minimum elevation
        :type hmin: float
        :param lat: latitude of the grid center
        :type lat: float
        :param zoom: zoom level of the grid
        :type zoom: float
        :param invertY: Invert Y axis, defaults to False
        :type invertY: bool, optional
        """
        res = calc_res(
            lat,
            zoom,
        )

        # self.X = self.X * res
        # self.Y = self.Y * res
        self.dist = self.dist * res

        # if invertY:
        # self.Y = np.nanmax(self.Y) - self.Y
        # self.Z = npmax() - self.Y
        # self.Z = np.flipud(self.Z)
        # self.E = np.flipud(self.E)

        z_max_val = np.nanmax(self.Z)
        depth = 2**16 if z_max_val > 255 else 255

        self.Z = ((hmax - hmin) / depth) * self.Z + hmin
        self.E = ((hmax - hmin) / depth) * self.E
        self.calib_dic = {
            "hmin": hmin,
            "hmax": hmax,
            "depth": depth,
            "res": float(res),
            "invertY": invertY,
            "lat": lat,
            "zoom": zoom,
        }

    def plot(self, show_error=True, title=None, show_flags=True, sea_level=None):
        """
        Plots the profile with standard aesthetic and optional vertex flags.
        """

        fig, ax = plt.subplots(figsize=(12, 5))
        plot_title = title if title else f"Profile: {self.title}"

        temp_Z = self.Z.copy()
        temp_Z = temp_Z - sea_level if sea_level is not None else temp_Z

        # 1. Uncertainty and Elevation (same as before)
        if show_error:
            ax.fill_between(
                self.dist,
                temp_Z - self.E,
                temp_Z + self.E,
                color="lightblue",
                alpha=0.4,
                label="Uncertainty (±σ)",
            )

        ax.plot(self.dist, temp_Z, color="darkgreen", lw=2, label="Z")
        if sea_level is not None:
            ax.axhline(y=0, color="#000080", linestyle="--", alpha=0.5, lw=2)

        # 2. Add Flags (Vertices)
        if show_flags and hasattr(self, "vertices") and self.vertices:
            # Calculate cumulative distances for the original vertices
            v_x, v_y = zip(*self.vertices)
            v_dx = np.diff(v_x)
            v_dy = np.diff(v_y)
            v_seg_dist = np.sqrt(v_dx**2 + v_dy**2)
            v_cum_dist = np.insert(np.cumsum(v_seg_dist), 0, 0.0)

            if self.calib_dic:
                v_cum_dist *= self.calib_dic["res"]

            for i, d in enumerate(v_cum_dist):
                # Draw vertical dashed line
                ax.axvline(x=d, color="red", linestyle="--", alpha=0.5, lw=1)

                # Find elevation at this vertex to place the label
                # We use np.interp to find the Z exactly at the vertex distance
                # z_at_v = np.interp(d, self.dist, self.Z)

                # Add label (P0, P1, P2...)
                ax.text(
                    d,
                    ax.get_ylim()[1],
                    f" V{i}",
                    color="red",
                    verticalalignment="top",
                    fontsize=9,
                    fontweight="bold",
                )

        # Formatting
        ax.set_title(plot_title, fontsize=14)
        ax.set_xlabel("Cumulative Distance")
        ax.set_ylabel("Z")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="best")

        plt.tight_layout()
        plt.show()
