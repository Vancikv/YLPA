'''
Created on 2. 6. 2015

@author: Kapsak
'''

from ylpa import \
    Meshgen, YLPATreeView, LinearProgramming, \
    Node, PlateSegment, YieldLine, PlateLoadUniform, \
    Plate

from ylpa.meshgen import get_simple_mesh

from ylpa.plasticity import \
    Reinforcement

msh = Meshgen(outline_nodes=[[0., 0.], [4., 0.], [2., 3.],
                                   ],
                  simple_edges=[0, 1],
                  fixed_edges=[],
#                   additional_input_nodes=[
#                                         [1., 1.], [2., 1.], [3., 1.],
#                                         [1., 2.], [2., 2.], [3., 2.],
#                                         [1., 3.], [2., 3.], [3., 3.],
#                                         [0.5, 0.5], [1.5, 0.5], [2.5, 0.5], [3.5, 0.5],
#                                         [0.5, 1.5], [1.5, 1.5], [2.5, 1.5], [3.5, 1.5],
#                                         [0.5, 2.5], [1.5, 2.5], [2.5, 2.5], [3.5, 2.5],
#                                         [0.5, 3.5], [1.5, 3.5], [2.5, 3.5], [3.5, 3.5],
#                                           ],
                  minimal_distance=0.1,
                  no_of_points=10000)
p = msh.plate_object
p.h = 0.2
p.reinforcement = [Reinforcement(p1=0.01, p2=0.01,
                                 p1u=0.01, p2u=0.01,
                                 node_name='reinforcement')]
p.plastic_moment_def_type = "ortho_reinf_indep"

for yl in p.yield_lines_with_ref:
    yl.reinforcement = 'reinforcement'

unn = p.unsupported_node_nos
# p = get_simple_mesh(4., 4., 4, 4)
print 'The plate has %d yield lines' % len(p.yield_lines)
view = YLPATreeView(root=p)

lp = LinearProgramming(plate=p, verbose=False)
print lp.solution
p.plot_3d()
view.configure_traits()

