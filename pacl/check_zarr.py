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
from colorama import Fore, Style
from typing import Callable


def check_single(path: str, verbose: False):
    """Check a single zarr store"""

    ds = xr.open_zarr(path)
    
    if verbose:
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
    if verbose: 
        print(data)
        print()

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
    
def check_spatial_coords(ds1: xr.Dataset, ds2: xr.Dataset) -> bool:
    # Check that the spatial coordinates (lat, lon, lev) are equivalent in shape and value.

    # Check that they have the same spatial dims
    possible_spatial_dims = ["lat", "lon", "lev", "latitude", "longitude", "level"]
    spatial_dims_1 = [dim for dim in possible_spatial_dims if dim in ds1.dims]
    spatial_dims_2 = [dim for dim in possible_spatial_dims if dim in ds2.dims]

    if spatial_dims_1 != spatial_dims_2:
        return False
    
    # Check that the spatial dims have the same shape
    for dim in spatial_dims_1:
        if ds1[dim].shape != ds2[dim].shape:
            return False
        
    # Check that the spatial dims have the same values
    for dim in spatial_dims_1:
        if not np.array_equal(ds1[dim].values, ds2[dim].values):
            return False
        
    return True

def check_vars_same_name(ds1: xr.Dataset, ds2: xr.Dataset) -> bool:
    # Check that the variables in the datasets have the same name

    vars_1 = list(ds1.data_vars.keys())
    vars_2 = (ds2.data_vars.keys())

    if vars_1 != vars_2:
        return False

    return True

def check_time(ds1: xr.Dataset, ds2: xr.Dataset) -> bool:
    # Check that the time coordinates are monotonic and that all datasets use the same calendar
    
    if not ds1.time.to_index().is_monotonic_increasing:
        return False
    
    if not ds2.time.to_index().is_monotonic_increasing:
        return False
    
    if ds1.time.encoding['calendar'] != ds2.time.encoding['calendar']:
        return False
    
    return True

def check_units(ds1: xr.Dataset, ds2: xr.Dataset) -> bool:
    # Check that the units attributes are equivalent for each variable in all datasets

    for var in ds1.data_vars:
        if 'bnds' in var: 
            continue 
        if 'units' not in ds1[var].attrs:
            print("No unit attribute for variable: ", var)
            print(ds1[var].attrs)
            return False
        if var not in ds2.data_vars:
            return False
        if ds1[var].attrs["units"] != ds2[var].attrs["units"]:
            return False

    return True

def find_majority_ds(datasets: list, check_equiv: Callable) -> int: 
    # Find the majority dataset in a list of datasets using Boyer–Moore majority vote algorithm
    # This function will be used to determine which dataset to compare the others to
    # We will compare all datasets to the majority dataset to ensure that they are equivalent

    majority_ds = -1 
    counter = 0

    for i, ds in enumerate(datasets): 
        if counter == 0:
            majority_ds = i
            counter += 1
            continue

        if check_equiv(datasets[majority_ds], ds):
            counter += 1
        else:
            counter -= 1

    # count if majority_ds is actually the majority 
    counter = 0
    for ds in datasets:
        if check_equiv(datasets[majority_ds], ds):
            counter += 1
    
    if counter <= len(datasets) / 2:
        return -1

    return majority_ds

def find_different_datasets(datasets: list, check_equiv: Callable) -> list:
    # Find the datasets that are different from the majority dataset
    # It will return [-1] if no majority dataset is found
    majority_ds = find_majority_ds(datasets, check_equiv)
    if majority_ds == -1:
        return [-1]

    different_datasets = []
    for i, ds in enumerate(datasets):
        if not check_equiv(datasets[majority_ds], ds):
            different_datasets.append(i)

    return different_datasets

def get_check_msg(different_datasets: list, datasets: list, check_num: int, checks: list, msgs: list) -> str: 
    # The first msg is what it say if the check failed. The second msg is what it says if the check passed

    if different_datasets == [-1]:
        checks[check_num] = False
        check_msg = Fore.RED + f"Check {check_num+1} failed: {msgs[0]} A majority of them are different from each other.\n" + Style.RESET_ALL
    elif len(different_datasets) == 0:
        checks[check_num] = True
        check_msg = Fore.GREEN + f"Check {check_num+1} passed: {msgs[1]}\n" + Style.RESET_ALL
    else: 
        dataset_names = [datasets[i] for i in different_datasets]
        checks[check_num] = False
        check_msg = f"Check {check_num+1} failed: {msgs[0]} The following datasets ({len(different_datasets)} / {len(datasets)}) are different from the majority dataset: " + str(dataset_names) + "\n"

    return check_msg


def check_paths(paths: list, verbose: False):

    checks_passed = np.zeros(4)
    summary_msg = ""
    
    datasets = []
    for path in paths:
        ds = xr.open_zarr(path)
        datasets.append(ds)

    # Check 1 
    different_datasets = find_different_datasets(datasets, check_spatial_coords)
    msgs = ["Spatial coordinates are not equivalent across all datasets.", "Spatial coordinates are equivalent across all datasets."]
    summary_msg += get_check_msg(different_datasets, datasets, 0, checks_passed, msgs)

    # Check 2
    different_datasets = find_different_datasets(datasets, check_vars_same_name)
    msgs = ["Variables do not have the same name across all datasets.", "Variables have the same name across all datasets."]
    summary_msg += get_check_msg(different_datasets, datasets, 1, checks_passed, msgs)

    # Check 3
    different_datasets = find_different_datasets(datasets, check_time)
    msgs = ["Time coordinates are not monotonic or do not use the same calendar across all datasets.", "Time coordinates are monotonic and use the same calendar across all datasets."]
    summary_msg += get_check_msg(different_datasets, datasets, 2, checks_passed, msgs)

    # Check 4
    different_datasets = find_different_datasets(datasets, check_units)
    msgs = ["Units are not equivalent across all datasets.", "Units are equivalent across all datasets."]
    summary_msg += get_check_msg(different_datasets, datasets, 3, checks_passed, msgs)

    print(f"\n\nSUMMARY: {int(sum(checks_passed))}/{len(checks_passed)} checks passed.")
    print("=============================================================")
    print(summary_msg)



def check_zarr(paths: str | list, verbose: False): # Definitely add more optional parameters as you see fit
    """Willow, this is the function you will want to work on"""
    
    # Check if paths is a string or list
    if(isinstance(paths, str)):
        check_single(paths, verbose)
    
    if(isinstance(paths, list)):
        check_paths(paths, verbose)
    
    




    return None # This might return a Matplotlib figure object



