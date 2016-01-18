'''
Created on 26. 5. 2015

@author: Kapsak
'''

from ylpa import \
    Meshgen, YLPATreeView, LinearProgramming, \
    Node, PlateSegment, YieldLine, PlateLoadUniform, \
    Plate, PlateLoadNodalForce

from ylpa.meshgen import get_simple_mesh, Testmesh

from ylpa.plasticity import \
    Reinforcement

import matplotlib.pyplot as plt

msh = Testmesh(outline_nodes=[[0., 0.], [4., 0.], [4., 2.], [0., 2.],
                                   ],
              nx=8, ny=4,
                  simple_edges=[1, 3],
                  fixed_edges=[],
                  minimal_distance=0.25,
                  no_of_points=0)
p = msh.plate_object
p.h = 0.2
pu = 0.01
p.reinforcement = [Reinforcement(p1=0.01, p2=0.01,
                                 p1u=pu, p2u=pu,
                                 node_name='reinforcement')]
p.plastic_moment_def_type = "simple"
p.load = [PlateLoadUniform()]  # , PlateLoadNodalForce(x=4., y=2., load_factor_multiplier=1.)

for yl in p.yield_lines_with_ref:
    yl.reinforcement = 'reinforcement'

print 'The plate has %d yield lines' % len(p.yield_lines)
view = YLPATreeView(root=p)
view.configure_traits()

lp = LinearProgramming(plate=p, verbose=False)
print lp.solution
p.plot_3d()
fig = plt.figure()
ax = fig.add_subplot(111)
p.plot_geometry(ax)
plt.show()
