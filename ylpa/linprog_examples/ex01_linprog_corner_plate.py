'''
Created on 26. 5. 2015

@author: Kapsak
'''

from ylpa import \
    Meshgen, YLPATreeView, LinearProgramming, \
    Node, PlateSegment, YieldLine, PlateLoadUniform, \
    Plate, PlateLoadNodalForce

from ylpa.meshgen import get_simple_mesh

from ylpa.plasticity import \
    Reinforcement

import matplotlib.pyplot as plt

msh = Meshgen(outline_nodes=[[0., 0.], [6., 0.], [6., 4.], [0., 4.],
                                   ],
              supported_outline_nodes=[],
                  simple_edges=[0, 1],
                  fixed_edges=[],
                  minimal_distance=0.5,
                  no_of_points=10000)
p = msh.plate_object
p.h = 0.2
pu = 0.01
p.reinforcement = [Reinforcement(p1=0.01, p2=0.01,
                                 p1u=pu, p2u=pu,
                                 node_name='reinforcement')]
p.plastic_moment_def_type = "ortho_reinf_dep"
p.load = [PlateLoadUniform()]  # , PlateLoadNodalForce(x=4., y=2., load_factor_multiplier=1.)

for yl in p.yield_lines_with_ref:
    yl.reinforcement = 'reinforcement'

unn = p.unsupported_node_nos
# p = get_simple_mesh(4., 4., 8, 8)
print 'The plate has %d yield lines' % len(p.yield_lines)
view = YLPATreeView(root=p)

lp = LinearProgramming(plate=p, verbose=False)
print lp.solution
p.plot_3d()
fig = plt.figure()
ax = fig.add_subplot(111)
p.plot_geometry(ax)
plt.show()

# pu = 0.005
# p.reinforcement[0].p1u = pu
# p.reinforcement[0].p2u = pu
# print lp.solution
# p.plot_3d()
# fig = plt.figure()
# ax = fig.add_subplot(111)
# p.plot_geometry(ax)
# plt.show()
#
# pu = 0.002
# p.reinforcement[0].p1u = pu
# p.reinforcement[0].p2u = pu
# print lp.solution
# p.plot_3d()
# fig = plt.figure()
# ax = fig.add_subplot(111)
# p.plot_geometry(ax)
# plt.show()
