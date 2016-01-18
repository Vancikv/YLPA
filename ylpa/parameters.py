'''
Created on 1. 2. 2015

@author: Kapsak
'''

from traits.api import \
    Float, Str, Int, on_trait_change, WeakRef

from tree_nodes import \
    YLPATreeNode

class Parameter(YLPATreeNode):
    base_value = Float(0.)
    minimum = Float(None)
    maximum = Float(None)
    optimization_constrain_multiplier = Float(1.)
    pstudyref = WeakRef
    @on_trait_change('+')
    def notify_change(self):
        if self.pstudyref: self.pstudyref.params_changed = True

    def __getitem__(self, i):
        if i == 0: return self.base_value
        if i == 1: return (self.minimum, self.maximum)

    def __getstate__(self):
        state = super(Parameter, self).__getstate__()

        for key in ['minimum', 'maximum']:
            if state[key] == None:
                del state[key]
        for key in [ 'pstudyref', 'pstudyref_' ]:
            if state.has_key(key):
                del state[ key ]
        return state

class ParamNode(YLPATreeNode):
    node_no = Int()
    trait_name = Str()
    param_no = Int()
    multiplier = Float(1.)
    base_value = Float(0.)
    pstudyref = WeakRef
    @on_trait_change('+')
    def notify_change(self):
        if self.pstudyref: self.pstudyref.params_changed = True
    def __getitem__(self, i):
        if i == 0: return self.node_no
        if i == 1: return self.trait_name
        if i == 2: return self.param_no
        if i == 3: return self.multiplier
        if i == 4: return self.base_value

class ParamPlate(YLPATreeNode):
    trait_name = Str()
    param_no = Int()
    multiplier = Float(1.)
    base_value = Float(0.)
    reinf_layout_name = Str()
    pstudyref = WeakRef
    @on_trait_change('+')
    def notify_change(self):
        if self.pstudyref: self.pstudyref.params_changed = True
    def __getitem__(self, i):
        if i == 0: return self.trait_name
        if i == 1: return self.param_no
        if i == 2: return self.multiplier
        if i == 3: return self.base_value
        if i == 4: return self.reinf_layout_name
