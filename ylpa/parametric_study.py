'''
Created on 17. 11. 2014

@author: Kapsak
'''

import time
import numpy as np
from scipy.optimize import minimize

from traits.api import \
    HasTraits, Float, Property, List, \
    cached_property, WeakRef, Event, \
    on_trait_change, Instance, Str

from traitsui.api import \
    View, TableEditor, Item, HGroup, Group, \
    VGroup

from traitsui.table_column import \
    ObjectColumn

from plate import \
    Plate

import matplotlib.pyplot as plt

from tree_nodes import \
    YLPATreeNode

from parameters import \
    Parameter, ParamNode, ParamPlate

METHOD = 'L-BFGS-B'

class ParametricStudy(YLPATreeNode):
    def __init__(self, *args, **kwargs):
        super(ParametricStudy, self).__init__(*args, **kwargs)
        if 'plate' not in kwargs.keys():
            self.plate = Plate()
        self.plate.pstudy = self

    plate = Instance(Plate)
    def _plate_changed(self):
        self.plate.pstudyref = self

    def __getstate__ (self):
        '''Overriding __getstate__ because of
        '''
        state = super(ParametricStudy, self).__getstate__()

        return state

    plate_changed = Event
    params_changed = Event

    node_params = List(Instance(Parameter), [])
    '''A list of tuples (base_value, (min, max))
    '''

    plate_params = List(Instance(Parameter), [])
    '''A list of tuples (base_value, (min, max))
    '''

    param_nodes = List(Instance(ParamNode), [])
    '''A list of tuples (node, trait_name, param_no, multiplier, base_value)
    '''

    param_plate = List(Instance(ParamPlate), [])
    '''A list of tuples (trait_name, param_no, multiplier, base_value)
    '''

    optimization_constrain_value = Float(0.01)

    def get_unit_work_ratio(self, vals):
        nds = self.plate.nodes_with_ref
        for pn in self.param_nodes_with_ref:
            val = pn.base_value + pn.multiplier * vals[pn.param_no - 1]
            setattr(nds[pn.node_no - 1], pn.trait_name, val)
        return self.plate.unit_work_ratio

    def get_unit_work_ratio_neg(self, vals):
        vals2 = [par[0] for par in self.node_params_with_ref]
        bds2 = [par[1] for par in self.node_params_with_ref]
        for pp in self.param_plate_with_ref:
            val = pp.base_value + pp.multiplier * vals[pp.param_no - 1]
            setattr(self.plate.reinf_dict[pp.reinf_layout_name], pp.trait_name, val)
        if len(vals2) > 0:
            res = minimize(fun=self.get_unit_work_ratio, x0=vals2, bounds=bds2, method=METHOD)
        return -self.plate.unit_work_ratio

    min_work_ratio = Property(depends_on='node_params,plate_params,param_nodes,param_plate,params_changed,plate_changed')
    @cached_property
    def _get_min_work_ratio(self):
        print 'Commencing optimization...'
        start = time.clock()
        vals = [par[0] for par in self.plate_params_with_ref]
        bds = [par[1] for par in self.plate_params_with_ref]

        if len(vals) > 0:
            res = minimize(fun=self.get_unit_work_ratio_neg, x0=vals, bounds=bds, constraints={'type':'eq', 'fun':self.constrain_function}, method='SLSQP')
        else:
            vals2 = [par[0] for par in self.node_params_with_ref]
            bds2 = [par[1] for par in self.node_params_with_ref]
            res = minimize(fun=self.get_unit_work_ratio, x0=vals2, bounds=bds2, method=METHOD)

        end = time.clock()

        print 'Optimization finished in', str(end - start), 'seconds'
        print res
        return self.plate.unit_work_ratio

    def constrain_function(self, *args):
        cns = 0.
        for i in range(len(args[0])):
            cns += args[0][i] * self.plate_params_with_ref[i].optimization_constrain_multiplier
        return cns - self.optimization_constrain_value

    def plot_plate(self):
        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.7, 0.7])
        self.plate.plot(ax)
        plt.show()

    def plot(self, fig):
        self.plate.plot(fig)

    def calculate(self, fig):
        '''Calculate the optimized limit load factor and plot geometry.
        '''
        try:
            print 'Optimized load factor: %f' % self.min_work_ratio
        except:
            print 'Optimization failed. Check input.'
        self.plate.plot(fig)
        return

    node_name = Str('Parametric study')

    tree_node_list = Property(depends_on='plate')
    @cached_property
    def _get_tree_node_list(self):
        return [self.plate]

    node_params_with_ref = Property(List(Instance(Parameter)), depends_on='node_params')
    def _get_node_params_with_ref(self):
        for i in range(len(self.node_params)):
            self.node_params[i].node_name = 'Parameter ' + str(i + 1)
            self.node_params[i].pstudyref = self
        return self.node_params

    plate_params_with_ref = Property(List(Instance(Parameter)), depends_on='plate_params')
    def _get_plate_params_with_ref(self):
        for i in range(len(self.plate_params)):
            self.plate_params[i].node_name = 'Parameter ' + str(i + 1)
            self.plate_params[i].pstudyref = self
        return self.plate_params

    param_nodes_with_ref = Property(List(Instance(ParamNode)), depends_on='param_nodes')
    def _get_param_nodes_with_ref(self):
        for i in range(len(self.param_nodes)):
            self.param_nodes[i].node_name = 'Node data ' + str(i + 1)
            self.param_nodes[i].pstudyref = self
        return self.param_nodes

    param_plate_with_ref = Property(List(Instance(ParamPlate)), depends_on='param_plate')
    def _get_param_plate_with_ref(self):
        for i in range(len(self.param_plate)):
            self.param_plate[i].node_name = 'Plate data ' + str(i + 1)
            self.param_plate[i].pstudyref = self
        return self.param_plate

    tree_view = View(HGroup(VGroup(
                     Group(Item('node_params_with_ref', editor=TableEditor(columns=[ObjectColumn(name='node_name', label='Name', editable=False),
                                                                       ObjectColumn(name='base_value', label='Default value'),
                                                                       ObjectColumn(name='minimum', label='Minimum'),
                                                                       ObjectColumn(name='maximum', label='Maximum'),
                                                                     ],
                                                             row_factory=Parameter,
                                                             show_toolbar=True,
                                                             deletable=True,
                                                             auto_size=False,
                                                             auto_add=True,
                                                            ),
                          show_label=False,
                          ), label='Node parameters:', springy=True),
                     Group(Item('param_nodes_with_ref', editor=TableEditor(columns=[ObjectColumn(name='node_name', label='Name', editable=False),
                                                                       ObjectColumn(name='node_no', label='Node Number'),
                                                                       ObjectColumn(name='trait_name', label='Unknown value name'),
                                                                       ObjectColumn(name='param_no', label='Parameter'),
                                                                       ObjectColumn(name='multiplier', label='Multiplier'),
                                                                       ObjectColumn(name='base_value', label='Default value'),
                                                                     ],
                                                             row_factory=ParamNode,
                                                             show_toolbar=True,
                                                             deletable=True,
                                                             auto_size=False,
                                                             auto_add=True,
                                                            ),
                          show_label=False,
                          ), label='Node optimization data:', springy=True)),
                            VGroup(
                            Group(Item('optimization_constrain_value', show_label=False), label='Optimization constrain value:', springy=True),
                            Group(Item('plate_params_with_ref', editor=TableEditor(columns=[ObjectColumn(name='node_name', label='Name', editable=False),
                                                                       ObjectColumn(name='base_value', label='Default value'),
                                                                       ObjectColumn(name='minimum', label='Minimum'),
                                                                       ObjectColumn(name='maximum', label='Maximum'),
                                                                       ObjectColumn(name='optimization_constrain_multiplier', label='Constrain multiplier'),
                                                                     ],
                                                             row_factory=Parameter,
                                                             show_toolbar=True,
                                                             deletable=True,
                                                             auto_size=False,
                                                             auto_add=True,
                                                            ),
                          show_label=False,
                          ), label='Plate parameters:', springy=True),
                     Group(Item('param_plate_with_ref', editor=TableEditor(columns=[ObjectColumn(name='node_name', label='Name', editable=False),
                                                                       ObjectColumn(name='reinf_layout_name', label='Reinf. layout name'),
                                                                       ObjectColumn(name='trait_name', label='Unknown value name'),
                                                                       ObjectColumn(name='param_no', label='Parameter'),
                                                                       ObjectColumn(name='multiplier', label='Multiplier'),
                                                                       ObjectColumn(name='base_value', label='Default value'),
                                                                     ],
                                                             row_factory=ParamPlate,
                                                             show_toolbar=True,
                                                             deletable=True,
                                                             auto_size=False,
                                                             auto_add=True,
                                                            ),
                          show_label=False,
                          ), label='Plate optimization data:', springy=True),)
                     )
                     )

