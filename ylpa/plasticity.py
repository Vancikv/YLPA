'''
Created on Nov 18, 2014

@author: Werner
'''

import numpy as np

from traits.api import \
    HasStrictTraits, Float, Property, List, \
    cached_property, WeakRef, Event, \
    on_trait_change

from traitsui.api import \
    View, Item, HGroup, Group, \
    VGroup

from tree_nodes import YLPALeafNode

from scipy.optimize import brentq, newton

class Reinforcement(YLPALeafNode):
    plateref = WeakRef
    node_name = 'default_reinforcement'
    @on_trait_change('+mat_input')
    def notify_change(self):
        if self.plateref: self.plateref.reinf_data_changed = True

    d1_1 = Float(0.03, mat_input=True)
    d1_2 = Float(0.03, mat_input=True)
    '''Distances of reinforcement from the tensile edge'''

    d1_1u = Float(0.03, mat_input=True)
    d1_2u = Float(0.03, mat_input=True)
    '''Distances of upper reinforcement from the tensile edge'''

    p1 = Float(0.01, mat_input=True)
    p2 = Float(0.01, mat_input=True)
    '''Reinforcement ratios in orthogonal directions'''

    p1u = Float(0.01, mat_input=True)
    p2u = Float(0.01, mat_input=True)
    '''Upper reinforcement ratios in orthogonal directions'''

    alfa1 = Float(0., mat_input=True)
    '''Orientation of axis 1 (corresponds to reinforcement ratios p1 and p1u)'''

    tree_view = View(VGroup(
                         Group(Item('node_name', show_label=False),
                               label='Layout name'),
                         Group(Item('alfa1'),
                               label='Angle of main direction'),
                         HGroup(Group(Item('p1'),
                                      Item('p2'),
                                      Item('d1_1'),
                                      Item('d1_2'),
                                      springy=True,
                                      label='Bottom surface reinforcement parameters'
                                      ),
                                Group(Item('p1u'),
                                      Item('p2u'),
                                      Item('d1_1u'),
                                      Item('d1_2u'),
                                      springy=True,
                                      label='Top surface reinforcement parameters'
                                      ),
                                ),
                     )
                     )

class PlasticMomentDefinition(HasStrictTraits):
    backref = WeakRef
    def get_plastic_moment(self, angle):
        pass
    def get_negative_plastic_moment(self, angle):
        pass
    def __getstate__ (self):
        '''Overriding __getstate__ because of WeakRef usage
        '''
        state = super(PlasticMomentDefinition, self).__getstate__()

        for key in [ 'backref', 'backref_' ]:
            if state.has_key(key):
                del state[ key ]

        return state

class PMDSimple(PlasticMomentDefinition):
    def get_plastic_moment(self, angle):
        return 1.
    def get_negative_plastic_moment(self, angle):
        return 1.

class PMDOrthoReinfDep(PlasticMomentDefinition):
    '''Orthotropic reinforcement, compressive zone dependent of the section orientation.
    '''
    def get_plastic_moment(self, angle):
        reinf = self.backref.reinforcement_
        plate = self.backref.plateref
        fi = angle - reinf.alfa1
        N1 = plate.h * reinf.p1 * plate.f_y
        N2 = plate.h * reinf.p2 * plate.f_y
        a = (N1 * (np.sin(fi) ** 2) + N2 * (np.cos(fi) ** 2)) / plate.f_c
        r1 = plate.h - reinf.d1_1 - a / 2
        r2 = plate.h - reinf.d1_2 - a / 2
        Mp1 = N1 * r1
        Mp2 = N2 * r2
        Mp = Mp1 * (np.sin(fi) ** 2) + Mp2 * (np.cos(fi) ** 2)
        return Mp

    def get_negative_plastic_moment(self, angle):
        reinf = self.backref.reinforcement_
        plate = self.backref.plateref
        fi = angle - reinf.alfa1
        N1 = plate.h * reinf.p1u * plate.f_y
        N2 = plate.h * reinf.p2u * plate.f_y
        a = (N1 * (np.sin(fi) ** 2) + N2 * (np.cos(fi) ** 2)) / plate.f_c
        r1 = plate.h - reinf.d1_1u - a / 2
        r2 = plate.h - reinf.d1_2u - a / 2
        Mp1 = N1 * r1
        Mp2 = N2 * r2
        Mp = Mp1 * (np.sin(fi) ** 2) + Mp2 * (np.cos(fi) ** 2)
        return Mp

