import os

import pandas as pd

from pygeko.utils import calc_res


class Calibrator:
    """
    Auxiliary class for converting CSV files generated with png2csv (PNGs obtained
    from https://tangrams.github.io/heightmapper/ and the like) to meters. When generating PNGs
    in HeightMapper, be sure to annotate 'max elevation', 'min elevation' from the
    dialog box and `latitude` and `zoom factor` (starts with #) from the URL.


    """

    def __init__(self, *arg, **karg):
        """
        Constructor

        All arguments are passed to `pandas.read_csv` method, the first one
        must be a `.csv` filename containing the columns that we will use
        as X, Y, and Z values.
        """
        self.orig_file = locals()["arg"][0]
        self.dframe = pd.read_csv(*arg, **karg)
        self.title = os.path.basename(arg[0])
        self.x_col = "X"
        self.y_col = "Y"
        self.z_col = "Z"
        self.hmax = None
        self.hmin = None
        self.lat = None
        self.lon = None
        self.zoom = None
        self.res = None

    @property
    def status(self):
        """Describe dataframe"""
        print(self.dframe.describe())
        print("\nSetting:")
        print(f"x_col: {self.x_col}")
        print(f"y_col: {self.y_col}")
        print(f"z_col: {self.z_col}")

    def calibXY(self, lat: float, zoom: float):
        """
        Convert columns X and Y to meters

        :param lat: Map center latitude (degrees)
        :type lat: float
        :param zoom: Web zoom level
        :type zoom: float
        """
        """"""
        res = calc_res(lat, zoom)

        self.dframe[self.x_col] = self.dframe[self.x_col] * res
        self.dframe[self.y_col] = self.dframe[self.y_col] * res

        self.lat = lat
        self.zoom = zoom
        self.res = res

    def calibZ(self, hmax: float, hmin: float):
        """
        Convert column Z to meters


        :param hmax: Maximum elevation
        :type hmax: float
        :param hmin: Minimum elevation
        :type hmin: float
        """
        # Detect whether it is 8-bit or 16-bit based on the maximum of the dataframe
        z_max_val = self.dframe[self.z_col].max()
        depth = 2**16 if z_max_val > 255 else 255

        self.dframe[self.z_col] = ((hmax - hmin) / depth) * self.dframe[
            self.z_col
        ] + hmin

        self.hmax = hmax
        self.hmin = hmin

    def save(self, filename: str):
        """
        Saves the dataframe to a CSV file

        :param filename: CSV filename base (without the .csv extension) to write
        :type filename: str
        """
        self.dframe.to_csv(filename + ".csv", index=False)

        with open(filename + ".txt", "w") as f:
            f.write(" --- Calibration parameters --- \n")
            f.write(32 * "=" + "\n")
            f.write(f"Source: {self.orig_file}\n")
            f.write(f"  Latitude: {self.lat} (deg)\n")
            f.write(f"  Longitude: {self.lon} (deg)\n") if self.lon else ""
            f.write(f"  Zoom: #{self.zoom}\n")
            f.write(f"  Hmax: {self.hmax} (m)\n")
            f.write(f"  Hmin: {self.hmin} (m)\n")
            f.write(f"  Res: {self.res} (m/px)\n")
        print(f"[OK] Saved: {filename + '.csv'} and sidecar {filename + '.txt'}")


class GRIGcalibrater(Calibrator):
    """"""

    def __init__(self, dframe, hmax, hmin, lat, zoom):
        """"""
        self.dframe = dframe
        self.x_col = "X"
        self.y_col = "Y"
        self.z_col = "Z_ESTIM"
        self.calibZ(hmax, hmin)
        self.calibXY(lat, zoom)

    def save(self):
        pass
