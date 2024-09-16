# pacl.check_zarr
Persad Aero-Climate Lab (PACL) tool for "gut" checking zarr stores for data integrity and inter-comparisons.

*The following is still in development, many of these features do not work yet*

## Usage
Import the Python module within a Jupyter notebook or interactive session:
```
import pacl
```
To check a single zarr store, use the following syntax:
```
pacl.check_zarr("path/to/zarr/store/data.zarr")
```

To check if multiple zarr stores are compatable, use the following syntax:
```
pacl.check_zarr(["path/to/zarr/store/data1.zarr", "path/to/zarr/store/data2.zarr", "path/to/zarr/store/data3.zarr", ...])
```

Running either line of Python code will print out various checks and an image with multiple diagnostic plots.

## Diagnostics and Checks
No checks are performed on single zarr stores. Rather, a series of plots are made for the user to verify data integrity qualitatively. The following diagnostic plots are produced:
1. A line plot of timeseries data averaged over all spatial dimensions. Other dimensions, such as "member" are plotted as separate lines. If there are multiple other dimensions, then their combinations are plotted.
2. Instead of a line plot, a heat map is generated using the same specifications as #1.
3. A map of the mean of all dimensions other than latitude and longitude for the entire time period.
4. A map of the mean of all dimensions other than latitude and longitude for the first timestep.
5. A map of the mean of all dimensions other than latitude and longitude for the last timestep.

When given multiple zarr stores, a series of checks are performed between all datasets to ensure compatability:
1. Check that the spatial coordinates (lat, lon, lev) are equivalent in shape and value.
2. Check that all variables share the same name.
3. Check that the time coordinates are monotonic and that all datasets use the same calendar.
4. Check that the units attributes are equivalent for each variable in all datasets.
A warning is issued if any of these checks fail.