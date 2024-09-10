# Persad Aero Climate Lab (PACL) Toolkit
A generalized Python toolkit for automating common tasks with PACL.

*The following is still in development, many of these features do not work yet*

## Installation
This package is listed on PyPi and can be installed using `pip`:
```
pip install pacl
```

## Static Functions
- `pacl.check_zarr` gut checks a zarr store for data integrity and ensures compatability between multiple stores.
- `pacl.check_netcdf` wrapper for `pacl.check_zarr` designed to run on netCDF datasets directly.
- `pacl.nc_to_zarr` concatenates and converts multiple netCDF datasets into a zarr store.
- `pacl.compute_climo_suite` generates xarray Dataset with multiple statistics computed as variables for an input zarr store.

## Classes
- `pacl.AutoFigure` modified automatic figure generation with PACL figure specifications.
- `pacl.Database` centralized path object for managing all large datasets stored under `persad_research`.