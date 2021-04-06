import os
import json
from collections.abc import Iterable
import warnings
from pyomo.environ import Var, Param
import numpy as np
import pandas as pd

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



