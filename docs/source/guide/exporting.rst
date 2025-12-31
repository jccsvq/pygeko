Exporting Results
=================

pyGEKO is designed to fit into a wider GIS (Geographic Information System) workflow. 

Supported Formats
-----------------

When you run an estimation, pyGEKO generates two main files:

1.  **The Grid File (.grd):** A CSV-formatted file containing the columns ``X, Y, Z_ESTIM, SIGMA``.
2.  **The Header File (.hdr):** A metadata file containing the parameters used (nork, nvec, model ID) and error metrics (MAE, RMSE).

Importing to QGIS
-----------------

To visualize your pyGEKO maps in QGIS:

1.  Open **Layer -> Add Layer -> Add Delimited Text Layer**.
2.  Select your ``.grd`` file.
3.  Set X field to ``X`` and Y field to ``Y``.
4.  Once imported, use the **Interpolation** plugin or simply use the **Graduated Symbology** on the ``Z_ESTIM`` field.

Surfer Compatibility
--------------------

The generated ``.grd`` files are structured to be easily converted into Golden Software Surfer grids. You can open them directly as "Data" and perform a "Grid Data" operation using the "Nearest Neighbor" method (since the points are already on a regular grid) to create a native ``.grd`` binary file.