class PMDOrthoReinfDepDuctCheck(PlasticMomentDefinition):
    '''
    Orthotropic reinforcement, compressive zone dependent of the section orientation.
    Reinforcement ratio itself is calculated depending on angle, which allows to compute ductility.
    '''
    eps_c = Float
    eps_s = Float
    '''Deformation in concrete and steel (both positive as only pure bending is relevant).'''

    p = Float
    d1 = Float
    pu = Float
    d1u = Float

    a = Property(depends_on='eps_c,eps_s')
    '''Compressive zone'''
    @cached_property
    def _get_a(self):
        return (self.eps_c / (self.eps_c + self.eps_s)) * (self.backref.plateref.h - self.d1)

    curvature = Property(depends_on='eps_c,eps_s')
    '''Curvature'''
    @cached_property
    def _get_curvature(self):
        return (self.eps_c + self.eps_s) / (self.backref.plateref.h - self.d1)

    moment = Property(depends_on='eps_c,eps_s')
    '''Bending moment'''
    @cached_property
    def _get_moment(self):
        M = 0.
        plate = self.backref.plateref
        M += plate.f_y * self.p * plate.h * (plate.h - self.d1)
        for i in range(20):
            eps = ((i + 0.5) / 20) * self.eps_c
            dN = self.get_sigma_c(eps) * self.a / 20.
            r = (1 - ((i + 0.5) / 20)) * self.a
            M -= dN * r
        return M

    def get_sigma_c(self, eps):
        eta = eps / self.plateref.eps_c1
        plate = self.backref.plateref
        sigma = plate.f_c * (plate.parab_k * eta - eta ** 2) / (1 + (plate.parab_k - 2) * eta)
        if sigma > plate.f_c: print sigma
        return sigma

    def get_N(self, val, attr):
        setattr(self, attr, val)
        N = 0.
        plate = self.backref.plateref
        N -= plate.f_y * self.p * plate.h
        for i in range(20):
            eps = ((i + 0.5) / 20) * self.eps_c
            dN = self.get_sigma_c(eps) * self.a / 20.
            N += dN
        # print 'compute N: eps_c=%f, eps_s=%f, N=%f' % (self.eps_c, self.eps_s, N)
        return N

    def get_mom_crv(self, angle):
        '''Return yield and ultimate curvature.'''
        self.set_vals(angle)
        plate = self.backref.plateref
        eps_y = plate.f_y / plate.E_s
        self.eps_s = eps_y
        brentq(f=self.get_N, a=0., b=plate.eps_cu1, args=('eps_c',))
        yld = (self.moment, self.curvature)
        self.eps_c = plate.eps_cu1
        newton(func=self.get_N, x0=eps_y, args=('eps_s',))
        if self.eps_s > plate.eps_su:
            self.eps_s = plate.eps_su
            brentq(f=self.get_N, a=0., b=plate.eps_cu1, args=('eps_c',))
        ult = (self.moment, self.curvature)
        return yld + ult

    def get_negative_mom_crv(self, angle):
        '''Return yield and ultimate curvature.'''
        self.set_vals(angle)
        plate = self.backref.plateref
        eps_y = plate.f_y / plate.E_s
        self.eps_s = eps_y
        brentq(f=self.get_N, a=0., b=plate.eps_cu1, args=('eps_c',))
        yld = (self.moment, self.curvature)
        self.eps_c = plate.eps_cu1
        newton(func=self.get_N, x0=eps_y, args=('eps_s',))
        if self.eps_s > plate.eps_su:
            self.eps_s = plate.eps_su
            brentq(f=self.get_N, a=0., b=plate.eps_cu1, args=('eps_c',))
        ult = (self.moment, self.curvature)
        return yld + ult

    def set_vals(self, angle):
        reinf = self.backref.reinforcement_
        fi = angle - reinf.alfa1
        p1 = reinf.p1 * (np.sin(fi) ** 2)
        p2 = reinf.p2 * (np.cos(fi) ** 2)
        self.p = p1 + p2
        self.d1 = (p1 * reinf.d1_1 + p2 * reinf.d1_2) / self.p
        p1u = reinf.p1u * (np.sin(fi) ** 2)
        p2u = reinf.p2u * (np.cos(fi) ** 2)
        self.pu = p1u + p2u
        self.d1u = (p1u * reinf.d1_1u + p2u * reinf.d1_2u) / self.pu

    def get_plastic_moment(self, angle):
        self.set_vals(angle)
        plate = self.backref.plateref
        N = plate.h * self.p * plate.f_y
        a = N / plate.f_c
        r = plate.h - self.d1 - a / 2
        Mp = N * r
        return Mp

    def get_negative_plastic_moment(self, angle):
        self.set_vals(angle)
        plate = self.backref.plateref
        N = plate.h * self.pu * plate.f_y
        a = N / plate.f_c
        r = plate.h - self.d1u - a / 2
        Mp = N * r
        return Mp

