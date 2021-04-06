from fastapi import FastAPI, Query
from typing import List, Optional
import pandas as pd
import numpy as np
import json

from greenfield import BaseGreenFieldModel
import utils

app = FastAPI()

names = ["Aaron", "Bill", "Chad", "Doug", "Evan", "Frank", "George"]
fake_items_db = [{"name": n} for n in names]

_regions = ["NAA", "LAA", "Europe", "Africa", "Middle East and India",
    "APAC", "Australia"]
regions = [{"region": r} for r in _regions]

years = [2017 + i for i in range(4)]

@app.get("/items/")
async def read_item(skip: int=0, limit: int=10):
    return fake_items_db[skip:skip + limit]

@app.get("/regions/")
async def get_regions():
    return regions

@app.get("/years/")
async def get_years():
    return years

@app.get("/data/")
async def get_data(region: str="APAC", year: int=2020):
    data = pd.read_csv("data/location_data.csv", index_col='City')
    cols = [c for c in data.columns if 'Demand' not in c]
    demand_year = f"Demand_{year}"
    cols.append(demand_year)
    return data[cols].to_json()

@app.get("/greenfield/")
async def run_greenfield(
    n_locs: int=1,
    iters: int=10,
    dist_max: Optional[float]=None,
    cap_min: float=0,
    cap_max: Optional[float]=None,
    demand: List[float]=Query(None), 
    custLat: List[float]=Query(None),
    custLon: List[float]=Query(None)):
    '''Pass data to the greenfield algorithm'''
    print("Running model")
    if dist_max is None:
        dist_max = np.inf
    if cap_max is None:
        cap_max = np.inf
    model = BaseGreenFieldModel(n=n_locs, iters=iters, 
        dist_max=dist_max, cap_min=cap_min, cap_max=cap_max)
    demand = np.array(demand).astype(float)
    custLat = np.array(custLat).astype(float)
    custLon = np.array(custLon).astype(float)
    solns = model.run_algorithm(demand, custLat, custLon)
    return utils.convert_results_to_json(solns)
