'''
Created on 30. 1. 2015

@author: Kapsak
'''

from traits.api import \
    HasTraits, Str, Int, WeakRef, on_trait_change, \
    Tuple, Float, Trait, Enum, cached_property, \
    Property, Event

from traitsui.api import \
    View, Item, VGroup

from tree_nodes import \
    YLPALeafNode

import numpy as np

class YieldLine(YLPALeafNode):
    def __init__(self, node1=1, node2=2):
        self.node1 = node1
        self.node2 = node2

    node1 = Int(input=True)
    node2 = Int(input=True)
    theta = Float
    mom_crv_info = Tuple
    plateref = WeakRef
    pmd_changed = Event
    type = Enum('positive', ['positive', 'negative', 'inactive'])

    @on_trait_change('+input')
    def notify_change(self):
        if self.plateref: self.plateref.yield_lines_changed = True

    angle = Property()
    def _get_angle(self):
        n1, n2 = self.plateref.nodes_with_ref[self.node1 - 1], self.plateref.nodes_with_ref[self.node2 - 1]
        angle = np.arctan2(n2.y - n1.y, n2.x - n1.x)
        return angle

    length = Property()
    def _get_length(self):
        n1, n2 = self.plateref.nodes_with_ref[self.node1 - 1], self.plateref.nodes_with_ref[self.node2 - 1]
        ln = np.sqrt((n2.y - n1.y) ** 2 + (n2.x - n1.x) ** 2)
        return ln

    plastic_moment_def = Property(depends_on="pmd_changed")
    # @cached_property
    def _get_plastic_moment_def(self):
        return self.plateref.plastic_moment_def_type_(backref=self)

    tree_view = View(VGroup(Item('node1', label='Node 1'),
                            Item('node2', label='Node 2'),
                            Item('reinforcement')))
