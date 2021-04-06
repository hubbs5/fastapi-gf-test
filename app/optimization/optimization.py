import numpy as np
from pyomo.environ import *
from pyomo.opt import SolverFactory

from utils import calc_distance

class CustomerAllocationModel:

    def __init__(self, dc_locs, demand, lat_c, lon_c,
        dist_max=np.inf, cap_min=0, cap_max=np.inf):

        self.dc_locs = dc_locs
        self.demand = demand
        self.lat_c = lat_c
        self.lon_c = lon_c
        self.dist_max = dist_max
        self.cap_min = cap_min
        self.cap_max = cap_max

    def build_allocation_model(self):
        '''
        Builds math programming model for binary allocation.
        '''
        m = ConcreteModel()

        m.i = Set(initialize=np.arange(len(self.dc_locs)))
        m.j = Set(initialize=np.arange(len(self.lat_c)))
        m.dc_assignment = Var(m.i, m.j, within=Binary)

        m.lat_cust = Param(m.j,
            initialize={i:j for i, j in enumerate(self.lat_c)})
        m.lon_cust = Param(m.j,
            initialize={i:j for i, j in enumerate(self.lon_c)})
        m.demand = Param(m.j,
            initialize={i:j for i, j in enumerate(self.demand)})
        # m.distance = Param(m.i, m.j,
            # initialize={(i, k): calc_distance(j, (l[0], l[1]))
            # }
            # )
        m.distance = Param(m.i, m.j,
            initialize={(i, k): calc_distance(j, (l[0], l[1]))
                for i, j in enumerate(self.dc_locs)
                for k, l in enumerate(zip(self.lat_c, self.lon_c))},
            mutable=True)

        m.dist_max = self.dist_max
        m.cap_min = self.cap_min
        m.cap_max = self.cap_max
        m.distribution_center_locs = self.dc_locs

        @m.Constraint(m.j)
        def assignment_constraint(m, j):
            return sum(m.dc_assignment[i, j] for i in m.i) == 1

        @m.Constraint(m.i, m.j)
        def distance_constraint(m, i, j):
            return m.distance[i, j] * m.dc_assignment[i, j] <= m.dist_max
        
        @m.Constraint(m.i)
        def min_cap_constraint(m, i):
            return sum(m.dc_assignment[i, j] * m.demand[j] for j in m.j) >= m.cap_min

        @m.Constraint(m.i)
        def max_cap_constraint(m, i):
            return sum(m.dc_assignment[i, j] * m.demand[j] for j in m.j) <= m.cap_max

        m.obj = Objective(expr=(
            sum(m.demand[j] * m.distance[i, j] * m.dc_assignment[i, j]
            for i in m.i
            for j in m.j)),
            sense=minimize)

        return m

    def solve(self, solver='glpk', print_output=False):
        model = self.build_allocation_model()
        py_solver = SolverFactory(solver)
        results = py_solver.solve(model, tee=print_output)

        return results, model