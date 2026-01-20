.. pyGEKO documentation master file

pyGEKO: Fast Generalized Covariance Kriging
===========================================

.. image:: https://img.shields.io/pypi/v/pygeko.svg
   :target: https://pypi.org/project/pygeko/
   :alt: PyPI Version

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/jccsvq/pygeko/blob/main/LICENSE
   :alt: License


**Spatial interpolation made fast, automatic, and hardware-efficient.**

**pyGEKO** is a high-performance Python library for **Generalized Covariance Kriging (GCK)**. Unlike traditional Ordinary Kriging, pyGEKO eliminates the tedious process of manual variogram fitting. It automatically recognizes the underlying spatial structure using a powerful library of generalized covariance models.

Designed for efficiency, pyGEKO runs seamlessly on high-end x86 workstations and is specifically optimized for **ARM64 architectures**, making it the premier choice for geospatial analysis on the **Raspberry Pi 5**.

🚀 Key Features
---------------



* **🚫 No Variograms Needed:** Bypasses the manual fitting of experimental variograms. pyGEKO uses a genetic-like search algorithm (GEKO) to identify the optimal structural model automatically.
* **⚡ ARM Optimized:** Fine-tuned to run on the Raspberry Pi 5 without thermal throttling, leveraging specific threading controls for ARM cores.
* **🎨 GPU Visualization:** Generates interactive 3D surfaces using Plotly (WebGL), optimized for smooth rendering even over VNC remote connections.

.. figure:: /_static/msh-rpi.jpg
   :align: center
   :alt: Mount St. Helens 1000x1000 grid as viewed in a Raspberry PI 5 acceded vis VNC center

   Mount St. Helens 500x500 grid (from 5000 points) as viewed in a Raspberry PI 5 acceded vis VNC
   `Click here to open the Interactive 3D Model (13 MB WebGL) <https://jccsvq.github.io/pygeko/docs/web_models/msh_3d_500.html>`_

* **🛠️ Battle-Tested Algorithms:** Implements Generalized Increment Kriging (GIK) and KD-Tree spatial indexing for rapid neighborhood search.
* **📦 GIS Ready:** Exports results directly to standard ``.grd`` and ``.hdr`` formats compatible with Surfer, QGIS, and other geospatial tools.

📊 Performance Benchmark
------------------------

PyGEKO was benchmarked processing a **1,000,000 point grid** (1000x1000) on Debian 12:

+--------------------+-----------------+-------+------------------+
| Platform           | CPU             | Cores | Time (1M points) |
+====================+=================+=======+==================+
| **Desktop PC**     | Intel i7-9700K  | 8     | **36.3 s**       |
+--------------------+-----------------+-------+------------------+
| **Raspberry Pi 5** | Cortex-A76      | 3*    | **~110 s**       |
+--------------------+-----------------+-------+------------------+

\* *Recommended 3-core config for thermal stability on ARM.* 

🧠 Tuning & Optimization Benchmark
----------------------------------

The following benchmark shows the time required to perform an exhaustive search of **30 model configurations** (Testing 22 GIK models + 
Cross-Validation per config) using the St. Helens dataset (**5,000 points**):

+--------------------+-----------------+---------+-------------------+------------+
| Platform           | CPU             | Workers | Time (30 configs) | Rate       |
+====================+=================+=========+===================+============+
| **Desktop PC**     | Intel i7-9700K  | 8       | **~2 min 51 s**   | 5.7 s/it   |
+--------------------+-----------------+---------+-------------------+------------+
| **Raspberry Pi 5** | Cortex-A76      | 3*      | **~10 min 10 s**  | 20.4 s/it  |
+--------------------+-----------------+---------+-------------------+------------+

* *Recommended 3-core config for thermal stability on ARM.*


.. note::
   **Reliability:** PyGEKO uses a **multiprocessing isolation strategy** for tuning. Each iteration runs in a dedicated child process, ensuring 100% memory reclamation and preventing RAM accumulation even during intensive **5K+ point** explorations.

🛠 Installation
---------------

Install pyGEKO directly from PyPI:

.. code-block:: bash

   pip install pygeko

or

.. code-block:: bash

   pipx install pygeko

📂 Output Formats
-----------------

* ``.gck``: Binary object containing the full Python state and metadata.
* ``.grd``: Standard grid file (CSV format) for GIS software.
* ``.hdr``: Human-readable header file with model performance metrics.
* ``.html``: WebGL HTML with surface models.

📖 Documentation Contents
--------------------------


The documentation is organized following the **Diátaxis** framework:



.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :name: sec-tutorials

   guide/installation
   guide/quickstart.md

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :name: sec-guides

   guide/tutorial.md
   guide/tuning
   guide/rpi_optimization
   guide/exporting
   guide/cli.md

.. toctree::
   :maxdepth: 3
   :caption: API Reference
   :name: sec-api

   reference/api

.. toctree::
   :maxdepth: 2
   :caption: Theory & Background
   :name: sec-theory

   theory/gck_method
 
.. toctree::
   :maxdepth: 2
   :caption: Other
   :name: sec-Other

   todo.md
 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. Este bloque es invisible pero fuerza a Sphinx a incluir la imagen grande
.. image:: _static/msh-rpi.jpg
   :width: 0