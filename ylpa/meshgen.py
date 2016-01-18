'''
Created on 26. 5. 2015

@author: Kapsak
'''

import numpy as np
import scipy as sp
from scipy.linalg import lu
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from utils import *

from traits.api import \
    HasStrictTraits, Float, Property, List, \
    cached_property, WeakRef, Event, \
    on_trait_change, Instance, Trait, \
    Str, Dict, Any, Int

from traitsui.api import \
    View, Item, HGroup, Group, \
    VGroup

from node import \
    Node

from plate_segment import \
    PlateSegment

from plate import \
    Plate

from yield_line import \
    YieldLine

from plate_load import \
    PlateLoadUniform

def get_simple_mesh(xlength, ylength, xcells, ycells):
    xcell = xlength / xcells
    ycell = ylength / ycells

    # generate coordinate arrays
    x_arr = np.hstack(ycells * [np.linspace(0., xlength, xcells + 1), np.linspace(xcell / 2., xlength - xcell / 2, xcells)] + [np.linspace(0., xlength, xcells + 1)])
    y_arr = np.hstack([np.zeros(xcells + 1), ycell * 0.5 * np.ones(xcells)]) + np.array([[i] for i in np.linspace(0., ylength, ycells + 1)]) * np.ones(2 * xcells + 1)
    y_arr = np.reshape(y_arr, y_arr.shape[0] * y_arr.shape[1])[:-xcells]

    nodes = [Node(x=x_arr[i], y=y_arr[i]) for i in range(len(x_arr))]
    for i in range(len(x_arr)):
        if i < xcells + 1 or i > len(x_arr) - xcells - 2 or i % (2 * xcells + 1) == 0 or (i - xcells) % (2 * xcells + 1) == 0:
            nodes[i].w = 0

    segments = []
    yield_lines = []
    for i in range(xcells * ycells):
        corner = i + (i // xcells) * (xcells + 1) + 1
        segments.append(PlateSegment(node_nos=[corner, corner + 1, corner + xcells + 1]))
        segments.append(PlateSegment(node_nos=[corner + 1, corner + 2 * xcells + 2, corner + xcells + 1]))
        segments.append(PlateSegment(node_nos=[corner + 2 * xcells + 2, corner + 2 * xcells + 1, corner + xcells + 1]))
        segments.append(PlateSegment(node_nos=[corner + 2 * xcells + 1, corner, corner + xcells + 1]))
        yield_lines.append(YieldLine(corner, corner + xcells + 1))
        yield_lines.append(YieldLine(corner + 1, corner + xcells + 1))
        yield_lines.append(YieldLine(corner + 2 * xcells + 2, corner + xcells + 1))
        yield_lines.append(YieldLine(corner + 2 * xcells + 1, corner + xcells + 1))

    yl_ranges = [range(i, i + ycells * (2 * xcells + 1) + 1, 2 * xcells + 1) for i in range(1, xcells)] + [range(j, j + xcells + 1) for j in range(2 * xcells + 1, (2 * xcells + 1) * ycells, 2 * xcells + 1)]
    for rng in yl_ranges:
        for i in range(len(rng) - 1):
            yield_lines.append(YieldLine(rng[i] + 1, rng[i + 1] + 1))
    # plate_yield_lines = [YieldLine(yl[0], yl[1]) for yl in yield_lines]

    plate = Plate(nodes=nodes,
                segments=segments,
                yield_lines=yield_lines,
                plastic_moment_def_type='simple',
                load=[PlateLoadUniform()]
                      )
    return plate

class Meshgen(HasStrictTraits):
    outline_nodes = List([])
    additional_input_nodes = List([])

    fixed_edges = List([])
    '''Defined as numbers of the first outline_node - the second
    one must be the next one as the boundary must be continuous.
    Deflections are zero and yield lines are generated.
    '''
    simple_edges = List([])
    '''Defined as numbers of the first outline_node - the second
    one must be the next one as the boundary must be continuous.
    Deflections are zero and yield lines are not generated.
    '''
    supported_outline_nodes = List([])
    supported_additional_nodes = List([])

    minimal_distance = Float()
    no_of_points = Int()

    plate_object = Property(depends_on='minimal_distance,no_of_points,fixed_edges,simple_edges,supported_outline_nodes,supported_additional_nodes')
    @cached_property
    def _get_plate_object(self):
        nd = self.nodedata
        md = self.meshdata
        nodes = [Node(x=pt[0], y=pt[1]) for pt in md.points]

        for i in self.supported_outline_nodes:
            nodes[i].w = 0.

        boundary_nodes_length = nd[1][-1][-2] + 1
        for i in self.supported_additional_nodes:
            nodes[boundary_nodes_length + i].w = 0.

        for i in self.fixed_edges:
            for j in nd[1][i]:
                nodes[j].w = 0.
        for i in self.simple_edges:
            for j in nd[1][i]:
                nodes[j].w = 0.

        sims = md.simplices
        segments = [PlateSegment(node_nos=[sim[0] + 1, sim[1] + 1, sim[2] + 1]) for sim in sims]

        yield_lines = []
        for sim in sims:
            n1 = sim[0] + 1
            n2 = sim[1] + 1
            n3 = sim[2] + 1
            yl1 = [min(n1, n2), max(n1, n2)]
            yl2 = [min(n1, n3), max(n1, n3)]
            yl3 = [min(n3, n2), max(n3, n2)]
            if yl1 not in yield_lines:
                yield_lines.append(yl1)
            if yl2 not in yield_lines:
                yield_lines.append(yl2)
            if yl3 not in yield_lines:
                yield_lines.append(yl3)

        # Now remove the yield lines from simple and free edges
        no_yl_edges = range(len(self.outline_nodes))
        for i in self.fixed_edges:
            no_yl_edges.remove(i)
        anti_yls = []
        for i in no_yl_edges:
            for j in range(len(nd[1][i]) - 1):
                n1 = nd[1][i][j] + 1
                n2 = nd[1][i][j + 1] + 1
                yl = [min(n1, n2), max(n1, n2)]
                anti_yls.append(yl)

        for yl in anti_yls:
            if yl in yield_lines:
                yield_lines.remove(yl)

        plate_yield_lines = [YieldLine(yl[0], yl[1]) for yl in yield_lines]

        plate = Plate(nodes=nodes,
                      segments=segments,
                      yield_lines=plate_yield_lines,
                      plastic_moment_def_type='simple',
                      load=[PlateLoadUniform()]
                      )
        return plate


    meshdata = Property(depends_on='minimal_distance,no_of_points')
    @cached_property
    def _get_meshdata(self):
        nd = self.nodedata[0]
        points = np.array(nd[0])
        for data in nd[1:]:
            if len(data) > 0:
                points = np.vstack([points, data])
        return Delaunay(points)

    nodedata = Property(depends_on='minimal_distance,no_of_points')  # ,outline_nodes[],additional_input_nodes[]
    @cached_property
    def _get_nodedata(self):
        # Generate boundary nodes
        boundary_nodes = np.array(self.outline_nodes)
        additional_nodes = np.array(self.additional_input_nodes)
        xmin, xmax = min(boundary_nodes[:, 0]), max(boundary_nodes[:, 0])
        ymin, ymax = min(boundary_nodes[:, 1]), max(boundary_nodes[:, 1])
        boundary_codes = []
        for i in range(len(self.outline_nodes)):
            boundary_codes.append([i])
            j = i + 1
            if j == len(self.outline_nodes): j = 0

            p1, p2 = self.outline_nodes[i], self.outline_nodes[j]
            edge_length = get_point_distance(p1=p1, p2=p2)
            no_of_nodes = int(edge_length / self.minimal_distance)
            inner_point_params = np.linspace(start=1. / no_of_nodes, stop=1., num=no_of_nodes - 1, endpoint=False)

            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            inner_points = np.array([[p1[0] + dx * par, p1[1] + dy * par] for par in inner_point_params])
            boundary_codes[-1] += range(len(boundary_nodes), len(boundary_nodes) + len(inner_points)) + [j]
            boundary_nodes = np.vstack([boundary_nodes, inner_points])

        # Generate random nodes
        rnd_points = np.random.rand(self.no_of_points, 2)
        inner_nodes = np.transpose(np.vstack([rnd_points[:, 0] * (xmax - xmin) + xmin,
                                rnd_points[:, 1] * (ymax - ymin) + ymin
                                ]))

        # Cut off nodes outside the boundary
        for i in range(-1, len(self.outline_nodes) - 1):
            p1, p2 = self.outline_nodes[i], self.outline_nodes[i + 1]
            inner_nodes = cutoff_by_vector(p1, p2, inner_nodes)

        # Remove nodes close to the boundary and additional input nodes
        if len(additional_nodes) > 0:
            nodes = np.vstack([boundary_nodes, additional_nodes])
        else:
            nodes = boundary_nodes
        for node in nodes:
            new_inner_node_ids = []
            for i in range(len(inner_nodes)):
                if get_point_distance(node, inner_nodes[i]) > self.minimal_distance:
                    new_inner_node_ids.append(i)
            inner_nodes = inner_nodes[new_inner_node_ids, :]

        checked_ids = []
        # Space the inner nodes evenly
        for i in range(len(inner_nodes)):
            if i >= len(inner_nodes):
                break
            checked_ids.append(i)
            new_ids = []
            for j in range(i + 1, len(inner_nodes)):
                if get_point_distance(inner_nodes[i], inner_nodes[j]) > self.minimal_distance:
                    new_ids.append(j)
            inner_nodes = inner_nodes[checked_ids + new_ids, :]

        return ([boundary_nodes, additional_nodes, inner_nodes], boundary_codes)

class Testmesh(Meshgen):
    nx = Int(8)
    ny = Int(4)
    additional_input_nodes = Property(List)
    def _get_additional_input_nodes(self):
        L = self.outline_nodes[1][0] - self.outline_nodes[0][0]
        H = self.outline_nodes[2][1] - self.outline_nodes[1][1]
        dx = L / self.nx
        dy = H / self.ny
        ain = []
        for i in range(1, self.ny):
            if i % 2:
                for j in range(self.nx):
                    ain.append([dx / 2 + j * dx, i * dy])
            else:
                for j in range(self.nx - 1):
                    ain.append([dx + j * dx, i * dy])
        return ain

    nodedata = Property(depends_on='minimal_distance,no_of_points')  # ,outline_nodes[],additional_input_nodes[]
    @cached_property
    def _get_nodedata(self):
        # Generate boundary nodes
        boundary_nodes = np.array(self.outline_nodes)
        additional_nodes = np.array(self.additional_input_nodes)
        xmin, xmax = min(boundary_nodes[:, 0]), max(boundary_nodes[:, 0])
        ymin, ymax = min(boundary_nodes[:, 1]), max(boundary_nodes[:, 1])
        boundary_codes = []
        for i in range(len(self.outline_nodes)):
            boundary_codes.append([i])
            j = i + 1
            if j == len(self.outline_nodes): j = 0

            p1, p2 = self.outline_nodes[i], self.outline_nodes[j]
            edge_length = get_point_distance(p1=p1, p2=p2)
            if i == 0 or i == 2:
                no_of_nodes = self.nx
            else:
                no_of_nodes = self.ny

            inner_point_params = np.linspace(start=1. / no_of_nodes, stop=1., num=no_of_nodes - 1, endpoint=False)

            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            inner_points = np.array([[p1[0] + dx * par, p1[1] + dy * par] for par in inner_point_params])
            boundary_codes[-1] += range(len(boundary_nodes), len(boundary_nodes) + len(inner_points)) + [j]
            boundary_nodes = np.vstack([boundary_nodes, inner_points])

        # Generate random nodes
        rnd_points = np.random.rand(self.no_of_points, 2)
        inner_nodes = np.transpose(np.vstack([rnd_points[:, 0] * (xmax - xmin) + xmin,
                                rnd_points[:, 1] * (ymax - ymin) + ymin
                                ]))

        # Cut off nodes outside the boundary
        for i in range(-1, len(self.outline_nodes) - 1):
            p1, p2 = self.outline_nodes[i], self.outline_nodes[i + 1]
            inner_nodes = cutoff_by_vector(p1, p2, inner_nodes)

        # Remove nodes close to the boundary and additional input nodes
        if len(additional_nodes) > 0:
            nodes = np.vstack([boundary_nodes, additional_nodes])
        else:
            nodes = boundary_nodes
        for node in nodes:
            new_inner_node_ids = []
            for i in range(len(inner_nodes)):
                if get_point_distance(node, inner_nodes[i]) > self.minimal_distance:
                    new_inner_node_ids.append(i)
            inner_nodes = inner_nodes[new_inner_node_ids, :]

        checked_ids = []
        # Space the inner nodes evenly
        for i in range(len(inner_nodes)):
            if i >= len(inner_nodes):
                break
            checked_ids.append(i)
            new_ids = []
            for j in range(i + 1, len(inner_nodes)):
                if get_point_distance(inner_nodes[i], inner_nodes[j]) > self.minimal_distance:
                    new_ids.append(j)
            inner_nodes = inner_nodes[checked_ids + new_ids, :]

        return ([boundary_nodes, additional_nodes, inner_nodes], boundary_codes)

if __name__ == '__main__':
#     msh = Meshgen(outline_nodes=[[0., 0.], [4., 0.], [4., 3.], [0., 3.],
#                                    ],
#                   simple_edges=[0, 1, 2, 3],
#                   # additional_input_nodes=[[2, 1.5], [2, 1.6]],
#                   minimal_distance=0.5,
#                   no_of_points=1000)
#
#     nd = msh.nodedata
#     tri = msh.meshdata
#     points = tri.points
#     plt.triplot(points[:, 0], points[:, 1], tri.simplices.copy())
#     plt.plot(points[:36, 0], points[:36, 1], 'o')
#
#     plt.show()
#     p = msh.plate_object
#     print p.unit_work_ratio
    p = get_simple_mesh(4., 4., 2, 2)
    print p.unit_work_ratio

