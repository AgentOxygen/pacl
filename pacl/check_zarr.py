#!/usr/bin/env python
"""
check_zarr.py

Persad Aero-Climate Lab tool for checking zarr stores for data integrity and
valid inter-comparisons.

see README.md for more details.

Developer: 
Contact: 
Last Header Update: 
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

def check_single(path: str, debugging: False):
    """Check a single zarr store"""

    ds = xr.open_zarr(path)
    
    if debugging:
        print("Checking single zarr store: ", path)
        print(ds) 
        print("\n\n")
        print(ds.info())
        print("\n\n")

    data_vars = []
    for var in ds.data_vars:
        # we want to ignore all data variables that are actually bounds
        if 'bnds' not in ds[var].dims:
            data_vars.append(ds[var])

    if len(data_vars) > 1: 
        print("More than one valid data variable in zarr store")
        return 
    
    data = data_vars[0]


    # TASK 1
    # TODO: will there ever be more than one valid data variable in a zarr store?
    if debugging: 
        print(data)
        print()

    # TODO: all possible spatial dimensions are ? Check if all of the data variable actually has all of these dimensions? 
    possible_spatial_dims = ["lat", "lon", "lev", "latitude", "longitude", "level"]
    spatial_dims = [dim for dim in possible_spatial_dims if dim in data.dims]
    other_dimensions = [dim for dim in data.dims if dim not in spatial_dims and dim != 'time']

    # latitudinal weighting for task 1 and task 2 
    if 'lat' in spatial_dims:
        weights = np.cos(np.deg2rad(data.lat))
    if 'latitude' in spatial_dims:
        weights = np.cos(np.deg2rad(data.latitude))
    weights.name = "weights"
    data_weighted = data.weighted(weights)


    # Take the mean over the spatial dimensions and plot each combination of the other_dimensions as a line with the x-axis being "time"
    if len(other_dimensions) > 1:
        print("This is untested. Please let Willow know what zarr file you are using so she can test it.")
        # We need to group our dataarray so it has one singular new dimension that has all combinations of the other_dimensions
        data_ = data_weighted.stack(new_dim=other_dimensions)
        data_.mean(dim=spatial_dims).plot.line(x='time', hue='new_dim')
    elif len(other_dimensions) == 1:
        data_weighted.mean(dim=spatial_dims).plot.line(x='time', hue=other_dimensions[0])
    else:
        data_weighted.mean(dim=spatial_dims).plot()

    plt.suptitle(f"Mean over spatial dimensions")
    plt.figtext(0.5, 0, f"Plot generated for {path}", horizontalalignment='center', fontsize=7) 
    plt.show()

    # TASK 2
    if len(other_dimensions) > 1:
        print("This is untested. Please let Willow know what zarr file you are using so she can test it. ")
        data_ = data_weighted.stack(new_dim=other_dimensions)
        data_.mean(dim=spatial_dims).plot.pcolormesh(x='time', y='new_dim')
    elif len(other_dimensions) == 1:
        data_weighted.mean(dim=spatial_dims).plot.pcolormesh(x='time', y=other_dimensions[0])
    else:
        print("Not enough dimensions for a color mesh plot.")
        # data.mean(dim=spatial_dims).plot.pcolormesh()

    plt.suptitle(f"Mean over spatial dimensions")
    plt.figtext(0.5, 0, f"Plot generated for {path}", horizontalalignment='center', fontsize=7) 
    plt.show()

    # TASK 3
    other_dimensions = other_dimensions + ['time']
    data.mean(dim=other_dimensions).plot()
    plt.suptitle(f"Mean over entire time period and all other dimensions")
    plt.figtext(0.5, 0, f"Plot generated for {path}", horizontalalignment='center', fontsize=7) 
    plt.show()

    # TASK 4
    other_dimensions.remove('time')
    data.isel(time=0).mean(dim=other_dimensions).plot()
    plt.suptitle(f"First timestep, mean over all other dimensions ")
    plt.figtext(0.5, 0, f"Plot generated for {path}", horizontalalignment='center', fontsize=7) 
    plt.show() 

    # TASK 5
    data.isel(time=-1).mean(dim=other_dimensions).plot()
    plt.suptitle(f"Last timestep, mean over all other dimensions for \n{path}")
    plt.figtext(0.5, 0, f"Plot generated for {path}", horizontalalignment='center', fontsize=7) 
    plt.show() 



def check_zarr(paths: str | list, debugging: False): # Definitely add more optional parameters as you see fit
    """Willow, this is the function you will want to work on"""
    
    # Check if paths is a string or list
    if(isinstance(paths, str)):
        check_single(paths, debugging)
    
    
    
    




    return None # This might return a Matplotlib figure object



