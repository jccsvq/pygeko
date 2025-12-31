Theoretical Background
======================

The Generalized Covariance Kriging (GCK) method is the mathematical heart of **pyGEKO**. Understanding its principles is key to leveraging the library's full potential for automated spatial interpolation.

The Problem with Ordinary Kriging
---------------------------------

In traditional Geostatistics (Ordinary Kriging), the user must model spatial correlation through a **Variogram** (semi-variance). This process involves:

1.  Calculating the experimental variogram.
2.  Manually selecting a model (Spherical, Exponential, Gaussian).
3.  Fitting parameters like *Sill*, *Range*, and *Nugget*.

This workflow is subjective, time-consuming, and difficult to automate in real-time systems or autonomous sensors (like a Raspberry Pi in the field).

The GCK Solution
----------------

**Generalized Covariance Kriging** approaches the problem from a different perspective. Instead of modeling the semi-variance of the data, it utilizes **Generalized Covariance Functions (GCF)**. 

The core advantage of GCK is that it does not require a positive-definite covariance in the traditional sense, but rather a function that satisfies the condition of **Conditional Positive Definiteness** for increments of a certain order.



Intrinsic Random Functions of Order k (IRF-k)
---------------------------------------------

pyGEKO implements the theory of **Intrinsic Random Functions of Order k**. This allows the model to handle:

* **Non-stationary data:** Where the mean is not constant (spatial trends).
* **Polynomial Drift:** GCK filtering automatically accounts for trends of order *k* (usually linear, :math:`k=1`, or quadratic, :math:`k=2`).

The structural model in pyGEKO is defined as a linear combination of basis functions:

.. math::

   K(h) = \sum_{p=0}^{4} a_p f_p(h)

Where :math:`f_p(h)` includes structures such as:

* :math:`1` (Nugget effect)
* :math:`|h|` (Linear structure)
* :math:`|h|^3` (Cubic structure)
* :math:`|h|^5` (Penta-spherical)
* :math:`|h|^2 \ln|h|` (Spline / Thin-plate effect)

The mathematical background of this project was explained by the author as early as 1991 in `Topography of the Galactic Disk: Z Structure and Large-Scale Star Formation <https://ui.adsabs.harvard.edu/abs/1991ApJ...378..106A/abstract>`_
(publicly accessible, see also the project: `GCK <https://github.com/jccsvq/gck>`_  on GitHub).

The GEKO Algorithm: Automatic Recognition
-----------------------------------------

The name **pyGEKO** comes from **GE** neralized **KO** variance. The library uses a structural recognition algorithm that:

1.  **Filters the Drift:** Using Generalized Increments (GIK), it removes the polynomial trend from the calculation to focus on the underlying spatial structure.
2.  **Model Selection:** It tests multiple combinations of the basis functions (22 models by default).
3.  **Cross-Validation Ranking:** Each model is evaluated using Leave-One-Out Cross-Validation (LOOCV). The model with the lowest **Mean Absolute Error (MAE)** and highest correlation is automatically selected.

Why use pyGEKO?
---------------

1.  **Automation:** No manual variogram fitting. It is a "plug-and-play" kriging engine.
2.  **Mathematical Rigor:** Based on the work of Georges Matheron and Jean-Paul Chilès, ensuring unbiased estimations (BLUE - Best Linear Unbiased Estimator).
3.  **Versatility:** Excellent for environmental sensors, topographic surveys, and any application where spatial structures vary across different datasets.

References
----------

* Alfaro, E. J., Cabrera-Cano, J., and Delgado, A. J., “Topography of the Galactic Disk: Z-Structure and Large-Scale Star Formation”, *The Astrophysical Journal*, vol. 378, IOP, p. 106, 1991. doi:10.1086/170410.
* Chilès, J. P., & Delfiner, P. (2012). *Geostatistics: Modeling Spatial Uncertainty*. Wiley.
* Matheron, G. (1973). *The Intrinsic Random Functions and Their Applications*. Advances in Applied Probability.
