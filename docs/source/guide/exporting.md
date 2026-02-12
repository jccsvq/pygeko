# Exporting Results

`pyGEKO` is designed to fit into a professional GIS (Geographic Information System) workflow. While it maintains its internal metadata system, it can export high-fidelity rasters for immediate use in software like QGIS or ArcGIS.

## Supported Formats

When you run an estimation and save your results, `pyGEKO` generates:

1. **The Metadata Sidecar (.gck/.hdr):** Stores Kriging parameters and error metrics.
2. **The ESRI ASCII (.asc):** A universal raster format generated via the [`Gplot.export_asc()`](#GIS-integration) method.

## Exporting to GIS (ESRI ASCII)

The `export_asc()` method is the preferred way to move your data into QGIS. It handles coordinates, flips the grid to align with Northern orientation, and creates projection files.

### 1. Automatic Georeferencing

If you have calibrated your project using the built-in Heightmapper support:

```python
gp.export_asc(paste_sigma=True)

```

This produces `.asc` files and a `.prj` file (EPSG:3857). QGIS will automatically "fly" to the correct global location (e.g., Mount St. Helens).

### 2. Manual and Pre-calibrated Data

If your data is already in a specific metric system (like UTM):

```python
gp.export_asc(xll=542000.0, yll=4125000.0)

```

*Note: You will need to manually set the Coordinate Reference System in your GIS software as no `.prj` is generated for custom metric offsets.*

## Advanced: Custom Calibration and Method Binding

`pyGEKO` is highly extensible. You can replace the default calibration logic with your own. However, because `calibrate` is a method of the `Gplot` class, you must manually **bind** your custom function to the instance using Python's descriptor protocol.

### The Correct Way to Bind

If you simply assign a function to an instance (`gp.calibrate = my_func`), Python will not pass the `self` argument automatically. You must use the `.__get__` method/descriptor:

```python
from pygeko import Gplot

def my_custom_calib(self, **kwargs):
    # Your logic here
    self.calib_dic = {
        "CRS": "EPSG:3857", # Trigger .prj generation
        "xllcorner": 123456.7,
        "yllcorner": 765432.1,
        # ... other metadata ...
    }

gp = Gplot("my_experiment")
# Bind the function as a method of the instance
gp.calibrate = my_custom_calib.__get__(gp, Gplot)

gp.calibrate(custom_param="value")

```

> **Warning:** If your data uses the Web Mercator projection and you want to trigger automatic `.prj` file creation in `export_asc()`, your custom `calib_dic` **must** include the key `"CRS": "EPSG:3857"` and provide `xllcorner` and `yllcorner` values.

Of course, you can also choose to use [inheritance](#custom-calibration).

## Importing to QGIS

1. Open QGIS and simply **drag and drop** the generated `.asc` file.
2. If a `.prj` file is present, the layer will be positioned automatically.
3. Go to **Layer Properties -> Symbology** and set the **Render type** to *Singleband pseudocolor* to visualize the elevation relief.

