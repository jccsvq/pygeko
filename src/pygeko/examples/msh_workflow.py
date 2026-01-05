"""
pyGEKO Workflow: Full 1M Point Interpolation
--------------------------------------------
This script demonstrates the complete Geostatistical workflow:
1. Data loading & scaling
2. GIK Model analysis (Order 1 Drift)
3. Large-scale grid estimation (1000x1000)
"""

import gc
import time

from pygeko.kdata import Kdata, Kgrid
from pygeko.utils import get_data_path


def main():
    print("--- pyGEKO Full Workflow Stress Test ---")
    start_time = time.time()

    # 1. Load and prepare data
    # Scaling is recommended when Z range is significantly different from X,Y
    msh_path = get_data_path("msh5000.csv")
    kd = Kdata(msh_path)
    kd.Z /= 60.0  # Normalized for numerical stability

    # 2. Configure Kriging Parameters
    # nork=1 (Linear Drift), nvec=20 (Local neighbors)
    kd.nork = 1
    kd.nvec = 20

    print(
        f"Analyzing {len(kd.dframe)} points with NORK={kd.nork} and NVEC={kd.nvec}..."
    )
    kd.analyze(preview=False)
    end_time = time.time()
    print("\n--- Analysis Finished ---")
    print(f"Total processing time: {end_time - start_time:.2f} seconds")

    # 3. Define Grid Resolution
    # Creating a 1000x1000 grid (1,000,000 nodes)
    print("Generating 1,000x1,000 estimation grid...")
    kg = Kgrid(kd, 0.0, 1000.0, 0.0, 1000.0, 1000, 1000)

    # 4. Set the Model ID
    # Model 13 is the 'Power' model, often stable for topographic surfaces
    kg.model = 13

    # 5. Execute Grid Estimation
    # preview=True will show the resulting map once finished
    print("Computing Kriging weights and estimating nodes. Please wait...")
    start_time = time.time()
    kg.estimate_grid(filename="MtStHelens5000", preview=True)
    end_time = time.time()
    print("\n--- Grid Estimation Finished ---")
    print(f"Total processing time: {end_time - start_time:.2f} seconds")

    gc.collect()


if __name__ == "__main__":
    main()