class PMDOrthoReinfDepDuctCheckCompReinf(PlasticMomentDefinition):
    '''
    Orthotropic reinforcement, compressive zone dependent of the section orientation.
    Reinforcement ratio itself is calculated depending on angle, which allows to compute ductility.
    Reinforcement in compression is considered.

    NOT FINISHED

    '''
    eps_c = Float
    eps_s = Float
    '''Deformation in concrete and steel (both positive as only pure bending is relevant).'''

    p = Float
    d1 = Float
    pu = Float
    d1u = Float

    a = Property(depends_on='eps_c,eps_s')
    '''Compressive zone'''
    @cached_property
    def _get_a(self):
        return (self.eps_c / (self.eps_c + self.eps_s)) * (self.plateref.h - self.d1)

    curvature = Property(depends_on='eps_c,eps_s')
    '''Curvature'''
    @cached_property
    def _get_curvature(self):
        return (self.eps_c + self.eps_s) / (self.plateref.h - self.d1)

    moment = Property(depends_on='eps_c,eps_s')
    '''Bending moment'''
    @cached_property
    def _get_moment(self):
        M = 0.
        M += self.plateref.f_y * self.p * self.plateref.h * (self.plateref.h - self.d1)
        for i in range(20):
            eps = ((i + 0.5) / 20) * self.eps_c
            dN = self.get_sigma_c(eps) * self.a / 20.
            r = (1 - ((i + 0.5) / 20)) * self.a
            M -= dN * r
        return M

    def get_sigma_c(self, eps):
        eta = eps / self.plateref.eps_c1
        sigma = self.plateref.f_c * (self.plateref.parab_k * eta - eta ** 2) / (1 + (self.plateref.parab_k - 2) * eta)
        if sigma > self.plateref.f_c: print sigma
        return sigma

    def get_N(self, val, attr):
        setattr(self, attr, val)
        N = 0.
        N -= self.plateref.f_y * self.p * self.plateref.h
        for i in range(20):
            eps = ((i + 0.5) / 20) * self.eps_c
            dN = self.get_sigma_c(eps) * self.a / 20.
            N += dN
        # print 'compute N: eps_c=%f, eps_s=%f, N=%f' % (self.eps_c, self.eps_s, N)
        return N

    def get_mom_crv(self, angle):
        '''Return yield and ultimate curvature.'''
        self.set_vals(angle)
        eps_y = self.plateref.f_y / self.plateref.E_s
        self.eps_s = eps_y
        brentq(f=self.get_N, a=0., b=self.plateref.eps_cu1, args=('eps_c',))
        yld = (self.moment, self.curvature)
        self.eps_c = self.plateref.eps_cu1
        newton(func=self.get_N, x0=eps_y, args=('eps_s',))
        if self.eps_s > self.plateref.eps_su:
            self.eps_s = self.plateref.eps_su
            brentq(f=self.get_N, a=0., b=self.plateref.eps_cu1, args=('eps_c',))
        ult = (self.moment, self.curvature)
        return yld + ult

    def get_negative_mom_crv(self, angle):
        '''Return yield and ultimate curvature.'''
        self.set_vals(angle)
        eps_y = self.plateref.f_y / self.plateref.E_s
        self.eps_s = eps_y
        brentq(f=self.get_N, a=0., b=self.plateref.eps_cu1, args=('eps_c',))
        yld = (self.moment, self.curvature)
        self.eps_c = self.plateref.eps_cu1
        newton(func=self.get_N, x0=eps_y, args=('eps_s',))
        if self.eps_s > self.plateref.eps_su:
            self.eps_s = self.plateref.eps_su
            brentq(f=self.get_N, a=0., b=self.plateref.eps_cu1, args=('eps_c',))
        ult = (self.moment, self.curvature)
        return yld + ult

    def set_vals(self, angle):
        reinf = self.backref.reinforcement_
        fi = angle - reinf.alfa1
        p1 = reinf.p1 * (np.sin(fi) ** 2)
        p2 = reinf.p2 * (np.cos(fi) ** 2)
        self.p = p1 + p2
        self.d1 = (p1 * reinf.d1_1 + p2 * reinf.d1_2) / self.p
        p1u = reinf.p1u * (np.sin(fi) ** 2)
        p2u = reinf.p2u * (np.cos(fi) ** 2)
        self.pu = p1u + p2u
        self.d1u = (p1u * reinf.d1_1u + p2u * reinf.d1_2u) / self.pu

    def get_plastic_moment(self, angle):
        self.set_vals(angle)
        plate = self.backref.plateref
        N = plate.h * self.p * plate.f_y
        a = N / plate.f_c
        r = plate.h - self.d1 - a / 2
        Mp = N * r
        return Mp

    def get_negative_plastic_moment(self, angle):
        self.set_vals(angle)
        plate = self.backref.plateref
        N = plate.h * self.pu * plate.f_y
        a = N / plate.f_c
        r = plate.h - self.d1u - a / 2
        Mp = N * r
        return Mp

