import argparse
import os
import joblib

# from datetime import datetime


def check_gck_files(directory: str = ".", verbose: bool = False):
    """Scan the directory for .gck files and display their contents.

    :param directory: directory to scan, defaults to ".":str
    :type directory: str, optional
    :param verbose: print additional information, defaults to False
    :type verbose: bool, optional
    """
    files = [f for f in os.listdir(directory) if f.endswith(".gck")]

    if not files:
        print("No .gck files were found in this directory.")
        return

    # Table header
    if verbose:
        header = (
            f"{'File':<30} | {'N':<1} | {'Date':<6} | {'nork':<5} | {'nvec':<5} "
            + f"| {'MAE':<8} | {'RMSE':<8} | {'CORR':<8} | {'Model':<6}"
        )
        print("\n" + "=" * len(header))
        print(header)
        print("-" * len(header))
    else:
        header = f"{'File':<30} | {'N':<1} | {'Date':<6} | {'nork':<5} | {'nvec':<5} | {'MAE':<8} | {'Model':<6}"
        print("\n" + "=" * len(header))
        print(header)
        print("-" * len(header))

    # found_any = False
    for f in sorted(files):
        try:
            # We only load the metadata to speed things up (if the file allows it)
            # Note: joblib loads the entire file, but because it's compressed, it's faster
            data = joblib.load(directory + "/" + f)

            if isinstance(data, dict) and "metadata" in data:
                m = data["metadata"]
                p = m.get("params", {})
                res = m.get("metricas", {})
                # Extract information about normalization mode
                isn=m.get("isnorm",None)
                if isn is None:  # Pre v1.0.0dev1 gck file case
                    isN = '?'
                elif isn:        # v1.0.0dev1 onwards gck file case
                    isN = 'Y'
                else:
                    isN = 'N'   


                # Format date (day and month only)
                fecha_str = m.get("fecha_creacion", "N/D").split(" ")[0][5:]
                # One alternative 
                # mae_str = f"{res.get('MAE', 0):.4f}" if isinstance(res.get('MAE'), (int, float)) else "N/A"
                if verbose:
                    print(
                        f"{f:<30} | {isN:<1} | {fecha_str:<6} | {p.get('nork', '??'):<5} | {p.get('nvec', '??'):<5} "
                        + f"| {res.get('MAE', '??'):8g} | {res.get('RMSE', '??'):8g} "
                        + f"| {res.get('Corr', '??'):8g} | {p.get('model_id', '??'):<6}"
                    )
                else:
                    print(
                        f"{f:<30} | {isN:<1} | {fecha_str:<6} | {p.get('nork', '??'):<5} | {p.get('nvec', '??'):<5} "
                        + f"| {res.get('MAE', '??'):8g} | {p.get('model_id', '??'):<6}"
                    )
                # found_any = True
            else:
                print(f"{f:<30} | [Old file or file without metadata]")
        except Exception as e:
            print(f"{f:<30} | [Error reading file: {str(e)[:20]}...]")

    print("=" * len(header) + "\n")


def main():
    """
    Program entry point
    """
    # 1. Create parser object
    parser = argparse.ArgumentParser(
        description="pyGEKO Utility: Scan directory for geospatial data."
    )

    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        default=".",
        help='Path to the directory to scan (default: current directory ".")',
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="print additional information",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    target_dir = os.path.abspath(args.dir)

    if os.path.isdir(target_dir):
        print(f"Scanning directory: {target_dir}")
        check_gck_files(target_dir, args.verbose)
    else:
        print(f"Error: The path '{target_dir}' is not a valid directory.")


if __name__ == "__main__":
    main()
