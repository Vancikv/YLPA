'''
Created on 13. 11. 2014

@author: Kapsak
'''

import numpy as np
import numpy.linalg as npla
import scipy as sp
import random

from traits.api import \
    HasTraits, Float, Property, List, \
    cached_property, WeakRef, Event, \
    on_trait_change, Instance, Trait, \
    Str, Dict, Any

from utils import *

from traitsui.api import \
    View, Item, HGroup, Group, \
    VGroup

from traitsui.table_column import \
    ObjectColumn

from plate_load import \
    PlateLoad

from plasticity import \
    PMDSimple, PMDOrthoReinfDep, PMDOrthoReinfIndep, \
    PMDOrthoReinfIndepUni, PMDOrthoReinfDepDuctCheck, \
    Reinforcement

from node import \
    Node

from plate_segment import \
    PlateSegment

from tree_nodes import \
    YLPATreeNode, PlateNodesTreeNode, PlateSegmentsTreeNode, \
    PlateLoadTreeNode, PlateReinforcementTreeNode, PlateYieldLinesTreeNode

from yield_line import \
    YieldLine

PLATE_CHANGE = 'node_data_changed,load_data_changed,yield_lines_changed,segment_data_changed,\
    reinf_data_changed,+mat_input,nodes,segments,yield_lines,load'

class Plate(YLPATreeNode):
    def __init__(self, *args, **kwargs):
        super(Plate, self).__init__(*args, **kwargs)
        self.reinf_dict = {}
        for r in self.reinforcement:
            r.plateref = self
            self.reinf_dict[r.node_name] = r
        for yl in self.yield_lines_with_ref:
            yl.add_trait('reinforcement', Trait(self.reinf_dict.keys()[0], self.reinf_dict))

        self.on_trait_change(self.refresh_reinf, 'reinforcement.node_name,reinforcement')
        self.on_trait_change(self.refresh_yield_lines, 'yield_lines[]')

    def __getstate__ (self):
        '''Overriding __getstate__ because of WeakRef usage
        '''
        state = super(Plate, self).__getstate__()
        for key in [ 'pstudyref', 'pstudyref_' ]:
            if state.has_key(key):
                del state[ key ]
        return state

    def __setstate__(self, state):
        super(Plate, self).__setstate__(state)
        self.__init__()

    pstudyref = WeakRef
    nodes = List(Instance(Node), [])
    segments = List(Instance(PlateSegment), [])
    yield_lines = List(Instance(YieldLine), [])
    load = List(Instance(PlateLoad), [])
    reinforcement = List(Instance(Reinforcement), [Reinforcement()])

    node_data_changed = Event
    yield_lines_changed = Event
    segment_data_changed = Event
    load_data_changed = Event
    reinf_data_changed = Event

    @on_trait_change(PLATE_CHANGE)
    def notify_change(self):
        if self.pstudyref: self.pstudyref.plate_changed = True

