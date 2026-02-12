Parameter Tuning
================

Finding the optimal configuration for Kriging can be challenging. pyGEKO simplifies this through the ``Kdata.tune()`` method, which automates the search for the best trend order and neighborhood size.

The Core Parameters
-------------------

* **nork (Order of Drift):** * ``0``: Simple Kriging (constant mean).
    * ``1``: Linear trend (most common for topography).
    * ``2``: Quadratic trend (for complex surfaces).
* **nvec (Number of Neighbors):** * Small values (8-12): Faster calculation, more local detail, but higher risk of "noise".
    * Large values (20-40): Smoother results, handles gaps better, but significantly slower.

Using the Automated Tuner
-------------------------

The ``tune()`` method performs a grid search across different combinations and ranks them by **Mean Absolute Error (MAE)**.

.. code-block:: python

   from pygeko import Kdata

   # Load data
   kd = Kdata("my_survey.csv")
   
   # Test linear and quadratic trends with 8, 12, and 16 neighbors
   results = kd.tune(nvec_list=[8, 12, 16], nork_list=[1, 2])
   
   # pyGEKO automatically sets the object to the best configuration found
   # Plot a Heatmap of the results
   kd.plot_tuning_results(results)

Interpreting the Heatmap
------------------------

When you run ``tune()`` followed by ``plot_tuning_results()``, pyGEKO generates a heatmap. Look for the "darkest" or "lowest" point in the MAE matrix. If the best result is at the edge of your tested values (e.g., at 16 neighbors), consider running another tune with higher values (e.g., 20, 24) to see if accuracy improves further.
