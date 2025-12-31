Installation Guide
==================

This page covers how to get **pyGEKO** up and running on your system, whether you are an end-user or a developer looking to contribute.

Prerequisites
-------------

* **Python:** 3.9 or higher (3.11+ recommended for performance).
* **Pip:** Latest version recommended.
* **Architecture:** Supports x86_64 and ARM64 (specifically optimized for Raspberry Pi 5).

Standard Installation
---------------------

The easiest way to install pyGEKO is via PyPI:

.. code-block:: bash

   pip install pygeko

This will automatically install all core dependencies, including:
* ``numpy`` and ``scipy`` for mathematical operations.
* ``pandas`` for data handling.
* ``plotly`` and ``matplotlib`` for visualization.
* ``scikit-learn`` for KD-Tree spatial indexing.

Developer Installation (using Hatch)
------------------------------------

If you want to modify the source code or contribute to the project, we recommend using **Hatch**, as it manages isolated environments and project standards automatically.

1. **Clone the repository:**

   .. code-block:: bash

      git clone https://github.com/yourusername/pygeko.git
      cd pygeko

2. **Install Hatch:**

   .. code-block:: bash

      pip install hatch

3. **Enter the development shell:**

   This command creates a virtual environment and installs pyGEKO in "editable" mode:

   .. code-block:: bash

      hatch shell

4. **Or run the interactive REPL immediately with Hatch**

   .. code-block:: bash

      hatch run pygeko



Raspberry Pi 5 Setup
--------------------

For Raspberry Pi users, we recommend the following additional steps to ensure optimal performance:

1. **System Dependencies:**
   Ensure your system is up to date:
   
   .. code-block:: bash

      sudo apt update && sudo apt upgrade
      sudo apt install libopenblas-dev libatlas-base-dev gfortran -y

2. **Cooling:**
   Kriging is a CPU-intensive task. Using the **Official Raspberry Pi 5 Active Cooler** is highly recommended to prevent thermal throttling during large matrix operations.

3. **Virtual Environments:**
   On recent versions of Raspberry Pi OS (Bookworm), you must use a virtual environment or ``hatch`` to install packages:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate
      pip install pygeko

Troubleshooting
---------------

**Error: "Could not find a version that satisfies the requirement..."**
Ensure you are using Python 3.9+. Older versions of Python are not supported.

**Performance is slow on ARM:**
Check if other processes are consuming CPU. pyGEKO is optimized for single-thread efficiency on ARM to avoid overhead, but it still requires raw processing power for large datasets.
