from __future__ import annotations

import argparse

from brain_organoid_criticality.loaders import inspect_nwb, list_electrical_series


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect an NWB file")
    parser.add_argument("path", help="Path to an NWB file")
    args = parser.parse_args()

    summary = inspect_nwb(args.path)
    print(summary)

    electrical_series = list_electrical_series(args.path)
    if electrical_series:
        print("\nElectrical series:")
        for ref in electrical_series:
            print(ref)


if __name__ == "__main__":
    main()
