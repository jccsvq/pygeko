"""Extract and print information from `.gck` file"""

import argparse
import os

import joblib


def read_gck(filename: str) -> tuple[dict, dict]:
    """
    Reads a GCK file with basic error handling.

    :param filename: filename or filename base (without extension)
    :type filename: str
    :raises FileNotFoundError: file do not exist
    :raises RuntimeError: run time error
    :return: tuple with metadata and payload
    :rtype: tuple[dict, dict]
    """

    if not filename.endswith(".gck"):
        filename += ".gck"

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    try:
        checkpoint = joblib.load(filename)
        return checkpoint["metadata"], checkpoint["payload"]
    except Exception as e:
        raise RuntimeError(f"Error reading GCK file: {e}")


def print_gck(filename: str, prec: bool = False):
    """
    Print information from  GCK file

    :param filename: filename or filename base (without extension)
    :type filename: str
    :param prec: use maximum precision for ZK coefficients
    :type prec: bool, optional
    """
    try:
        meta, payload = read_gck(filename)
    except Exception as e:
        print(f"Error: {e}")
        return

    # --- 1. Print header & metadata ---
    p = meta.get("params", {})
    norm = meta.get("isnorm", "?")
    cvd = payload.get("crossvaldata", [])
    sorted_models = sorted(cvd, key=lambda x: x["rmse"])

    print(f"\n{' GCK EXPLORER ':=^75}")
    print(f"File: {os.path.basename(filename):<32} | From: {payload.get('title', 'N/A')}")
    print(
        f"Date/Time:   {meta.get('fecha_creacion', 'N/A'):<25} | Input points: {meta.get('n_puntos', 'N/A')}"
    )
    print(f"Col X: {payload.get('x_col', 'N/A'):<16} | Col Y: {payload.get('y_col', 'N/A'):<16} |",
        f"Col Z: {payload.get('z_col', 'N/A'):<16}")


    print(
        f"Conf:    nork={p.get('nork')} | nvec={p.get('nvec')} | Norm={norm} | Best model is #{sorted_models[0]['model_idx']}"
    )
    print(f"{'':-^75}")

    metrics = meta.get("metricas", {})
    print(
        f"Best MAE: {meta.get('metricas', {}).get('MAE'):.6f} | Best RMSE: {metrics.get('RMSE'):.6f} | Best CORR: {metrics.get('Corr'):.6f}"
    )
    print(f"{'':-^75}")

    # --- 2. Print models ---
    if not cvd:
        print("No model data was found in the payload.")
        return

    header = f"{'RANK':<5} | {'MOD':<4} | {'MAE':<12} | {'RMSE':<12} | {'CORR':<10}"
    print(f"\n{header}")
    print("-" * len(header))

    for rank, res in enumerate(sorted_models, 1):
        star = "★" if rank == 1 else " "

        # Line 1: Metrics
        print(
            f"{star}{rank:<4} | {res['model_idx']:<4} | {res['mae']:<12.6f} | {res['rmse']:<12.6f} | {res['corr']:<10.6f}"
        )

        # Line 2: ZK coefficients
        zk_list = res.get("zk", [])
        if prec:
            zk_str = " ".join([f"{v:16.12e}" for v in zk_list])
        else:
            zk_str = " ".join([f"{v:10.6e}" for v in zk_list])
        print(f"{'':<4} ZK: [{zk_str}]")
        print(f"{'':.<76}")  # Subtle separator between models




def main():
    parser = argparse.ArgumentParser(
        description="Extract and print information from `.gck` file",
        epilog="pyGEKO Analysis Tool",
    )
    parser.add_argument("gckfile", help="GCK file to inspect")
    parser.add_argument(
        "-p",
        "--precise",
        action="store_true",
        help="use maximum precision for ZK coefficients",
    )

    args = parser.parse_args()
    print_gck(args.gckfile, args.precise)


if __name__ == "__main__":
    main()
