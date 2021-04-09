import os
import json
from collections.abc import Iterable
import warnings
from pyomo.environ import Var, Param
import numpy as np
import pandas as pd
import folium
from folium import plugins

def calc_distance(X, Y):
    return np.sqrt(np.power(X[0]-Y[0], 2) + np.power(X[1]-Y[1], 2))

def calc_objective(dc_locs, cust_assignment, demand, lat_c, lon_c):
    obj = 0
    for y, d, phi, lam in zip(cust_assignment, demand, lat_c, lon_c):
        dist = calc_distance(dc_locs[y], (phi, lam))
        obj += d * dist

    return obj

def get_opt_assignment(model):
    opt_assignment = np.zeros(len(model.j)).astype(int)
    for i in model.i:
        for j in model.j:
            if model.dc_assignment[i, j].value > 0:
                opt_assignment[j] += 1
    return opt_assignment

def _pyomo_obj_to_dict(model, obj):
    out = {}
    for comp in model.component_objects(obj, active=True):
        comp_dict = {}
        for idx in comp:
            try:
                val = comp[idx].value
            except AttributeError:
                val = comp[idx]
            if hasattr(val, 'dtype'):
                if 'f' in val.dtype.str:
                    val = float(val)
                elif 'i' in val.dtype.str:
                    val = int(val)
                else:
                    msg = f"Unnaccounted for NumPy type: {val.dtype}"
                    msg += "\nCoercing to 0 to avoid JSON serialization error."
                    warnings.warn(msg)
                    val = 0
            if isinstance(idx, Iterable) and type(idx) is not str:
                d = val
                for i, j in enumerate(reversed(idx)):
                    d = {str(j): d}

                try:
                    comp_dict[str(idx[0])].update(d[str(idx[0])])
                except KeyError:
                    comp_dict.update(d)
            else:
                comp_dict[idx] = val
        out[str(comp)] = comp_dict
    return out

def _model_to_json(model):
    '''Parse Pyomo model to store as JSON'''
    out = {}
    out['parameters'] = _pyomo_obj_to_dict(model, Param)
    out['variables'] = _pyomo_obj_to_dict(model, Var)

    return out

def convert_results_to_json(soln_dict):
    out = {}
    for k1, v1 in soln_dict.items():
        iter_key = 'iter_' + str(k1)
        out[iter_key] = {}
        for k2, v2 in v1.items():
            if k2 == 'model':
                try:
                    out[iter_key][k2] = _model_to_json(v2)
                except AttributeError:
                    out[iter_key][k2] = str(v2.__class__)
            elif type(v2) == np.ndarray:
                out[iter_key][k2] = v2.tolist()
            else:
                out[iter_key][k2] = v2
    return json.dumps(out)

def _check_max_input(X):
    '''Takes string input from app and changes it based on expected output'''
    try:
        if X is None:
            return None
        elif X.upper() == 'NONE':
            return np.inf
        elif int(X) <= 0:
            return np.inf
        elif int(X) > 0:
            return int(X)
        else:
            # To raise error in app
            return None
    except ValueError:
        return None

def _check_min_input(X):
    '''Takes string input from app and changes it based on expected output'''
    try:
        if X is None:
            return None
        elif X.upper() == 'NONE':
            return 0
        elif int(X) <= 0:
            return 0
        elif int(X) > 0:
            return int(X)
        else:
            # To raise error in app
            return None
    except ValueError:
        return None

def plot_customer_assignment(opt_results_iteration):
    '''Plots customer assignment from optimization model output.'''
    colors = ['red', 'blue', 'darkred', 'lightred',
              'orange', 'beige', 'green', 'darkgreen',
              'lightgreen', 'darkblue', 'lightblue', 'purple',
              'darkpurple', 'pink', 'cadetblue', 'lightgray',
              'gray', 'black']
    # Plot customer locations
    lat_cust = [i for i in opt_results_iteration['model']['parameters']['lat_cust'].values()]
    lon_cust = [i for i in opt_results_iteration['model']['parameters']['lon_cust'].values()]
    CUST = len(lat_cust)
    dc_locs = np.vstack(opt_results_iteration['dc_locs'])
    DC = len(dc_locs)
    assignment = opt_results_iteration['model']['variables']['dc_assignment']
    map_center = [np.mean(lat_cust), np.mean(lon_cust)]
    
    m = folium.Map(location=map_center, zoom_start=4, width=800)
    _ = [folium.Marker(location=(lat_cust[j], lon_cust[j]), 
            icon=folium.Icon(color=colors[i])).add_to(m)
            for i in range(DC) 
             for j in range(CUST) if assignment[str(i)][str(j)] > 0]
    
    _ = [folium.Marker(location=(dc[0], dc[1]), 
            icon=folium.Icon(color=colors[i], icon='screenshot'),
            tooltip=f'Distribution Center {i}').add_to(m)
             for i, dc in enumerate(dc_locs)]
    
    return m