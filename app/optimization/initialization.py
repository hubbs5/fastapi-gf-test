import os
import numpy as np

class GreenfieldRandomInit:

    def __init__(self, n, lat_c, lon_c):

        self.n = n
        self.lat_c = lat_c
        self.lon_c = lon_c
        # assert len(lon_c) == len(lat_c)
        try:
            self.n_customers = len(self.lat_c)
        except TypeError:
            print(self.lat_c, type(self.lat_c))

        self.dc_locs = self._initialize_distribution_center_locs()
        self.cust_assignment = self._initialize_customer_assignment()

    def _initialize_distribution_center_locs(self):
        '''Returns random distribution center locations'''
        # Get bounds from lat/lon
        lat_min, lat_max = min(self.lat_c), max(self.lat_c)
        lon_min, lon_max = min(self.lon_c), max(self.lon_c)

        centers = np.random.rand(2, self.n)
        lats = lat_min + (lat_max - lat_min) * centers[0]
        lons = lon_min + (lon_max - lon_min) * centers[1]
        return np.vstack([lats, lons]).T

    def _initialize_customer_assignment(self):
        '''Returns random customer to distribution center assignment'''
        return np.random.choice(np.arange(self.n), size=self.n_customers)




