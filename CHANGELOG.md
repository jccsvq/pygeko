# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-02-12

### Added
- small improvement to `Gplot` `.calibrate()` and `.export_asc()` methods and to `Gplot.calib_dic` attribute to prevent some potential conflicts with user calibrations.

### Fixed
- Significant omission in the documentation regarding Python's descriptor protocol (`__get__`) for custom calibration.
- Corrected several documentation "fossils".

## [1.0.0] - 2026-02-08

### Added
- First stable release of `pyGEKO`.
- Core GCK Kriging engine with automatic model selection.
- Sidecar metadata system (`.gck`, `.hdr` and `_meta.txt` files).
- CLI tools: `pygeko`, `lsgck` and `catgck`.
- ARM64 optimization for Raspberry Pi 5.