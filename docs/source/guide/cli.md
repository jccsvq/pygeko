# 🔍 Command Line Interface (CLI)

pyGEKO includes several command-line utilities to streamline geospatial workflows.

## [pygeko](#pygeko-utility) (The Main Engine)

The core tool to perform Kriging, a custom Python REPL with all relevant classes (an a few additional symbols) pre-imported. It can be used interactively or to run scripts. It is the essential component for using `pyGEKO` if it has been installed using `pipx`.




## [lsgck](#lsgck-utility) (Structure Analysis)

Use this tool to list and analyze the available Generalized Covariance models analyzed for your dataset. It helps in understanding the spatial structure before running a full grid estimation.

## [catgck](#catgck-utility) (Structure Analysis)

This tool complements the previous one by showing detailed information for each model analyzed.

## [png2csv](#png2csv-utility) (Data Preparation)

Utility to sample XYZ data from PNG raster images of Digital Elevation Models (DEM) and write them to a CSV file. It has been used during the development of this project to obtain test data from images obtained in [Heightmapper](https://tangrams.github.io/heightmapper/).