class PMDOrthoReinfIndep(PlasticMomentDefinition):
    '''Orthotropic reinforcement, compressive zone independent of the section orientation.
    '''
    def get_plastic_moment(self, angle):
        reinf = self.backref.reinforcement_
        plate = self.backref.plateref
        fi = angle - reinf.alfa1
        N1 = plate.h * reinf.p1 * plate.f_y
        N2 = plate.h * reinf.p2 * plate.f_y
        a1 = N1 / plate.f_c
        a2 = N2 / plate.f_c
        r1 = plate.h - reinf.d1_1 - a1 / 2
        r2 = plate.h - reinf.d1_2 - a2 / 2
        Mp1 = N1 * r1
        Mp2 = N2 * r2
        Mp = Mp1 * (np.sin(fi) ** 2) + Mp2 * (np.cos(fi) ** 2)
        return Mp

    def get_negative_plastic_moment(self, angle):
        reinf = self.backref.reinforcement_
        plate = self.backref.plateref
        fi = angle - reinf.alfa1
        N1 = plate.h * reinf.p1u * plate.f_y
        N2 = plate.h * reinf.p2u * plate.f_y
        a1 = N1 / plate.f_c
        a2 = N2 / plate.f_c
        r1 = plate.h - reinf.d1_1u - a1 / 2
        r2 = plate.h - reinf.d1_2u - a2 / 2
        Mp1 = N1 * r1
        Mp2 = N2 * r2
        Mp = Mp1 * (np.sin(fi) ** 2) + Mp2 * (np.cos(fi) ** 2)
        return Mp

class PMDOrthoReinfIndepUni(PlasticMomentDefinition):
    '''Orthotropic reinforcement, compressive zone independent of the section orientation,
    unified lever for both directions
    '''
    def get_plastic_moment(self, angle):
        reinf = self.backref.reinforcement_
        plate = self.backref.plateref
        fi = angle - reinf.alfa1
        N1 = plate.h * reinf.p1 * plate.f_y
        N2 = plate.h * reinf.p2 * plate.f_y
        a = (N1 / plate.f_c + N2 / plate.f_c) / 2.
        # r = plate.h - plate.d1_1 - a / 2.
        r = plate.h - (plate.d1_1 + plate.d1_2) / 2 - a / 2.
        Mp1 = N1 * r
        Mp2 = N2 * r
        Mp = Mp1 * (np.sin(fi) ** 2) + Mp2 * (np.cos(fi) ** 2)
        return Mp

    def get_negative_plastic_moment(self, angle):
        reinf = self.backref.reinforcement_
        plate = self.backref.plateref
        fi = angle - reinf.alfa1
        N1 = plate.h * reinf.p1u * plate.f_y
        N2 = plate.h * reinf.p2u * plate.f_y
        a = (N1 / plate.f_c + N2 / plate.f_c) / 2.
        # r = plate.h - plate.d1_1u - a / 2.
        r = plate.h - (plate.d1_1u + plate.d1_2u) / 2 - a / 2.
        Mp1 = N1 * r
        Mp2 = N2 * r
        Mp = Mp1 * (np.sin(fi) ** 2) + Mp2 * (np.cos(fi) ** 2)
        return Mp
