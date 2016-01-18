'''
Created on Nov 14, 2014

@author: Werner
'''

from ylpa import \
    Plate, Node, PlateSegment, \
    ParametricStudy, YieldLine, Parameter, \
    ParamNode, ParamPlate, PlateLoadUniform, \
    Reinforcement

import numpy as np

b = 3.
a = 2.
reinf = 0.01
n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=2 * b, y=0., w=0.)
n3 = Node(x=2 * b, y=2 * a, w=0.)
n4 = Node(x=0., y=2 * a, w=0.)

n5 = Node(x=0.5 * b, y=a, w=1.)
n6 = Node(x=1.5 * b)

sg1 = PlateSegment(node_nos=[1, 2, 6, 5])
sg2 = PlateSegment(node_nos=[2, 3, 6])
sg3 = PlateSegment(node_nos=[3, 4, 5, 6])
sg4 = PlateSegment(node_nos=[4, 1, 5])

yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5), YieldLine(2, 6), YieldLine(3, 6)]

reinforcement = [Reinforcement(p1=reinf, p2=reinf, d1_1=0.03, d1_2=0.03, node_name='reinforcement')]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="ortho_reinf_dep",
                  load=[PlateLoadUniform()],
                  reinforcement=reinforcement,
                  h=0.2,
                  )

pstudy = ParametricStudy(plate=plate,
                         optimization_constrain_value=reinf,
                         node_params=[Parameter(base_value=0.2 * b, minimum=0.01, maximum=b - 0.01),
                                 Parameter(base_value=a),
                                 Parameter(base_value=b + 0.8 * b, minimum=b + 0.01, maximum=2 * b - 0.01),
                                 ],
                         plate_params=[
                                 Parameter(base_value=0.005, minimum=0.0, maximum=reinf),
                                 Parameter(base_value=0.005, minimum=0.0, maximum=reinf)
                                 ],
                         param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      ParamNode(node_no=5, trait_name="y", param_no=2, multiplier=1., base_value=0.),
                                      ParamNode(node_no=6, trait_name="x", param_no=3, multiplier=1., base_value=0.)],
                         param_plate=[ParamPlate(trait_name="p1", param_no=1, multiplier=1., base_value=0., reinf_layout_name='reinforcement'),
                                      ParamPlate(trait_name="p2", param_no=2, multiplier=1., base_value=0., reinf_layout_name='reinforcement')]
                         )

# print pstudy.plate.plastic_moment_def.get_plastic_moment(0.)
# print pstudy.plate.plastic_moment_def.get_plastic_moment(np.pi / 2.)

print plate.unit_work_ratio
print pstudy.min_work_ratio
# print n5.x / (a / 4.), pstudy.plate.p1 / reinf, pstudy.plate.p2 / reinf

# print pstudy.plate.plastic_moment_def.get_plastic_moment(0.)
# print pstudy.plate.plastic_moment_def.get_plastic_moment(np.pi / 2.)
