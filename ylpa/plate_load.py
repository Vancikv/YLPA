'''
Created on 17. 11. 2014

@author: Kapsak
'''

import numpy as np
from traits.api import \
    WeakRef, HasTraits, Property, \
    cached_property, Event, Int, Float, Str, \
    on_trait_change

from tree_nodes import \
    YLPALeafNode

from traitsui.api import \
    View, VGroup, Item

class PlateLoad(YLPALeafNode):
    load_factor_multiplier = Float(1., input=True)
    plateref = WeakRef
    node_data_changed = Event

    @on_trait_change('+input')
    def notify_change(self):
        if self.plateref: self.plateref.load_data_changed = True

class PlateLoadUniform(PlateLoad):
    unit_work = Property(depends_on='node_data_changed')
    # @cached_property
    def _get_unit_work(self):
        return self.plateref.unit_volume * self.load_factor_multiplier

    load_vector = Property()
    def _get_load_vector(self):
        unn = self.plateref.unsupported_node_nos
        nds = self.plateref.nodes_with_ref
        vect = np.zeros(len(unn))
        for i in range(len(unn)):
            vect[i] = nds[unn[i]].linprog_k
        return vect

    node_name = Str('Uniform load')
    tree_view = View(VGroup(Item('load_factor_multiplier'),
                            ))

class PlateLoadNodalForce(PlateLoad):
    x = Float(0., input=True)
    y = Float(0., input=True)
    unit_work = Property(depends_on='node_data_changed')
    # @cached_property
    def _get_unit_work(self):
        return self.plateref.segments_with_ref[self.segment_no].get_point_deflection([self.x, self.y]) * self.load_factor_multiplier

    segment_no = Property()
    '''Number of the segment where the load lies
    '''
    def _get_segment_no(self):
        return self.plateref.get_segment_by_coords(self.x, self.y)

    load_vector = Property()
    def _get_load_vector(self):
        unn = self.plateref.unsupported_node_nos
        nds = self.plateref.nodes_with_ref
        vect = np.zeros(len(unn))
        sg = self.plateref.segments_with_ref[self.segment_no]
        node_nos = sg.real_node_nos
        nds = [nds[i] for i in node_nos]
        cfs = np.zeros(len(nds))

        x1, x2, x3 = nds[0].x, nds[1].x, nds[2].x
        y1, y2, y3 = nds[0].y, nds[1].y, nds[2].y
        j_c = (x3 - x1) * (y2 - y1) - (x2 - x1) * (y3 - y1)

        cfs[0] = 1 - (x1 * (y3 - y2) + y1 * (x2 - x3)) / j_c + self.x * (y3 - y2) / j_c + self.y * (x2 - x3) / j_c
        cfs[1] = (x1 * y3 - y1 * x3) / j_c + self.x * (y1 - y3) / j_c + self.y * (x3 - x1) / j_c
        cfs[2] = (y1 * x2 - x1 * y2) / j_c + self.x * (y2 - y1) / j_c + self.y * (x1 - x2) / j_c

        for i in range(len(cfs)):
            try:
                vect[unn.index(node_nos[i])] = cfs[i] * self.load_factor_multiplier
            except ValueError:
                pass
        return vect

    node_name = Str('Force load')
    tree_view = View(VGroup(Item('load_factor_multiplier'),
                            Item('x'),
                            Item('y')
                            ))