#     @on_trait_change('plastic_moment_def_type')
#     def notify_yl(self):
#         for yl in self.yield_lines_with_ref:
#             yl.pmd_changed = True
#
#     @on_trait_change('node_data_changed')
#     def notify_input_change(self):
#         for s in self.segments_with_ref: s.node_data_changed = True
#         for l in self.loads_with_ref: l.node_data_changed = True

    def refresh_reinf(self):
        self.reinf_dict = {}
        for r in self.reinforcement:
            r.plateref = self
            self.reinf_dict[r.node_name] = r
        for yl in self.yield_lines_with_ref:
            prechange_val = yl.reinforcement
            yl.add_trait('reinforcement', Trait(self.reinf_dict.keys()[0], self.reinf_dict))
            try:
                yl.reinforcement = prechange_val
            except:
                yl.reinforcement = self.reinf_dict.keys()[0]

    def refresh_yield_lines(self, new):
        for yl in new:
            yl.add_trait('reinforcement', Trait(self.reinf_dict.keys()[0], self.reinf_dict))

    tolerance = Float(1e-10)
    '''Numerical calculations tolerance - lesser value is considered zero.
    '''

    h = Float(0.2, mat_input=True)
    '''Plate thickness'''

    f_y = Float(500000., mat_input=True)
    '''Yield stress of reinforcement'''

    E_s = Float(200000000., mat_input=True)
    eps_su = Float(0.025, mat_input=True)

    f_c = Float(38000., mat_input=True)
    '''Compressive strength of concrete'''

    eps_c1 = Float(0.0022, mat_input=True)
    eps_cu1 = Float(0.0035, mat_input=True)
    E_cm = Float(33000000., mat_input=True)

    parab_k = Property(depends_on='eps_c1,E_cm,f_c')
    @cached_property
    def _get_parab_k(self):
        return 1.05 * self.E_cm * self.eps_c1 / self.f_c

    plastic_moment_def_type = Trait("ortho_reinf_dep", dict(ortho_reinf_indep=PMDOrthoReinfIndep,
                                                       ortho_reinf_dep=PMDOrthoReinfDep,
                                                       ortho_reinf_dep_duct=PMDOrthoReinfDepDuctCheck,
                                                       ortho_reinf_indep_uni=PMDOrthoReinfIndepUni,
                                                       simple=PMDSimple,
                                                       ), mat_input=True)

    loads_with_ref = Property(depends_on='load')
    @cached_property
    def _get_loads_with_ref(self):
        for load in self.load:
            load.plateref = self
        return self.load

    segments_with_ref = Property(depends_on='segments')
    @cached_property
    def _get_segments_with_ref(self):
        for i in range(len(self.segments)):
            self.segments[i].plateref = self
            self.segments[i].node_name = "Segment %d" % (i + 1)
        return self.segments

    nodes_with_ref = Property(depends_on='nodes')
    @cached_property
    def _get_nodes_with_ref(self):
        for i in range(len(self.nodes)):
            self.nodes[i].plateref = self
            self.nodes[i].node_number = i
            self.nodes[i].node_name = "Node %d" % (i + 1)
        return self.nodes

    yield_lines_with_ref = Property(List(Instance(YieldLine)), depends_on='yield_lines')
    @cached_property
    def _get_yield_lines_with_ref(self):
        for i in range(len(self.yield_lines)):
            yl = self.yield_lines[i]
            yl.plateref = self
            yl.node_name = "Yield line %d" % (i + 1)
        return self.yield_lines

    lines = Property()
    '''Plotting aid.
    '''
    def _get_lines(self):
        positive_lns = [(min(yl.node1, yl.node2) - 1, max(yl.node1, yl.node2) - 1) for yl in self.yield_lines_with_ref if yl.type == 'positive']
        negative_lns = [(min(yl.node1, yl.node2) - 1, max(yl.node1, yl.node2) - 1) for yl in self.yield_lines_with_ref if yl.type == 'negative']
        inactive_lns = [(min(yl.node1, yl.node2) - 1, max(yl.node1, yl.node2) - 1) for yl in self.yield_lines_with_ref if yl.type == 'inactive']
        lns = []
        for sg in self.segments_with_ref:
            for ln in sg.lines:
                if (ln not in lns) and (ln not in positive_lns) and (ln not in negative_lns) and (ln not in inactive_lns):
                    lns.append(ln)
        return (lns, positive_lns, negative_lns, inactive_lns)

    def plot_geometry(self, ax):
        lns, positive_lns, negative_lns, inactive_lns = self.lines[0], self.lines[1], self.lines[2], self.lines[3]
        nds = self.nodes_with_ref
        for ln in lns:
            xdata = [nds[i].x for i in ln]
            ydata = [nds[i].y for i in ln]
            if nds[ln[0]].w != 0. or nds[ln[1]].w != 0.:
                ax.plot(xdata, ydata, linestyle='--', color='black', linewidth=3.)
            else:
                ax.plot(xdata, ydata, linestyle='-', color='black', linewidth=3.)
        for ln in positive_lns:
            xdata = [nds[i].x for i in ln]
            ydata = [nds[i].y for i in ln]
            ax.plot(xdata, ydata, linestyle='--', color='blue', linewidth=3.)
        for ln in negative_lns:
            xdata = [nds[i].x for i in ln]
            ydata = [nds[i].y for i in ln]
            ax.plot(xdata, ydata, linestyle='-', color='blue', linewidth=3.)
        for ln in inactive_lns:
            xdata = [nds[i].x for i in ln]
            ydata = [nds[i].y for i in ln]
            ax.plot(xdata, ydata, linestyle='-', color='black', linewidth=1.)
        ax.axis('equal')
        ax.tick_params(axis='both', which='major', labelsize=30)

    def plot_3d(self):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # triangles = [seg.real_node_nos for seg in self.segments_with_ref]
        data = np.array([[nd.x, nd.y, -nd.w] for nd in self.nodes_with_ref])
        ax.plot_trisurf(data[:, 0], data[:, 1], data[:, 2], cmap=cm.jet)
        plt.show()
