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
        self.title = os.path.basename(fnamebase)

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
        v_min: float = None,
        v_max: float = None,
        step_thin: float = None,
        step_thick: float = None,
        color: str = "k",
        show_scale: bool = True,
        north_angle: float = 0.0,
    ):
        """
        Plot a professional topographic map with thin and thick (labeled) contour lines.

        :param v_min: minimum Z value to map, defaults to None
        :type v_min: float, optional
        :param v_max: maximum Z value to map, defaults to None
        :type v_max: float, optional
        :param step_thin: interval for ordinary lines (e.g., 20m) defaults to None
        :type step_thin: float, optional
        :param step_thick: interval for index/master lines (e.g., 100m) defaults to None
        :type step_thick: float, optional
        :param color:  color of the lines ('k' for black, 'sienna' for classic topo, 'royalblue' for bathymetry) defaults to "k"
        :type color: str, optional
        :param show_scale: show scale bar, defaults to True
        :type show_scale: bool, optional
        :param north_angle: angle of the north arrow respect to Y axis, defaults to 0.0
        :type north_angle: float, optional
        """
        fig, ax1 = plt.subplots(1, 1, figsize=(10, 10))

        z_min_real, z_max_real = np.nanmin(self.Z), np.nanmax(self.Z)
        z_range = z_max_real - z_min_real

        # --- Interval Logic ---
        if step_thin is None:
            step_thin = self._round_to_standard(z_range / 40)
        if step_thick is None:
            step_thick = step_thin * 5

        if v_min is None:
            v_min = np.floor(z_min_real / step_thin) * step_thin
        if v_max is None:
            v_max = np.ceil(z_max_real / step_thin) * step_thin

        levels_thin = np.arange(v_min, v_max + step_thin, step_thin)
        levels_thick = np.arange(v_min, v_max + step_thick, step_thick)

        # --- Drawing Curves ---
        _ = ax1.contour(
            self.X,
            self.Y,
            self.Z,
            levels=levels_thin,
            colors=color,
            linewidths=0.4,
            alpha=0.4,
        )
        c_thick = ax1.contour(
            self.X,
            self.Y,
            self.Z,
            levels=levels_thick,
            colors=color,
            linewidths=1.2,
            alpha=0.8,
        )
        ax1.clabel(c_thick, fontsize=8, inline=True, fmt="%1.0f", inline_spacing=2)

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
                size_vertical=x_range / 1500,
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
        # --- Final Aesthetics ---
        ax1.set_aspect("equal")
        ax1.set_facecolor("white")
        ax1.set_title(
            f"Topographic Map - {self.title if hasattr(self, 'title') else ''}", pad=20
        )

        plt.tight_layout()
        plt.show()
        plt.close("all")
        gc.collect()

    def topoHB(
        self,
        v_min: float = None,
        v_max: float = None,
        step_thin: float = None,
        step_thick: float = None,
        color: str = "k",
        show_scale: bool = True,
        north_angle: float = 0.0,
        sealevel: float = 0.0,
    ):
        """
        (Experimental) Plot a professional combined hypsometric/bathymetric map with thin and thick (labeled) contour lines,
        sienna color for Z >= 0 and royalblue for Z < 0.

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
        """
        color_land = 'sienna'
        color_sea = 'royalblue'

        plot_Z = self.Z.copy()
        plot_Z -= sealevel



        fig, ax1 = plt.subplots(1, 1, figsize=(10, 10))

        z_min_real, z_max_real = np.nanmin(self.Z), np.nanmax(self.Z)
        z_range = z_max_real - z_min_real

        # --- Interval Logic ---
        if step_thin is None:
            step_thin = self._round_to_standard(z_range / 40)
        if step_thick is None:
            step_thick = step_thin * 5

        if v_min is None:
            v_min = np.floor(z_min_real / step_thin) * step_thin
        if v_max is None:
            v_max = np.ceil(z_max_real / step_thin) * step_thin

        levels_thin = np.arange(v_min, v_max + step_thin, step_thin)
        levels_thick = np.arange(v_min, v_max + step_thick, step_thick)

        # --- Drawing Curves ---
        # --- 1. Draw ORDINARY (Fine) outlines ---
        # Land (Z >= 0)
        ax1.contour(self.X, self.Y, plot_Z, 
                    levels=[lvl for lvl in levels_thin if lvl >= 0],
                    colors=color_land, linewidths=0.4, alpha=0.4)
        # Sea (Z < 0)
        ax1.contour(self.X, self.Y, plot_Z, 
                    levels=[lvl for lvl in levels_thin if lvl < 0],
                    colors=color_sea, linewidths=0.4, alpha=0.4)

        # --- 2. Draw MASTER outlines (Thick and labeled) ---
        # Land
        levels_thick_land = [lvl for lvl in levels_thick if lvl >= 0]
        if levels_thick_land:
            c_thick_land = ax1.contour(self.X, self.Y, plot_Z, 
                                       levels=levels_thick_land,
                                       colors=color_land, linewidths=1.2, alpha=0.8)
            ax1.clabel(c_thick_land, fontsize=8, inline=True, fmt='%1.0f', inline_spacing=2)

        # Sea
        levels_thick_sea = [lvl for lvl in levels_thick if lvl < 0]
        if levels_thick_sea:
            c_thick_sea = ax1.contour(self.X, self.Y, plot_Z, 
                                      levels=levels_thick_sea,
                                      colors=color_sea, linewidths=1.2, alpha=0.8)
            ax1.clabel(c_thick_sea, fontsize=8, inline=True, fmt='%1.0f', inline_spacing=2, zorder=3)

        # --- 3. Coastline (Z = 0) optionally more marked ---
        ax1.contour(self.X, self.Y, plot_Z, levels=[0], colors='k', linewidths=1.1)
        
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
                size_vertical=x_range / 1500,
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
        # --- Final Aesthetics ---
        ax1.set_aspect("equal")
        ax1.set_facecolor("white")
        ax1.set_title(
            f"Topographic Map - {self.title if hasattr(self, 'title') else ''}", pad=20
        )

        plt.tight_layout()
        plt.show()
        plt.close("all")
        gc.collect()


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
        plt.show()
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
