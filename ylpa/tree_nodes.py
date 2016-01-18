'''
Created on 28. 1. 2015

@author: Kapsak
'''

from traits.api import \
    HasTraits, Str, List, WeakRef, \
    Property, cached_property

from traitsui.api import \
    View

class YLPALeafNode(HasTraits):
    '''Base class of all model classes that can appear in a tree view.
    '''
    node_name = Str('<unnamed>')

    def plot(self, fig):
        ax = fig.add_subplot(1, 1, 1)
        self.plateref.plot_geometry(ax)
        return

    def calculate(self, fig):
        print 'Plate load factor: %f' % self.plateref.unit_work_ratio
        self.plot(fig)
        return

    def __getstate__ (self):
        '''Overriding __getstate__ because of WeakRef usage
        '''
        state = super(YLPALeafNode, self).__getstate__()

        for key in [ 'plateref', 'plateref_' ]:
            if state.has_key(key):
                del state[ key ]

        return state

class YLPATreeNode(HasTraits):
    '''Base class of all model classes that can appear in a tree view.
    '''
    node_name = Str('<unnamed>')

    tree_node_list = List([])

    tree_view = View()

    def append_node(self, node):
        '''Add a new subnode to the current node.
        Inform the tree view to select the new node within the view.
        '''
        self.tree_node_list.append(node)

    def plot(self, fig):
        '''Plot the content of the current node.
        '''
        ax = fig.add_subplot(1, 1, 1)
        try:
            self.plot_geometry(ax)
        except AttributeError:
            self.plateref.plot_geometry(ax)
        return

    def calculate(self, fig):
        '''Calculate the limit load factor and plot geometry.
        '''
        ax = fig.add_subplot(1, 1, 1)
        try:
            print 'Plate load factor: %f' % self.unit_work_ratio
            self.plot_geometry(ax)
        except AttributeError:
            print 'Plate load factor: %f' % self.plateref.unit_work_ratio
            self.plateref.plot_geometry(ax)
        return

    def __getstate__ (self):
        '''Overriding __getstate__ because of WeakRef usage
        '''
        state = super(YLPATreeNode, self).__getstate__()

        for key in [ 'plateref', 'plateref_', 'pstudyref', 'pstudyref_' ]:
            if state.has_key(key):
                del state[ key ]

        return state


class PlateNodesTreeNode(YLPATreeNode):
    '''Class accommodating the list of all nodes.
    '''
    node_name = Str('Nodes')

    plateref = WeakRef

    tree_node_list = Property(depends_on='plateref.nodes_with_ref')
    @cached_property
    def _get_tree_node_list(self):
        # self.plate.changed = True
        return self.plateref.nodes_with_ref

class PlateSegmentsTreeNode(YLPATreeNode):
    '''Class accommodating the list of all plate segments.
    '''
    node_name = Str('Plate segments')

    plateref = WeakRef

    tree_node_list = Property(depends_on='plateref.segments_with_ref')
    @cached_property
    def _get_tree_node_list(self):
        # self.plate.changed = True
        return self.plateref.segments_with_ref

class PlateYieldLinesTreeNode(YLPATreeNode):
    '''Class accommodating the list of all yield lines.
    '''
    node_name = Str('Yield lines')

    plateref = WeakRef

    tree_node_list = Property(depends_on='plateref.yield_lines_with_ref')
    @cached_property
    def _get_tree_node_list(self):
        # self.plate.changed = True
        return self.plateref.yield_lines_with_ref

class PlateLoadTreeNode(YLPATreeNode):
    '''Class accommodating the list of all plate loads.
    '''
    node_name = Str('Load')

    plateref = WeakRef

    tree_node_list = Property(depends_on='plateref.loads_with_ref')
    @cached_property
    def _get_tree_node_list(self):
        # self.plate.changed = True
        return self.plateref.loads_with_ref

class PlateReinforcementTreeNode(YLPATreeNode):
    '''Class accommodating the list of all plate reinforcement layouts.
    '''
    node_name = Str('Reinforcement layouts')

    plateref = WeakRef

    tree_node_list = Property(depends_on='plateref.reinforcement')
    @cached_property
    def _get_tree_node_list(self):
        # self.plate.changed = True
        return self.plateref.reinforcement
