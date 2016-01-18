'''
Created on 13. 11. 2014

@author: Kapsak
'''

import numpy as np
from traits.api import \
    HasTraits, Float, Property, List, \
    cached_property, WeakRef, Event, \
    on_trait_change, Int

from traitsui.api import \
    View, Group, Item

from tree_nodes import \
    YLPALeafNode

class PlateSegment(YLPALeafNode):
    node_nos = List(Int, [])
    '''Minimum of 3 nodes that will define the segment
    '''
    real_node_nos = Property(depends_on='node_nos')
    @cached_property
    def _get_real_node_nos(self):
        return [no - 1 for no in self.node_nos]

    plateref = WeakRef
    node_data_changed = Event

    @on_trait_change('node_nos[]')
    def notify_change(self):
        if self.plateref: self.plateref.segment_data_changed = True

    def plot_geometry(self, ax):
        # print 'Plate work ratio: %f' % self.plateref.unit_work_ratio
        lns, positive_lns, negative_lns = self.plateref.lines[0], self.plateref.lines[1], self.plateref.lines[2]
        nds = self.plateref.nodes_with_ref
        mylines = self.lines
        for ln in lns:
            xdata = [nds[i].x for i in ln]
            ydata = [nds[i].y for i in ln]
            if ln in mylines:
                ax.plot(xdata, ydata, linestyle='-', color='red', linewidth=2.)
            else:
                ax.plot(xdata, ydata, linestyle='-', color='blue', linewidth=2.)
        for ln in positive_lns:
            xdata = [nds[i].x for i in ln]
            ydata = [nds[i].y for i in ln]
            if ln in mylines:
                ax.plot(xdata, ydata, linestyle=':', color='red', linewidth=2.)
            else:
                ax.plot(xdata, ydata, linestyle=':', color='blue', linewidth=2.)
        for ln in negative_lns:
            xdata = [nds[i].x for i in ln]
            ydata = [nds[i].y for i in ln]
            if ln in mylines:
                ax.plot(xdata, ydata, linestyle='--', color='red', linewidth=2.)
            else:
                ax.plot(xdata, ydata, linestyle='--', color='blue', linewidth=2.)
        ax.axis('equal')

    def solve(self):
        # If the parameters can be calculated, next node is passed
        if len(self.param_vect) == 3:
            return self.unknown_node
        return []

    known_nodes = Property(depends_on='node_data_changed,node_nos[]')
    # @cached_property
    def _get_known_nodes(self):
        knds = []
        for i in self.real_node_nos:
            if self.plateref and self.plateref.nodes_with_ref[i].w != None:
                knds.append(i)
        return knds

    unknown_node = Property
    def _get_unknown_node(self):
        for i in self.real_node_nos:
            if self.plateref.nodes_with_ref[i].w == None:
                return [i]
        return []

    param_vect = Property(depends_on='known_nodes')
    # @cached_property
    def _get_param_vect(self):
        knd = self.known_nodes
        if len(knd) > 2:
            matrix = np.ones((3, 3))
            rside = np.ones(3)
            for i in range(3):
                matrix[i, 1] = self.plateref.nodes_with_ref[knd[i]].x
                matrix[i, 2] = self.plateref.nodes_with_ref[knd[i]].y
                rside[i] = self.plateref.nodes_with_ref[knd[i]].w
            sol = np.linalg.solve(matrix, rside)
            return np.transpose(sol)
        return []

    def get_point_deflection(self, point):
        if self.param_vect is not None:
            a, b, c = self.param_vect[0], self.param_vect[1], self.param_vect[2]
            return a + b * point[0] + c * point[1]
        return None

    unit_volume = Property(depends_on='node_data_changed,node_nos[]')
    # @cached_property
    def _get_unit_volume(self):
        no_of_triangles = len(self.real_node_nos) - 2
        vol = 0.
        for i in range(no_of_triangles):
            n1 = self.plateref.nodes_with_ref[self.real_node_nos[0]]
            n2 = self.plateref.nodes_with_ref[self.real_node_nos[i + 1]]
            n3 = self.plateref.nodes_with_ref[self.real_node_nos[i + 2]]

            xt, yt = (n1.x + n2.x + n3.x) / 3., (n1.y + n2.y + n3.y) / 3.
            # coords of the centre of gravity
            wt = self.get_point_deflection((xt, yt))

            v1 = np.array([n2.x - n1.x, n2.y - n1.y])
            v2 = np.array([n3.x - n1.x, n3.y - n1.y])
            A = np.abs(np.cross(v1, v2)) / 2.
            vol += A * wt
        return vol

    area = Property(depends_on='node_data_changed,node_nos[]')
    # @cached_property
    def _get_area(self):
        no_of_triangles = len(self.real_node_nos) - 2
        A = 0.
        for i in range(no_of_triangles):
            n1 = self.plateref.nodes_with_ref[self.real_node_nos[0]]
            n2 = self.plateref.nodes_with_ref[self.real_node_nos[i + 1]]
            n3 = self.plateref.nodes_with_ref[self.real_node_nos[i + 2]]

            v1 = np.array([n2.x - n1.x, n2.y - n1.y])
            v2 = np.array([n3.x - n1.x, n3.y - n1.y])
            A += np.abs(np.cross(v1, v2)) / 2.
        return A

    lines = Property()
    '''Plotting aid
    '''
    def _get_lines(self):
        lns = []
        for i in range(len(self.real_node_nos)):
            node1 = min(self.real_node_nos[i - 1], self.real_node_nos[i])
            node2 = max(self.real_node_nos[i - 1], self.real_node_nos[i])
            lns.append((node1, node2))
        return lns

    def plot(self, fig):
        ax = fig.add_subplot(111)
        self.plot_geometry(ax)


    tree_view = View(Group(Item('node_nos')))

if __name__ == '__main__':
    seg = PlateSegment(node_nos=[0, 3, 4, 5])
    print seg.node_nos
    print seg.real_node_nos
    seg.node_nos[1] = 11
    print seg.node_nos
    print seg.real_node_nos