#        ax.plot_trisurf(x=data[0], y=data[1], z=data[2], triangles=triangles)
        # ax.axis('equal')

    conditioned_nodecoords = Property()
    '''
    Returns the number of dependent node coordinates.
    '''
    def _get_conditioned_nodecoords(self):
        verbose = False
        n_s = len(self.segments_with_ref)
        ''' Number of segments '''
        n_n = len(self.nodes_with_ref)
        ''' Number of nodes '''
        n_e = 0
        ''' Number of equations '''
        for seg in self.segments_with_ref:
            n_e += len(seg.node_nos)
        n_o = 0
        ''' Number of supported nodes '''
        for nd in self.nodes:
            if nd.w == 0.: n_o += 1
        n_x = n_e - 3 * n_s - (n_n - n_o - 1)
        ''' Number of dependent node coordinates '''
        if verbose:
            print 'n_s =', n_s
            print 'n_n =', n_n
            print 'n_e =', n_e
            print 'n_o =', n_o
            print 'n_x =', n_x
        if n_x > 0:
            # print 'To achieve a mechanism with 1 dof, %d node coordinates will be recalculated.' % n_x
            pass
        elif n_x < 0:
            print 'The mechanism has %d degrees of freedom. Consider changing input (e.g. merging some segments).' % (-n_x + 1)
        return n_x

    def solve_mechanism(self, verbose=False):
        # Delete any computed deflections of unsupported nodes:
        for nd in self.nodes_with_ref:
            if nd.w != 0.:
                nd.reset_traits(['w'])

        cnc = self.conditioned_nodecoords
        if verbose: print cnc
        # if cnc < 0: return

        # Go through all segments, if a zero deflection is calculated,
        # add node's segments to the end of the list.
        segment_queue = self.segments_with_ref
        for seg in segment_queue:
            node = seg.solve()
            for id in node:
                self.nodes_with_ref[id].w = 0.
            segment_queue += self.get_segments_from_nodes(node)

        unknown_nodes = []
        nr_of_segments_lst = []

        # Choose a node to prescribe deflection in - the node with the most adjacent segments:
        for i in range(len(self.nodes_with_ref)):
            if self.nodes_with_ref[i].w != 0.:
                nr_of_segments_lst.append(len(self.get_segments_from_nodes([i])))
                unknown_nodes.append(i)
            else:
                nr_of_segments_lst.append(0)

        node_nr = nr_of_segments_lst.index(max(nr_of_segments_lst))
        # Prescribe deflection:
        if verbose: print 'Prescribing deflection in node %d' % (node_nr + 1)
        self.nodes_with_ref[node_nr].w = 1.
        unknown_nodes.remove(node_nr)

        segment_queue = self.get_segments_from_nodes([node_nr])
        for seg in segment_queue:
            node = seg.solve()
            nodesegs = self.get_segments_from_nodes(node)
            knownnsegs = [nseg for nseg in nodesegs if len(nseg.param_vect) == 3]
            if len(knownnsegs) == 0:
                continue
            unknownnsegs = [nseg for nseg in nodesegs if len(nseg.param_vect) == 0]
            param_matrix = np.vstack([knnseg.param_vect for knnseg in knownnsegs])
            xy_columns = param_matrix[:, 1:]
            deflection_column = -1 * np.ones((param_matrix.shape[0], 1))
            rside_column = -1 * param_matrix[:, :1]
            system_matrix = np.hstack([xy_columns, deflection_column, rside_column])
            if verbose:
                print 'matrix to get node %d:' % (node[0] + 1)
                print system_matrix

            if system_matrix.shape[0] == 3:  # 3 rows => both in-plane coordinates are conditioned.
                xyw_vect = npla.solve(system_matrix[:, :3], system_matrix[:, 3])
                self.nodes_with_ref[node[0]].x = xyw_vect[0]
                self.nodes_with_ref[node[0]].y = xyw_vect[1]
                self.nodes_with_ref[node[0]].w = xyw_vect[2]
            elif system_matrix.shape[0] == 2:  # 2 rows => one in-plane coordinate is conditioned (the one whose coefficient is not zero).
                if np.abs(system_matrix[1, 0] - system_matrix[0, 0]) < self.tolerance:
                    mtr = system_matrix[:, 1:3]
                    rside = system_matrix[:, 3] - system_matrix[:, 0] * self.nodes_with_ref[node[0]].x
                    yw_vect = npla.solve(mtr, rside)
                    self.nodes_with_ref[node[0]].y = yw_vect[0]
                    self.nodes_with_ref[node[0]].w = yw_vect[1]
                else:
                    mtr = system_matrix[:, [0, 2]]
                    rside = system_matrix[:, 3] - system_matrix[:, 1] * self.nodes_with_ref[node[0]].y
                    xw_vect = npla.solve(mtr, rside)
                    self.nodes_with_ref[node[0]].x = xw_vect[0]
                    self.nodes_with_ref[node[0]].w = xw_vect[1]

            elif system_matrix.shape[0] == 1:  # 1 row => Both in-plane coordinates are known.
                x = self.nodes_with_ref[node[0]].x
                y = self.nodes_with_ref[node[0]].y
                w = (x * system_matrix[0, 0] + y * system_matrix[0, 1] - system_matrix[0, 3]) / (-system_matrix[0, 2])
            else:  # The shape is > 3. It cannot be 0, because the node is returned by a segment that has just been computed.
                print 'Error: Solution impossible. The node %d is over-conditioned' % node[0]
                return
            unknown_nodes.remove(node[0])
            segment_queue += unknownnsegs

        if len(unknown_nodes) > 0:
            # print 'An inner mechanism has been found with prescribed deflection in node %d, deflections in nodes %s have been set to 0.0.' % (node_nr + 1, ', '.join(map(str, [u + 1 for u in unknown_nodes])))
            for id in unknown_nodes:
                self.nodes_with_ref[id].w = 1.
        if verbose: print 'Mechanism solved'

    def get_segments_from_nodes(self, node_nos):
        seg = []
        if node_nos == []:
            return []
        for s in self.segments_with_ref:
            isin = True
            for n in node_nos:
                if not n in s.real_node_nos:
                    isin = False
                    break
            if isin: seg.append(s)
        return seg

    def get_segment_by_coords(self, x, y):
        segs = self.segments_with_ref
        nds = self.nodes_with_ref
        for i in range(len(segs)):
            node_nos = segs[i].real_node_nos
            inner_nodes = [[x, y]]
            for j in range(-1, len(node_nos) - 1):
                p1, p2 = nds[node_nos[j]], nds[node_nos[j + 1]]
                inner_nodes = cutoff_by_vector([p1.x, p1.y], [p2.x, p2.y], inner_nodes)
            try:
                inner_nodes[0]
                return i
            except:
                pass

    def get_deflection(self, x, y):
        '''This is a temporary solution used for force loads. It will fail
        when the load power should be negative or when there is a non-deflecting
        segment.

        @todo: Instead it should be checked which segment the node lies on and the
        deflection function of this segment should be used directly.
        '''
        deflst = []
        for seg in self.segments_with_ref:
            deflection = seg.get_point_deflection((x, y))
            if deflection >= 0:
                deflst.append(deflection)
        return min(deflst)

    external_power = Property(depends_on='node_data_changed,load_data_changed,segment_data_changed,nodes,segments,load')
    @cached_property
    def _get_external_power(self):
        W_ext = 0.
        for load in self.loads_with_ref:
            W_ext += load.unit_work
        return W_ext

    dissipation_rate = Property(depends_on='node_data_changed,yield_lines_changed,segment_data_changed,\
    +mat_input,reinf_data_changed,nodes,segments,yield_lines')
    @cached_property
    def _get_dissipation_rate(self):
        w_d = 0.
        for ln in self.yield_lines_with_ref:
            node_ids = (ln.node1 - 1, ln.node2 - 1)
            # User nodes start from 1 instead of 0.
            n1, n2 = self.nodes_with_ref[node_ids[0]], self.nodes_with_ref[node_ids[1]]
            segs = self.get_segments_from_nodes(node_nos=node_ids)
            b1, c1 = segs[0].param_vect[1], segs[0].param_vect[2]

            # Find a node not on the yield-line in order to check positive/negative yield-line
            checknode = ()
            nodes1 = segs[0].real_node_nos
            for nd in nodes1:
                if nd not in node_ids:
                    checknode = (self.nodes_with_ref[nd].x, self.nodes_with_ref[nd].y)
                    break
            w1 = segs[0].get_point_deflection(checknode)
            if len(segs) == 1:
                # Only one segment adjacent to the line - boundary segment's counterpart is described by "w=0".
                b2, c2 = 0., 0.
                w2 = 0.
            else:  # Always must be len(segs) == 2.
                b2, c2 = segs[1].param_vect[1], segs[1].param_vect[2]
                w2 = segs[1].get_point_deflection(checknode)
            angle = np.arctan2(n2.y - n1.y, n2.x - n1.x)

            dw = w1 - w2
            if np.abs(dw) < self.tolerance * 100000:
                ln.type = 'inactive'
                continue
            elif dw < 0.:  # Positive yield-line.
                ln.type = 'positive'
                Mp = ln.plastic_moment_def.get_plastic_moment(angle)
            elif dw > 0.:  # Negative yield-line.
                ln.type = 'negative'
                Mp = ln.plastic_moment_def.get_negative_plastic_moment(angle)

            theta = np.sqrt((b1 - b2) ** 2 + (c1 - c2) ** 2)
            w_d += Mp * np.sqrt((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2) * theta
        return w_d

    unit_volume = Property(depends_on='node_data_changed,segment_data_changed,nodes,segments')
    @cached_property
    def _get_unit_volume(self):
        vol = 0.
        for s in self.segments_with_ref:
            vol += s.unit_volume
        return vol

    unit_work_ratio = Property(depends_on=PLATE_CHANGE)
    @cached_property
    def _get_unit_work_ratio(self):
        # if len(self.unsupported_node_nos):
        self.solve_mechanism()
        return self.dissipation_rate / self.external_power

    ductility_check_lst = Property
    def _get_ductility_check_lst(self):
        for ln in self.yield_lines_with_ref:
            node_ids = (ln.node1 - 1, ln.node2 - 1)
            # User nodes start from 1 instead of 0.
            n1, n2 = self.nodes_with_ref[node_ids[0]], self.nodes_with_ref[node_ids[1]]
            segs = self.get_segments_from_nodes(node_nos=node_ids)
            b1, c1 = segs[0].param_vect[1], segs[0].param_vect[2]
            checknode = ()
            nodes1 = segs[0].real_node_nos
            for nd in nodes1:
                if nd not in node_ids:
                    checknode = (self.nodes_with_ref[nd].x, self.nodes_with_ref[nd].y)
                    break
            w1 = segs[0].get_point_deflection(checknode)
            if len(segs) == 1:
                # Only one segment adjacent to the line - boundary segment's counterpart is described by "w=0".
                b2, c2 = 0., 0.
                w2 = 0.
            else:  # Always must be len(segs) == 2.
                b2, c2 = segs[1].param_vect[1], segs[1].param_vect[2]
                w2 = segs[1].get_point_deflection(checknode)
            angle = np.arctan2(n2.y - n1.y, n2.x - n1.x)

            if w1 < w2:  # Positive yield-line.
                ln.mom_crv_info = self.plastic_moment_def.get_mom_crv(angle)
            else:  # Negative yield-line.
                ln.mom_crv_info = self.plastic_moment_def.get_negative_mom_crv(angle)
            theta = np.sqrt((b1 - b2) ** 2 + (c1 - c2) ** 2)
            ln.theta = theta
        return ([ln.theta for ln in self.yield_lines_with_ref], [ln.mom_crv_info for ln in self.yield_lines_with_ref])

    def check_ductility(self):
        dcl = self.ductility_check_lst
        rot = np.array(dcl[0])
        rot_matrix = np.array([rot * (1 / i) for i in rot])
        crv_y = np.array([tp[1] for tp in dcl[1]])
        crv_u = np.array([tp[3] for tp in dcl[1]])
        prod = np.transpose(np.transpose(rot_matrix) * crv_u)
        for row in prod:
            valid = True
            for i in range(row.shape[0]):
                if row[i] < crv_y[i] or row[i] > crv_u[i]:
                    valid = False
            if valid:
                print 'Yield curvatures:'
                print crv_y
                print 'Ultimate curvatures:'
                print crv_u
                print 'Unit rotations:'
                print rot_matrix
                print 'Control product:'
                print prod
                return True
        print 'Insufficient ductility! Mechanism cannot occur!'
        print 'Yield curvatures:'
        print crv_y
        print 'Ultimate curvatures:'
        print crv_u
        print 'Unit rotations:'
        print rot_matrix
        print 'Control product:'
        print prod
        return False

    unsupported_node_nos = Property()
    '''Numbers of unsupported nodes, real values (not user values)
    '''
    def _get_unsupported_node_nos(self):
        lst = []
        for i in range(len(self.nodes_with_ref)):
            if self.nodes_with_ref[i].w == None:
                lst.append(i)
        return lst

    linprog_vect_c = Property()
    def _get_linprog_vect_c(self):
        vect = np.zeros(2 * len(self.yield_lines_with_ref))
        for i in range(len(self.yield_lines_with_ref)):
            vect[i] = self.yield_lines_with_ref[i].plastic_moment_def.get_plastic_moment(self.yield_lines_with_ref[i].angle)
            vect[len(self.yield_lines_with_ref) + i] = self.yield_lines_with_ref[i].plastic_moment_def.get_negative_plastic_moment(self.yield_lines_with_ref[i].angle)
        return vect

    linprog_vect_k = Property()
    def _get_linprog_vect_k(self):
        vect = np.zeros(len(self.unsupported_node_nos))
        for l in self.loads_with_ref:
            vect += l.load_vector
        return vect

    linprog_matrix_B = Property()
    def _get_linprog_matrix_B(self):
        ylwr = self.yield_lines_with_ref
        unn = self.unsupported_node_nos
        B = np.zeros([len(ylwr), len(unn)])
        for i in range(len(self.yield_lines_with_ref)):
            yl_nodes = [ylwr[i].node1 - 1, ylwr[i].node2 - 1]
            segments = self.get_segments_from_nodes(node_nos=[yl_nodes[0], yl_nodes[1]])
            tri_nodes = []
            for s in segments:
                for n in s.real_node_nos:
                    if n not in yl_nodes:
                        tri_nodes.append(n)
            node_nos = yl_nodes + tri_nodes
            nds = [self.nodes_with_ref[j] for j in node_nos]

            cfs = np.zeros(len(nds))
            # counterclokwise check
            v1 = np.array([nds[2].x - nds[0].x, nds[2].y - nds[0].y])
            v2 = np.array([nds[2].x - nds[1].x, nds[2].y - nds[1].y])
            vA = np.cross(v1, v2) / 2.

            if vA < 0:
                tmp = node_nos[0]
                node_nos[0] = node_nos[1]
                node_nos[1] = tmp
                nds = [self.nodes_with_ref[j] for j in node_nos]

            x1, x2, x3 = nds[2].x, nds[0].x, nds[1].x
            y1, y2, y3 = nds[2].y, nds[0].y, nds[1].y

            j_cA = (x3 - x1) * (y2 - y1) - (x2 - x1) * (y3 - y1)
            if j_cA == 0:
                print 'Error: j_cA = 0.'
                return

            cfs[2] += ((y3 - y2) ** 2 + (x3 - x2) ** 2) / j_cA
            cfs[0] += ((y3 - y2) * (y1 - y3) - (x3 - x2) * (x3 - x1)) / j_cA
            cfs[1] += ((y3 - y2) * (y2 - y1) - (x3 - x2) * (x1 - x2)) / j_cA

            if len(nds) == 4:
                x1, x2, x3 = nds[3].x, nds[1].x, nds[0].x
                y1, y2, y3 = nds[3].y, nds[1].y, nds[0].y
                j_cB = (x3 - x1) * (y2 - y1) - (x2 - x1) * (y3 - y1)
                if j_cB == 0:
                    print 'Error: j_cB = 0.'
                    return
                cfs[3] += ((y3 - y2) ** 2 + (x3 - x2) ** 2) / j_cB
                cfs[1] += ((y3 - y2) * (y1 - y3) - (x3 - x2) * (x3 - x1)) / j_cB
                cfs[0] += ((y3 - y2) * (y2 - y1) - (x3 - x2) * (x1 - x2)) / j_cB

            for j in range(len(nds)):
                if nds[j].w != 0:
                    col = unn.index(node_nos[j])
                    B[i, col] += cfs[j]
        return B

    linprog_static_matrix = Property()
    def _get_linprog_static_matrix(self):
        ylwr = self.yield_lines_with_ref
        unn = self.unsupported_node_nos
        B = np.zeros([len(unn), len(ylwr)])
        for i in range(len(self.yield_lines_with_ref)):
            yl_nodes = [ylwr[i].node1 - 1, ylwr[i].node2 - 1]
            segments = self.get_segments_from_nodes(node_nos=[yl_nodes[0], yl_nodes[1]])
            tri_nodes = []
            for s in segments:
                for n in s.real_node_nos:
                    if n not in yl_nodes:
                        tri_nodes.append(n)

            node_nos = yl_nodes + tri_nodes
            nds = [self.nodes_with_ref[j] for j in node_nos]

            cfs = np.zeros(len(nds))

            # counterclokwise check
            v1 = np.array([nds[2].x - nds[0].x, nds[2].y - nds[0].y])
            v2 = np.array([nds[2].x - nds[1].x, nds[2].y - nds[1].y])
            vA = np.cross(v1, v2) / 2.

            if vA < 0:
                tmp = node_nos[0]
                node_nos[0] = node_nos[1]
                node_nos[1] = tmp
                nds = [self.nodes_with_ref[j] for j in node_nos]

            x1, x2, x3 = nds[2].x, nds[0].x, nds[1].x
            y1, y2, y3 = nds[2].y, nds[0].y, nds[1].y

            l1 = np.sqrt((x2 - x3) ** 2 + (y2 - y3) ** 2)
            l2 = np.sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2)
            l3 = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            a1 = (l1 ** 2 - l2 ** 2 + l3 ** 2) / (2 * l1)
            a2 = (l2 ** 2 - l3 ** 2 + l1 ** 2) / (2 * l2)
            h1 = ((y1 - y2) * (x3 - x2) - (x1 - x2) * (y3 - y2)) / l1
            h2 = ((y2 - y3) * (x1 - x3) - (x2 - x3) * (y1 - y3)) / l2

            cfs[2] += -(a1 / h1 + a2 / h2)
            cfs[0] += a2 / h2
            cfs[1] += a1 / h1

            if len(nds) == 4:
                x1, x2, x3 = nds[3].x, nds[1].x, nds[0].x
                y1, y2, y3 = nds[3].y, nds[1].y, nds[0].y

                l1 = np.sqrt((x2 - x3) ** 2 + (y2 - y3) ** 2)
                l2 = np.sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2)
                l3 = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                a1 = (l1 ** 2 - l2 ** 2 + l3 ** 2) / (2 * l1)
                a2 = (l2 ** 2 - l3 ** 2 + l1 ** 2) / (2 * l2)
                h1 = ((y1 - y2) * (x3 - x2) - (x1 - x2) * (y3 - y2)) / l1
                h2 = ((y2 - y3) * (x1 - x3) - (x2 - x3) * (y1 - y3)) / l2
                cfs[3] += -(a1 / h1 + a2 / h2)
                cfs[1] += a2 / h2
                cfs[0] += a1 / h1

            # print cfs
            for j in range(len(nds)):
                if nds[j].w != 0.:
                    row = unn.index(node_nos[j])
                    B[row, i] += cfs[j]
        return B

    def move_nodes(self, d_pos):
        for node in self.nodes_with_ref:
            node.x += (random.random() - 0.5) * 2 * d_pos
            node.y += (random.random() - 0.5) * 2 * d_pos

    node_name = Str('Plate')

    tree_node_list = Property
    @cached_property
    def _get_tree_node_list(self):
        return [PlateReinforcementTreeNode(plateref=self), PlateLoadTreeNode(plateref=self),
                PlateYieldLinesTreeNode(plateref=self), PlateNodesTreeNode(plateref=self),
                PlateSegmentsTreeNode(plateref=self),
                ]

    tree_view = View(VGroup(
                         HGroup(Group(Item('h'),
                                      Item('f_y'),
                                      Item('f_c'),
                                      Item('plastic_moment_def_type'),
                                      springy=True,
                                      label='Material parameters'
                                      ),
                                ),
                     )
                     )
