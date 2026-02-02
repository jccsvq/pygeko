"""GRID plotting"""

import gc
import os
import tempfile
import webbrowser

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from matplotlib import cm  # noqa: F401
from datetime import datetime

from pygeko.utils import calc_res
from pygeko.kprofile import ProfilePicker

plt.rcParams['savefig.directory'] = os.getcwd()

def set_xy_axes_equal_3d(ax: plt.Axes):
    """
    Adjust the 3D axis limits of a graph so that the aspect ratio is
    'equal' ONLY for the X and Y axes, leaving the Z axis free.

    :param ax: plt.Axes object
    :type ax: plt.Axes
    """
    x_lim = ax.get_xlim3d()
    y_lim = ax.get_ylim3d()

    x_range = abs(x_lim[1] - x_lim[0])
    x_middle = np.mean(x_lim)
    y_range = abs(y_lim[1] - y_lim[0])
    y_middle = np.mean(y_lim)

    # 1. Find the largest range only between X and Y
    plot_radius = 0.5 * max([x_range, y_range])

    # 2. Establecer los límites de X e Y usando este rango
    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])

    # 3. **IMPORTANT:** The Z-axis limits remain unchanged


class Gplot:
    """
    Plotting methods for grids
    """

    def __init__(self, fnamebase: str):
        """
        Class constructor

        :param fnamebase: `grd` and `hdr` filename base
        :type fnamebase: str
        """
        self.title = self.grd_file = os.path.basename(fnamebase)

        # Load grid data
        self.grid_df = pd.read_csv(fnamebase + ".grd", comment="#")

        # Load metadata
        self._meta = {}
        try:
            with open(fnamebase + ".hdr", "r") as f:
                for line in f:
                    if ":" in line:
                        key, val = line.strip().split(": ", 1)
                        self._meta[key] = val
        except FileNotFoundError:
            print(f"Warning: Metadata file not found {fnamebase}.hdr")

        # Extract dimensions and prepare 2D arrays for plotting
        # We use the column names defined in the exporter
        self.nx = int(self._meta.get("bins", 100))
        self.ny = int(self._meta.get("hist", 100))

        # Reshape de los datos (X, Y, Z, Sigma)
        self.X = self.grid_df["X"].values.reshape(self.ny, self.nx)
        self.Y = self.grid_df["Y"].values.reshape(self.ny, self.nx)
        self.Z = self.grid_df["Z_ESTIM"].values.reshape(self.ny, self.nx)
        self.E = self.grid_df["SIGMA"].values.reshape(self.ny, self.nx)
        # Other
        self._sealevel = None
        self.calib_dic = None

    @property
    def metadata(self):
        """
        Print grid metadata
        """
        print("\nGrid metadata:")
        for _ in self._meta:
            print("    ", _, "=", self._meta[_])

    def _format_coord(self, x: np.array, y: np.array) -> str:
        """
        Internal function to display Z values ​​when moving the cursor

        :param x: X array
        :type x: np.array
        :param y: Y array
        :type y: np.array
        :return: formated string
        :rtype: str
        """
        # Find the nearest index in the grid
        ix = np.argmin(np.abs(self.X[0, :] - x))
        iy = np.argmin(np.abs(self.Y[:, 0] - y))
        z_val = self.Z[iy, ix]
        if self._sealevel is not None:
            z_val -= self._sealevel
        e_val = self.E[iy, ix]
        return f"X={x:.2f}, Y={y:.2f} | Z={z_val:.2f}, Err={e_val:.2f}"

    def contourc(
        self,
        v_min: float = None,
        v_max: float = None,
        bad: str = "red",
    ):
        """
        Plot an interactive map of estimated Z and its errors with a continuous color map

        :param v_min: minimum Z value to map, defaults to None
        :type v_min: float, optional
        :param v_max: maximum Z value to map, defaults to None
        :type v_max: float, optional
        :param bad: bad pixels color, defaults to "red"
        :type bad: str, optional
        """
        Z_plot = self.Z.copy()
        # print(f"{v_min=}, {v_max=}, {np.nanmin(self.Z)=}, {np.nanmax(self.Z)=}, ")
        if v_min is None:
            v_min = np.nanmin(self.Z)
        if v_max is None:
            v_max = np.nanmax(self.Z)
        # self.Z = np.clip(self.Z, v_min, v_max)
        # print(f"{v_min=}, {v_max=}, {np.nanmin(self.Z)=}, {np.nanmax(self.Z)=}, ")
        Z_plot[Z_plot < v_min] = np.nan

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), sharex=True, sharey=True)

        # 1. Configure color map for Z (Relief)
        cmap_z = cm.terrain.copy()
        cmap_z.set_bad(color=bad)  # Bad pixels in RED

        # 2. Configure color map for Error (Deep Sky)
        cmap_e = cm.inferno.copy()
        cmap_e.set_bad(color="white")  # Bad pixels in WHITE

        # Draw Z Estimate
        # print(v_min, v_max)
        im1 = ax1.imshow(
            Z_plot,
            extent=[self.X.min(), self.X.max(), self.Y.min(), self.Y.max()],
            origin="lower",
            cmap=cmap_z,
            aspect="equal",
            vmin=v_min,
            vmax=v_max,
        )
        ax1.set_title("Estimated Z")
        fig.colorbar(im1, ax=ax1, label="Estimated Z")

        # Draw Standard Error
        im2 = ax2.imshow(
            self.E,
            extent=[self.X.min(), self.X.max(), self.Y.min(), self.Y.max()],
            origin="lower",
            cmap=cmap_e,
        )
        ax2.set_title("Error")
        fig.colorbar(im2, ax=ax2, label="Error")

        plt.tight_layout()
        plt.show()
        plt.close("all")
        gc.collect()

    def contourd(
        self,
        v_min: float = None,
        v_max: float = None,
        nlevels: int = 25,
    ):
        """
        Plot an interactive map of estimated Z and its errors with a discrete color map

        :param v_min: minimum Z value to map, defaults to None
        :type v_min: float, optional
        :param v_max: maximum Z value to map, defaults to None
        :type v_max: float, optional
        :param nlevels: number of levels, defaults to 25
        :type nlevels: int, optional
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), sharex=True, sharey=True)

        if v_min is None:
            v_min = np.nanmin(self.Z)
        if v_max is None:
            v_max = np.nanmax(self.Z)

        # Draw Z Estimate
        # Panel 1: Z estimated
        # Generate exactly 25 slices between v_min and v_max
        levels_cuts = np.linspace(v_min, v_max, nlevels)

        c1 = ax1.contourf(
            self.X,
            self.Y,
            self.Z,
            levels=levels_cuts,
            cmap="terrain",
            vmin=v_min,
            vmax=v_max,
            # extend="both"
        )
        fig.colorbar(c1, ax=ax1, label="Estimated Z")
        ax1.set_title("Estimated Z")
        ax1.set_aspect("equal")

        # Panel 2: Error (Sigma)
        c2 = ax2.contourf(self.X, self.Y, self.E, levels=nlevels, cmap="magma")
        fig.colorbar(c2, ax=ax2, label="Error")
        ax2.set_title("Error")
        ax2.set_aspect("equal")

        # Interactivity: Display values ​​in the status bar
        ax1.format_coord = self._format_coord
        ax2.format_coord = self._format_coord

        plt.tight_layout()
        plt.show()
        plt.close("all")
        gc.collect()

    def _round_to_standard(self, value: float) -> float:
        """
        Rounds a value to the nearest 'geographic standard' interval:
        1, 2, 5, 10, 20, 50, 100, 200, 500, 1000...

        :param value: number to round
        :type value: float
        :return: rounded value
        :rtype: float
        """
        if value <= 0:
            return 1
        # Get the order of magnitude (e.g., 135 -> 100, so magnitude is 100)
        magnitude = 10 ** np.floor(np.log10(value))
        # Normalized value between 1 and 10
        norm = value / magnitude

        # Standard steps in cartography
        steps = np.array([1, 2, 5, 10])
        # Find the closest step
        closest_step = steps[np.argmin(np.abs(steps - norm))]

        return closest_step * magnitude

    def topo(
        self,
        modeHB: bool = False,
        v_min: float = None,
        v_max: float = None,
        step_thin: float = None,
        step_thick: float = None,
        color: str = "k",
        show_scale: bool = True,
        north_angle: float = 0.0,
        sealevel: float = 0.0,
        hillshade: bool = False,
        azimuth: float = 315.0,
        alt: float = 45.0,
        out_file: str = None,
        interactive: bool = False,
    ):
        """
        Plot a professional topographic map. Supports combined hypsometric/bathymetric
        colors (Sienna/RoyalBlue) and Hillshading.

        :param modeHB: hypsometric/bathymetric mode, defaults to False
        :type modeHB: bool, optional
        :param v_min: minimum Z value to map, defaults to None
        :type v_min: float, optional
        :param v_max: maximum Z value to map, defaults to None
        :type v_max: float, optional
        :param step_thin: interval for ordinary lines (e.g., 20m) defaults to None
        :type step_thin: float, optional
        :param step_thick: interval for index/master lines (e.g., 100m) defaults to None
        :type step_thick: float, optional
        :param color:  color of the bar line defaults to "k"
        :type color: str, optional
        :param show_scale: show scale bar, defaults to True
        :type show_scale: bool, optional
        :param north_angle: angle of the north arrow respect to Y axis, defaults to 0.0
        :type north_angle: float, optional
        :param sealevel: sea level, defaults to 0.0
        :type sealevel: float, optional
        :param hillshade: add hillshade, defaults to False
        :type hillshade: bool, optional
        :param azimuth: azimuth of the hillshade, defaults to 315
        :type azimuth: float, optional
        :param alt: altitude of the hillshade, defaults to 45
        :type alt: float, optional
        :param out_file: output file name, defaults to None
        :type out_file: str, optional
        :param interactive: interactive mode for profiles, defaults to False
        :type interactive: bool, optional
        """
        # 0. Capture the input arguments immediately
        params = locals().copy()
        params.pop("self", None)

        # 1. --- INITIAL SETUP ---
        color_land, color_sea = ("sienna", "royalblue") if modeHB else (color, color)
        self._sealevel = sealevel  # for format_coord

        fig, ax1 = plt.subplots(1, 1, figsize=(10, 10))

        # 2. --- BACKGROUND LAYER: HILLSHADE ---
        if hillshade:
            from matplotlib.colors import LightSource

            # Limits
            x0, x1 = np.nanmin(self.X), np.nanmax(self.X)
            y0, y1 = np.nanmin(self.Y), np.nanmax(self.Y)

            # We define the light source
            ls = LightSource(azdeg=azimuth, altdeg=alt)
            shaded = ls.hillshade(self.Z, vert_exag=1.0)

            # Orientation correction for shading
            if self.Y[0, 0] > self.Y[-1, 0]:
                shaded = np.flipud(shaded)

            ax1.imshow(
                shaded,
                extent=[x0, x1, y0, y1],
                cmap="gray",
                origin="lower",
                alpha=0.25,
                interpolation="bilinear",
            )
            # Water dough (optional)
            if modeHB:
                ax1.contourf(
                    self.X,
                    self.Y,
                    self.Z,
                    levels=[-99999, sealevel],
                    colors=["#aaccff"],
                    alpha=0.3,
                )

        # 3. --- Level Logic ---
        z_rel = self.Z - sealevel
        z_min, z_max = np.nanmin(z_rel), np.nanmax(z_rel)
        z_range = z_max - z_min

        if step_thin is None:
            step_thin = self._round_to_standard(z_range / 40)
        if step_thick is None:
            step_thick = step_thin * 5

        # Limit setting
        v_min = v_min if v_min is not None else np.floor(z_min / step_thin) * step_thin
        v_max = v_max if v_max is not None else np.ceil(z_max / step_thin) * step_thin

        levels_thin = np.arange(v_min, v_max + step_thin, step_thin)
        levels_thick = np.arange(v_min, v_max + step_thick, step_thick)

        # 4. --- CONTOUR DRAWING ---
        # Ordinary
        ax1.contour(
            self.X,
            self.Y,
            z_rel,
            levels=[_ for _ in levels_thin if _ >= 0],
            colors=color_land,
            linewidths=0.4,
            alpha=0.4,
        )
        ax1.contour(
            self.X,
            self.Y,
            z_rel,
            levels=[_ for _ in levels_thin if _ < 0],
            colors=color_sea,
            linewidths=0.4,
            alpha=0.4,
        )

        # Master
        l_thick_land = [_ for _ in levels_thick if _ >= 0]
        if l_thick_land:
            c_land = ax1.contour(
                self.X,
                self.Y,
                z_rel,
                levels=l_thick_land,
                colors=color_land,
                linewidths=1.2,
                alpha=0.8,
            )
            ax1.clabel(c_land, fontsize=8, inline=True, fmt="%1.0f")

        l_thick_sea = [_ for _ in levels_thick if _ < 0]
        if l_thick_sea:
            c_sea = ax1.contour(
                self.X,
                self.Y,
                z_rel,
                levels=l_thick_sea,
                colors=color_sea,
                linewidths=1.2,
                alpha=0.8,
            )
            ax1.clabel(c_sea, fontsize=8, inline=True, fmt="%1.0f")

        # Coastline (Z = 0) optionally more marked
        if modeHB:
            ax1.contour(
                self.X,
                self.Y,
                z_rel,
                levels=[0],
                colors="k",
                linewidths=1.1,
            )

        # --- Graphic Scale ---
        if show_scale:
            from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
            import matplotlib.font_manager as fm

            x_range = np.nanmax(self.X) - np.nanmin(self.X)
            s_len = self._round_to_standard(x_range * 0.2)
            label = f"{s_len:g} m" if s_len < 1000 else f"{s_len / 1000:g} km"
            bar = AnchoredSizeBar(
                ax1.transData,
                s_len,
                label,
                "lower right",
                pad=0.8,
                color=color,
                frameon=False,
                size_vertical=x_range / 200,
                fontproperties=fm.FontProperties(size=10, weight="bold"),
            )
            ax1.add_artist(bar)

        # --- North Arrow (Infallible Vector Version) ---
        if north_angle is not None:
            # Compass center at fraction coordinates (0.08, 0.88)
            nx, ny = 0.08, 0.88

            # Convert angle to radians (Matplotlib uses clockwise, we compensate)
            # North (0°) should point upwards (90° on the unit circle)
            rad = np.radians(90 - north_angle)

            # Arrow length
            L = 0.05

            # We calculate the arrowhead vector
            dx = L * np.cos(rad)
            dy = L * np.sin(rad)

            # We draw the arrow using annotate but as a pure vector
            ax1.annotate(
                "",
                xy=(nx + dx, ny + dy),
                xycoords="axes fraction",
                xytext=(nx, ny),
                textcoords="axes fraction",
                arrowprops=dict(arrowstyle="->", color=color, lw=2, mutation_scale=20),
            )

            # We put the 'N' a little further beyond the tip so that it doesn't bump into anything
            ax1.text(
                nx + dx * 1.3,
                ny + dy * 1.3,
                "N",
                transform=ax1.transAxes,
                ha="center",
                va="center",
                weight="bold",
                color=color,
                fontsize=12,
            )
        # Interactivity: Display values ​​in the status bar
        ax1.format_coord = self._format_coord
        # --- Final Aesthetics ---
        ax1.set_aspect("equal")
        ax1.set_facecolor("white")
        ax1.set_title(
            f"Topographic Map - {self.title if hasattr(self, 'title') else ''}", pad=20
        )

        plt.tight_layout()

        # Save map to disk
        if out_file:
            plt.savefig(out_file, dpi=300, bbox_inches="tight")
            print(f"Map saved to {out_file}")
            # Write map metadata
            base_name = out_file.rsplit(".", 1)[0]
            sidecar_name = f"{base_name}_meta.txt"
            with open(sidecar_name, "w") as f:
                f.write(
                    f"pyGEKO Map Metadata - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                )
                f.write("-" * 50 + "\n")
                f.write(f"Title:        {self.title}\n")
                # Add the parameters passed when calling topo()
                for key, value in params.items():
                    # Avoid putting the out_file in its own report
                    if key != "out_file" and value is not None:
                        f.write(f"{key.capitalize()}: {value}\n")
                f.write("-" * 50 + "\n")
                f.write("Grid metadata:\n")
                f.write(f"Grid file: {self.grd_file}\n")
                for _ in self._meta:
                    f.write("    " + _ + "=" + self._meta[_] + "\n")
                if self.calib_dic is not None:
                    f.write("-" * 50 + "\n")
                    f.write("Calibration metadata:\n")
                    for _ in self.calib_dic:
                        f.write("    " + _ + "=" + str(self.calib_dic[_]) + "\n")
            print(f"Map sidecar '{sidecar_name}' saved.")
        if interactive:
        # Instead of plt.show(), we initialize the picker and then show
            from .kprofile import ProfilePicker
            ax = plt.gca()
            self._active_picker = ProfilePicker(ax, self)
            plt.show() # This will now block, but the picker is already active
        else:
            plt.show()
        # plt.close("all")
        self._sealevel = None
        # gc.collect()

    def zsurf(self):
        """
        3D surface of the estimated Z
        """
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(
            self.X, self.Y, self.Z, cmap="terrain", edgecolor="none", antialiased=True
        )
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        set_xy_axes_equal_3d(ax)  # X-Y axes equal scale !
        ax.set_title("Kriged " + self._meta["z_col"] + " " + self.title)
        ax.set_zlabel(self._meta["z_col"])
        ax.set_xlabel(self._meta["x_col"])
        ax.set_ylabel(self._meta["y_col"])
        # Force equal scaling in X-Y (limited in Matplotlib 3D, but it helps)
        ax.set_aspect("auto")
        plt.show(block=False)
        plt.close("all")
        gc.collect()

    def esurf(self):
        """
        3D surface of the estimated Z errors
        """
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(
            self.X, self.Y, self.E, cmap="magma", edgecolor="none", antialiased=True
        )
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        set_xy_axes_equal_3d(ax)  # X-Y axes equal scale !
        ax.set_title("Standard Error " + self.title)
        ax.set_xlabel(self._meta["x_col"])
        ax.set_ylabel(self._meta["y_col"])

        plt.show()
        plt.close("all")
        gc.collect()

    def zsurf_gpu(
        self,
        z_floor: float = None,
        v_exag: float = 0.5,
        cmap: str = "earth",
        contours: bool = False,
    ):
        """
        Smooth rendering using WebGL and your GPU

        :param z_floor: plot only above this value, defaults to None
        :type z_floor: float, optional
        :param v_exag: vertical exageration factor, defaults to 0.5
        :type v_exag: float, optional
        :param cmap: plotly color map name, defaults to "earth"
        :type cmap: str, optional
        :param contours: add contours, defaults to False
        :type contours: bool, optional

        """
        # Optional: To make the surface "die" at the ground instead of sinking
        # Z_plot = self.Z.copy()
        # Z_plot[Z_plot < z_floor] = np.nan # NaNs in Plotly create gaps or clean cuts
        if z_floor is None:
            z_floor = np.nanmin(self.Z)
        fig = go.Figure(
            data=[go.Surface(z=self.Z, x=self.X, y=self.Y, colorscale=cmap)]
        )
        range_x = self.X.max() - self.X.min()
        range_y = self.Y.max() - self.Y.min()
        if contours:
            fig.update_traces(
                contours_z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project_z=True,
                )
            )
        fig.update_layout(
            title="Estimated Z 3D (GPU Accelerated)",
            autosize=True,
            scene=dict(
                zaxis=dict(range=[z_floor, np.nanmax(self.Z) * 1.2]),
                aspectratio=dict(x=1, y=range_y / range_x, z=v_exag),
            ),
        )
        fig.show()
        gc.collect()
        # return fig

    def zsurf_gpu_PI(
        self,
        z_floor: float = None,
        v_exag: float = 0.5,
        cmap: str = "earth",
        contours: bool = False,
    ):
        """
        Renders the 3D surface using WebGL and opens it in the system's browser.
        Optimized for remote VNC sessions and Raspberry Pi 5.

        :param z_floor: plot only above this value, defaults to None
        :type z_floor: float, optional
        :param v_exag: vertical exageration factor, defaults to 0.5
        :type v_exag: float, optional
        :param cmap: plotly color map name, defaults to "earth"
        :type cmap: str, optional
        :param contours: add contours, defaults to False
        :type contours: bool, optional
        """

        if z_floor is None:
            z_floor = np.nanmin(self.Z)
        # 1. Generate the figure
        fig = go.Figure(
            data=[go.Surface(z=self.Z, x=self.X, y=self.Y, colorscale=cmap)]
        )
        range_x = self.X.max() - self.X.min()
        range_y = self.Y.max() - self.Y.min()

        if contours:
            fig.update_traces(
                contours_z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project_z=True,
                )
            )
        fig.update_layout(
            title="Estimated Z 3D (GPU Accelerated)",
            autosize=True,
            scene=dict(
                zaxis=dict(range=[z_floor, np.nanmax(self.Z) * 1.2]),
                aspectratio=dict(x=1, y=range_y / range_x, z=v_exag),
            ),
        )

        # 2. Define path in temporary directory
        # We use tempfile to make it cross-platform (i7 and Pi)
        temp_file = os.path.join(tempfile.gettempdir(), "gck_3d_view.html")

        # 3. Export toa HTML
        fig.write_html(
            temp_file,
            auto_open=False,
            include_plotlyjs="cdn",
            post_script="window.dispatchEvent(new Event('resize'));",
        )

        # 4. Non-blocking opening according to the Operating System
        print("[GPU-VIEW] Opening viewer in browser...")

        try:
            if os.name == "posix":  # Linux (Debian on i7 and Pi)
                # xdg-open sends the file to the default browser and releases the terminal
                os.system(f"xdg-open {temp_file} > /dev/null 2>&1 &")
            else:
                # Windows option
                webbrowser.open(f"file://{os.path.realpath(temp_file)}")

        except Exception as e:
            print(f"Error trying to open the browser: {e}")
            print(f"You can open the file manually in: {temp_file}")

    def save_zsurf(
        self,
        filename: str = None,
        z_floor: float = None,
        v_exag: float = 0.5,
        cmap: str = "earth",
        contours: bool = False,
    ):
        """Export the interactive 3D model to a separate HTML file.

        :param filename: filename, defaults to self.title + "_3d_model"
        :type filename: str, optional
        :param z_floor: plot only above this value, defaults to None
        :type z_floor: float, optional
        :param v_exag: vertical exageration factor, defaults to 0.5
        :type v_exag: float, optional
        :param cmap: plotly color map name, defaults to "earth"
        :type cmap: str, optional
        :param contours: add contours, defaults to False
        :type contours: bool, optional
        """

        if filename is None:
            filename = self.title + "_3d_model"
        if z_floor is None:
            z_floor = np.nanmin(self.Z)

        # 1. Create the figure (same logic as zsurf_gpu)
        range_x = self.X.max() - self.X.min()
        range_y = self.Y.max() - self.Y.min()

        fig = go.Figure(
            data=[
                go.Surface(
                    z=self.Z,
                    x=self.X,
                    y=self.Y,
                    colorscale=cmap,
                    lighting=dict(
                        ambient=0.4, diffuse=0.5, roughness=0.9, specular=0.1
                    ),
                    colorbar=dict(title="Estimated Z"),
                )
            ]
        )

        if contours:
            fig.update_traces(
                contours_z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project_z=True,
                )
            )
        fig.update_layout(
            title="Estimated Z - Interactive 3D Model",
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                zaxis=dict(range=[z_floor, np.nanmax(self.Z) * 1.2]),
                aspectratio=dict(x=1, y=range_y / range_x, z=v_exag),
            ),
            margin=dict(l=0, r=0, b=0, t=40),
        )

        # 2. Save as HTML
        output_file = f"{filename}.html"
        fig.write_html(output_file)
        print(f"3D model successfully exported to: {output_file}")

    def __repr__(self):
        # Verificamos si hay datos cargados para evitar errores si el grid está vacío
        status = "Ready" if self.Z is not None else "Empty (No grid estimated)"
        shape = f"{self.Z.shape}" if self.Z is not None else "N/A"

        return (
            f"<pyGEKO.Gplot | Status: {status} | "
            f"Grid Shape: {shape} | "
            f"Source: '{self.title}'>"
        )

    def calibrate(
        self,
        hmax: float,
        hmin: float,
        lat: float,
        zoom: float,
        invertY: bool = False,
    ):
        """
        Grid calibration if it was obtained from csv data from `png2csv` that were not previously calibrated.

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

        self.X = self.X * res
        self.Y = self.Y * res
        if invertY:
            #self.Y = self.Y.max() - self.Y
            self.Z = np.flipud(self.Z)
            self.E = np.flipud(self.E)

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


    def _interpolate_at(self, x: float, y: float, matrix: np.ndarray) -> float:
            """
            Performs bilinear interpolation on a matrix given real x, y coordinates.
            
            :param x: Real X coordinate
            :param y: Real Y coordinate
            :param matrix: The 2D array (self.Z or self.E) to sample from
            :return: Interpolated value (float)
            """
            # Get grid bounds
            x_min, x_max = self.X.min(), self.X.max()
            y_min, y_max = self.Y.min(), self.Y.max()
            #print(x_min, x_max, y_min, y_max)
            
            # Out-of-bounds protection
            if not (x_min <= x <= x_max and y_min <= y <= y_max):
                return np.nan
            
            # Convert real coordinates to fractional index positions
            # self.nx and self.ny are the grid dimensions
            frac_x = (x - x_min) / (x_max - x_min) * (self.nx - 1)
            frac_y = (y - y_min) / (y_max - y_min) * (self.ny - 1)
            
            # Identify the 4 surrounding pixel indices
            x0 = int(np.floor(frac_x))
            x1 = min(x0 + 1, self.nx - 1)
            y0 = int(np.floor(frac_y))
            y1 = min(y0 + 1, self.ny - 1)
            
            # Calculate weights (distance from the floor index)
            dx = frac_x - x0
            dy = frac_y - y0
            
            # Matrix values at the 4 corners
            # Note: matrix indexing is usually [row, col] -> [y, x]
            v00 = matrix[y0, x0]
            v10 = matrix[y0, x1]
            v01 = matrix[y1, x0]
            v11 = matrix[y1, x1]
            
            # Bilinear interpolation formula
            res = (v00 * (1 - dx) * (1 - dy) +
                v10 * dx * (1 - dy) +
                v01 * (1 - dx) * dy +
                v11 * dx * dy)
            return res

    def profile(self, start: tuple, end: tuple, n_points: int = 100) -> dict:
            """
            Extracts a topographic profile between two points.
            
            :param start: (x, y) starting coordinates
            :param end: (x, y) ending coordinates
            :param n_points: Number of sampling points along the line
            :return: Dictionary containing distance, z, e and coordinates
            """
            x1, y1 = start
            x2, y2 = end
            
            # Linear sampling of X and Y coordinates
            x_pts = np.linspace(x1, x2, n_points)
            y_pts = np.linspace(y1, y2, n_points)
            
            # Cumulative distance from the start point
            distances = np.sqrt((x_pts - x1)**2 + (y_pts - y1)**2)
            
            z_values = []
            e_values = []
            
            # Sampling Z and E (Error) from the grid
            for px, py in zip(x_pts, y_pts):
                z_values.append(self._interpolate_at(px, py, self.Z))
                e_values.append(self._interpolate_at(px, py, self.E))
                #print(f"Sampling at X={px:.1f}, Y={py:.1f}")
                
            return {
                "distance": distances,
                "z": np.array(z_values),
                "e": np.array(e_values),
                "x_coords": x_pts,
                "y_coords": y_pts
            }


    def plot_profile(self, p_data: dict, title: str = "Z Profile"):
            """
            Plots the profile and displays start/end coordinates.
            """
            import matplotlib.pyplot as plt
            
            fig_name = "pyGEKO_Profile_Analysis"
            fig = plt.figure(num=fig_name, figsize=(10, 6)) # Un poco más alto para el subtítulo
            
            if fig.axes:
                ax = fig.gca()
                ax.clear()
            else:
                ax = fig.add_subplot(111)

            dist = p_data["distance"]
            z = p_data["z"]
            e = p_data["e"]
            x_pts = p_data["x_coords"]
            y_pts = p_data["y_coords"]

            # Plot uncertainty and elevation
            ax.fill_between(dist, z - e, z + e, color='lightblue', alpha=0.4, label='Uncertainty (±σ)')
            ax.plot(dist, z, color='darkgreen', lw=2, label='Z')
            
            # Add labels and grid
            ax.set_title(title, fontsize=14, pad=20)
            
            # --- NEW: DISPLAY START AND END COORDINATES ---
            # We create a string with the start and end points
            start_txt = f"Start: ({x_pts[0]:.1f}, {y_pts[0]:.1f})"
            end_txt = f"End: ({x_pts[-1]:.1f}, {y_pts[-1]:.1f})"
            
            # We can place this as a 'suptitle' or as a text box
            fig.suptitle(f"{start_txt}  --->  {end_txt}", fontsize=9, color='gray', y=0.92)
            # ----------------------------------------------

            ax.set_xlabel("Distance along section")
            ax.set_ylabel("Z")
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='upper right')
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to make room for suptitle
            fig.canvas.draw()
            
            try:
                fig.canvas.manager.show()
            except Exception as e:
                pass

    def plot_profile2(self, p_data: dict, title: str = "Z Profile"):
            """
            Plots the profile, reusing the window if it already exists.
            """
            import matplotlib.pyplot as plt
            
            # Use a unique window name. 
            # If a window with this name exists, Matplotlib will switch to it.
            fig_name = "pyGEKO_Profile_Analysis"
            
            # If the window exists, we get its ID; if not, it creates a new one.
            fig = plt.figure(num=fig_name, figsize=(10, 5))
            
            # If the figure was already open, it will have axes. 
            # We clear them to draw the new profile.
            if fig.axes:
                ax = fig.gca()
                ax.clear()
            else:
                ax = fig.add_subplot(111)

            dist = p_data["distance"]
            z = p_data["z"]
            e = p_data["e"]
            
            # Plotting the uncertainty and the terrain
            ax.fill_between(dist, z - e, z + e, color='lightblue', alpha=0.4, label='Uncertainty (±σ)')
            ax.plot(dist, z, color='darkgreen', lw=2, label='Z')
            
            ax.set_title(title)
            ax.set_xlabel("Distance")
            ax.set_ylabel("Z")
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()
            # Add a vertical line at the peak or show min/max elevation
            #max_z = np.max(z)
            #max_dist = dist[np.argmax(z)]
            #ax.annotate(f'Peak: {max_z:.1f}m', xy=(max_dist, max_z), 
            #            xytext=(max_dist, max_z + 100),
            #            arrowprops=dict(facecolor='black', shrink=0.05))
            
            # Refresh the canvas without blocking
            fig.canvas.draw()
            
            # Bring to front if possible
            try:
                fig.canvas.manager.show()
            except Exception as e:
                pass

    def interactive_profile(self, n_points: int = 200):
            """
            Enables interactive profile selection on the current active plot.
            """
            import matplotlib.pyplot as plt
            
            ax = plt.gca() # Get current axes
            # Store the picker in an attribute to prevent garbage collection
            self._active_picker = ProfilePicker(ax, self, n_points)
            plt.show()