class PStudyBruteForce(HasTraits):
    '''Obsolete version, kept for test02
    '''

    plate = Instance(Plate)

    parameters = List([])
    '''A list of tuples (min, max, count) containing the range of each parameter.
    Its length is the total number of parameters.
    '''

    param_nodes = List([])
    '''A list of tuples (node, val_code, parameter, param_multiplier, base_value)
    '''

    init_param = Property
    '''Initially undefined parameters.
    '''
    @cached_property
    def _get_init_param(self):
        ids = []
        nds = self.plate.nodes_with_ref
        for i in range(len(nds)):
            for key in ["x", "y", "w"]:
                if getattr(nds[i], key) == None: ids.append((i, key))
        return ids

    def set_init_param(self):
        nds = self.plate.nodes_with_ref
        for tup in self.init_param:
            nds[tup[0]].reset_traits(traits=tup[1])

    def get_param_cycle(self, param_no):
        count = 1
        for i in range(param_no + 1, len(self.parameters)):
            count *= self.parameters[i][2]
        return count

    param_arr = Property(depends_on='parameters,param_nodes,plate')
    @cached_property
    def _get_param_arr(self):
        range_lst = [np.linspace(p[0], p[1], p[2]) for p in self.parameters]
        count = self.parameters[0][2] * self.get_param_cycle(0)
        param_arr = np.zeros((count, len(self.parameters)))
        for i in range(count):
            for j in range(len(self.parameters)):
                param_arr[i, j] = range_lst[j][(i // self.get_param_cycle(j)) % self.parameters[j][2]]
        return param_arr

    work_ratio_arr = Property(depends_on='parameters,param_nodes,plate')
    @cached_property
    def _get_work_ratio_arr(self):
        ip = self.init_param
        nds = self.plate.nodes_with_ref
        wr_arr = []
        for row in self.param_arr:
            for pn in self.param_nodes:
                val = pn[4] + pn[3] * row[pn[2]]
                setattr(nds[pn[0]], pn[1], val)
            wr_arr.append(self.plate.unit_work_ratio)
            self.set_init_param()
        return np.array(wr_arr)

    min_work_ratio = Property(depends_on='parameters,param_nodes,plate')
    @cached_property
    def _get_min_work_ratio(self):
        nds = self.plate.nodes_with_ref
        min_id = np.argmin(self.work_ratio_arr)
        params = self.param_arr[min_id, :]
        for pn in self.param_nodes:
            val = pn[4] + pn[3] * params[pn[2]]
            setattr(nds[pn[0]], pn[1], val)

        self.set_init_param()
        self.plate.solve_dependent_params()
        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.7, 0.7])
        self.plate.plot(ax)
        plt.show()

        return self.work_ratio_arr[min_id]


if __name__ == '__main__':
    ps = ParametricStudy(parameters=[(0, 2., 3), (0, 2., 3), (0, 2., 3)])
    print len(ps.param_arr)
    print ps.param_arr
