'''
Created on 27. 5. 2015

@author: Kapsak
'''

import numpy as np
from linprog import linprog
from lp_solve import *

from traits.api import \
    HasStrictTraits, Float, Property, List, \
    cached_property, WeakRef, Event, \
    on_trait_change, Instance, Trait, \
    Str, Dict, Any, Int, Bool

from traitsui.api import \
    View, Item, HGroup, Group, \
    VGroup

from plate import \
    Plate

from utils import \
    gauss

class LinearProgramming(HasStrictTraits):
    plate = Instance(Plate)
    verbose = Bool(False)

    solution = Property()
    def _get_solution(self):
        for nd in self.plate.nodes_with_ref:
            if nd.w != 0.:
                nd.reset_traits(['w'])
        p = self.plate
        unn = p.unsupported_node_nos
        w_dim = len(unn)
        c = np.hstack([p.linprog_vect_c, np.zeros(2 * w_dim)])
        if self.verbose: print 'Vector c:', c
        k = p.linprog_vect_k
        if self.verbose: print 'Vector k:', k
        B = p.linprog_matrix_B
        if self.verbose: print 'Matrix B:', B

        A_eq = np.vstack([np.hstack([np.identity(B.shape[0]), -np.identity(B.shape[0]), -B, B]),
                          np.hstack([np.zeros(B.shape[0]), np.zeros(B.shape[0]), k, -k]),
                          ])
        b_eq = np.zeros(A_eq.shape[0])
        b_eq[-1] = 1.
        print 'Simplex method input assembled succesfully.'
        print 'Dimensions of vector c:', c.shape
        print 'Dimensions of matrix A_eq:', A_eq.shape
        print 'Dimensions of vector b_eq:', b_eq.shape
        if self.verbose:
            print 'Vector c:', c
            print 'Matrix A_eq:', A_eq
            print 'Vector b_eq:', b_eq

        sol = lp_solve(f=c, a=A_eq, b=b_eq, e=np.zeros_like(b_eq))

        w_plus = np.array(sol[1][-2 * w_dim:-w_dim])
        w_minus = np.array(sol[1][-w_dim:])
        w = w_plus - w_minus

        for i in range(len(w)):
            p.nodes_with_ref[unn[i]].w = w[i]
        if self.verbose: print 'Resulting w:', w
        return sol

    dual_solution = Property()
    def _get_dual_solution(self):
        p = self.plate
        w_dim = len(p.unsupported_node_nos)
        b_ub = np.hstack([p.linprog_vect_c, np.zeros(2 * w_dim)])
        if self.verbose: print 'Vector b_ub:', b_ub
        k = p.linprog_vect_k
        if self.verbose: print 'Vector k:', k
        B = p.linprog_matrix_B
        if self.verbose: print 'Matrix B:', B

        A_eq = np.vstack([np.hstack([np.identity(B.shape[0]), -np.identity(B.shape[0]), -B, B]),
                          np.hstack([np.zeros(B.shape[0]), np.zeros(B.shape[0]), k, -k]),
                          ])

        A_ub = np.transpose(A_eq)
        c = np.zeros(A_ub.shape[1])
        c[-1] = -1.
        print 'Simplex method input assembled succesfully.'
        print 'Dimensions of vector c:', c.shape
        print 'Dimensions of matrix A_ub:', A_ub.shape
        print 'Dimensions of vector b_ub:', b_ub.shape
        if self.verbose:
            print 'Vector c:', c
            print 'Matrix A_ub:', A_ub
            print 'Vector b_ub:', b_ub

        sol = sol = lp_solve(f=c, a=A_ub, b=b_ub, e=-np.ones_like(b_ub))
        return sol

    solution_static = Property()
    def _get_solution_static(self):
        p = self.plate
        k = p.linprog_vect_k
        if self.verbose: print 'Vector k:', k
        C = p.linprog_static_matrix
        if self.verbose: print 'Matrix C:', C

        A_eq = np.vstack([np.hstack([C, -C, np.zeros_like(C), np.reshape(-k, (len(k), 1))]),
                          np.hstack([np.identity(C.shape[1]), np.identity(C.shape[1]), np.identity(C.shape[1]), np.reshape(np.zeros(C.shape[1]), (C.shape[1], 1))]),
                          ])
        c = np.zeros(C.shape[1] * 3 + 1)
        c[-1] = -1.

        b_eq = np.hstack([np.zeros(C.shape[0]), np.ones(C.shape[1])])
        print 'Simplex method input assembled succesfully.'
        print 'Dimensions of vector c:', c.shape
        print 'Dimensions of matrix A_eq:', A_eq.shape
        print 'Dimensions of vector b_eq:', b_eq.shape
        if self.verbose:
            print 'Vector c:', c
            print 'Matrix A_eq:', A_eq
            print 'Vector b_eq:', b_eq

        sol = lp_solve(f=c, a=A_eq, b=b_eq, e=np.zeros_like(b_eq))
        return sol

