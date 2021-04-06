import os
import sys
import numpy as np
from copy import deepcopy

src_dir = os.path.join(os.getcwd())
sys.path.append(src_dir)

# Cusotm modules
import utils
from optimization.optimization import CustomerAllocationModel
from optimization.initialization import GreenfieldRandomInit

class BaseGreenFieldModel:

    def __init__(self, n, iters=10, dist_max=np.inf, 
        cap_min=0, cap_max=np.inf):

        self.n = n
        self.iters = iters
        self.dist_max = dist_max
        self.cap_min = cap_min
        self.cap_max = cap_max

    def initialize_model(self, demand, lat_c, lon_c):
        print("Model initialized")
        init_soln = GreenfieldRandomInit(self.n, lat_c, lon_c)
        init_obj = utils.calc_objective(
            init_soln.dc_locs,
            init_soln.cust_assignment,
            demand,
            init_soln.lat_c,
            init_soln.lon_c
        )
        return init_soln, init_obj

    def _calc_new_dc_locs(self, dc_locs, assignment, lat_c, lon_c):
        new_dc_locs = np.zeros(dc_locs.shape)
        for i, _ in enumerate(dc_locs):
            cust = np.where(assignment==i)[0]
            if len(cust) == 0:
                new_dc_locs[i] += dc_locs[i]
                continue
            lat_mean = lat_c[cust].mean()
            lon_mean = lon_c[cust].mean()
            new_dc_locs[i] += [lat_mean, lon_mean]
        
        return new_dc_locs

    def run_algorithm(self, demand, lat_c, lon_c):
        solns = {}
        for k in range(self.iters):
            if k == 0:
                init_soln, obj = self.initialize_model(demand, lat_c, lon_c)
                dc_locs = init_soln.dc_locs.copy()
                solns[k] = {
                    'model': init_soln,
                    'obj': obj,
                    'dc_locs': dc_locs,
                    'assignment': init_soln.cust_assignment
                }
            else:
                new_locs = self._calc_new_dc_locs(dc_locs, opt_assignment, 
                    lat_c, lon_c)
                dc_locs = new_locs.copy()
            
            model = CustomerAllocationModel(dc_locs, demand, lat_c, lon_c,
                self.dist_max, self.cap_min, self.cap_max)
            results, m = model.solve()
            opt_assignment = utils.get_opt_assignment(m)

            solns[k+1] = {
                'model': deepcopy(m),
                'obj': m.obj.expr(),
                'dc_locs': dc_locs.copy(),
                'assignment': opt_assignment
            }

            if m.obj.expr() >= obj:
                print(f"Iteration k={k} yields " +
                      f"{100*(1-m.obj.expr()/obj):.1f}% improvement.")
                print(f"Stopping after {k} iterations.")
                return solns
            else:
                print(f"Iteration k={k} yields " +
                      f"{100*(1-m.obj.expr()/obj):.1f}% improvement.")
            obj = m.obj.expr()

        print(f"Max iterations ({self.iters}) reached.")
        return solns




