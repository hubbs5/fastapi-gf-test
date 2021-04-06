import os
import sys
import requests
import json
import pandas as pd
import numpy as np

src_dir = os.path.join(os.path.dirname(os.getcwd()), 'app')
sys.path.append(src_dir)

from greenfield import BaseGreenFieldModel

_url = "http://127.0.0.1:8000/"

def test_item_response():
    url = _url + "items/"
    response = requests.get(url)
    assert response.status_code == 200, f"Invalid response: {response.status_code}"

def test_post():
    url = _url + "items/"
    params = {"skip": 0, "limit": 3}
    response = requests.get(url, params=params)
    print(response.json())
    assert response.status_code == 200, f"Invalid response: {response.status_code}"

def test_get_regions():
    url = _url + "regions/"
    response = requests.get(url)
    print(response.json())
    assert response.status_code == 200, f"Invalid response: {response.status_code}"

def test_get_years():
    url = _url + "years/"
    response = requests.get(url)
    assert response.status_code == 200, f"Invalid response: {response.status_code}"

def test_get_data():
    url = _url + "data/"
    params = {"region": "APAC", "year": 2020}
    response = requests.get(url, params=params)
    assert response.status_code == 200, f"Invalid response: {response.status_code}"
    return response.json()

def test_greenfield_model():
    data = json.loads(test_get_data())
    dem_key = [k for k in data.keys() if 'Demand' in k][0]
    demand = np.array([float(i) for i in data[dem_key].values()])
    custLat = np.array([float(i) for i in data['Latitude'].values()])
    custLon = np.array([float(i) for i in data['Longitude'].values()])
    n_locs = 5
    iters = 10
    dist_max = np.inf
    cap_min = 0
    cap_max = sum(demand)
    model = BaseGreenFieldModel(n_locs, iters, dist_max, cap_min, cap_max)
    solns = model.run_algorithm(demand, custLat, custLon)
    return solns

def test_greenfield_api():
    url = _url + "greenfield/"
    data = json.loads(test_get_data())
    dem_key = [k for k in data.keys() if 'Demand' in k][0]
    demand = [float(i) for i in data[dem_key].values()]
    custLat = [float(i) for i in data['Latitude'].values()]
    custLon = [float(i) for i in data['Longitude'].values()]
    n_locs = 1
    iters = 10
    dist_max = 1000000
    cap_min = 0
    cap_max = sum(demand)
    params = {
        # "n_locs": n_locs,
        # "iters": iters,
        # "dist_max": dist_max,
        # "cap_min": cap_min,
        # "cap_max": cap_max,
        "demand": demand,
        "custLat": custLat,
        "custLon": custLon
    }
    response = requests.get(url, params=params)
    assert response.status_code == 200, f"Invalide response: {response.status_code}"


