'''
Created on 13. 11. 2014

@author: Kapsak
'''

from traits.api import \
    HasTraits, Float, Property, List, \
    cached_property, WeakRef, Event, \
    on_trait_change, Int

from traitsui.api import \
    View, VGroup, Item

from tree_nodes import \
    YLPALeafNode

class Node(YLPALeafNode):
    x = Float(None, geo_input=True)
    y = Float(None, geo_input=True)
    '''Position
    '''
    w = Float(None, geo_input=True)
    '''Deflection
    '''
    plateref = WeakRef
    node_number = Int()

    def __getstate__(self):
        state = super(Node, self).__getstate__()

        for key in state.keys():
            if state[key] == None:
                del state[key]
        return state

    linprog_k = Property()
    def _get_linprog_k(self):
        my_segments = self.plateref.get_segments_from_nodes(node_nos=[self.node_number])
        k = 0.
        for seg in my_segments:
            k += seg.area / 3
        return k

    @on_trait_change('+geo_input')
    def notify_input_change(self):
        if self.plateref: self.plateref.node_data_changed = True

    def plot(self, fig):
        ax = fig.add_subplot(111)
        if self.plateref:
            self.plateref.plot_geometry(ax)
            for node in self.plateref.nodes_with_ref:
                ax.plot(node.x, node.y, marker='o', color='blue', markersize=7.)
            ax.plot(self.x, self.y, marker='o', color='red', markersize=7.)

    tree_view = View(VGroup(Item('x'),
                            Item('y'),
                            Item('w'),
                            ))
