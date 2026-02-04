API Reference
=============

This section provides a detailed description of the classes and functions 
within the **pyGEKO** package.

.. currentmodule:: pygeko

Core Interface
--------------

The following classes are the primary entry points for interacting with the library.
These are available directly under the ``pygeko`` namespace.

Kdata
~~~~~
.. autoclass:: Kdata
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Kgrid
~~~~~
.. autoclass:: Kgrid
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Kprofile
~~~~~~~~
.. autoclass:: Kprofile
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

KprofileCSV
~~~~~~~~~~~
.. autoclass:: KprofileCSV
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

ProfilePicker
~~~~~~~~~~~~~
.. autoclass:: ProfilePicker
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Visualization
-------------

The ``Gplot`` class provides tools for rendering maps and diagnostic plots. 
The ``Pplot`` class performs a basic graphical representation of the profiles.

Gplot
~~~~~
.. autoclass:: Gplot
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Pplot
~~~~~
.. autoclass:: Pplot
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Data Preparation
----------------

Tools for data calibration and normalization.

Calibrator
~~~~~~~~~~
.. autoclass:: Calibrator
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

Internal Utilities
------------------

Functions.

.. automodule:: pygeko.utils
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource