'''
Created on 2. 6. 2015

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, \
    ParametricStudy, YieldLine, Parameter, \
    ParamNode, ParamPlate, PlateLoadUniform, \
    Reinforcement, YLPATreeView

import numpy as np

b = 3.
a = 2.
n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=2 * b, y=0., w=0.)
n3 = Node(x=2 * b, y=2 * a, w=0.)
n4 = Node(x=b, y=2 * a)
n5 = Node(x=0., y=2 * a)
n6 = Node(x=0., y=a)

sg1 = PlateSegment(node_nos=[1, 2, 3, 4, 6])
sg2 = PlateSegment(node_nos=[4, 5, 6])

yl = [YieldLine(6, 4)]

reinforcement = [Reinforcement(p1=0.01, p2=0.01,
                               p1u=0.01, p2u=0.01,
                               node_name='reinforcement')]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2],
                  yield_lines=yl,
                  plastic_moment_def_type="ortho_reinf_dep",
                  load=[PlateLoadUniform()],
                  reinforcement=reinforcement,
                  h=0.2,
                  )

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=b, minimum=0.01, maximum=2 * b - 0.01),
                                      Parameter(base_value=a, minimum=0.01, maximum=2 * a - 0.01),
                                 ],
                         param_nodes=[ParamNode(node_no=4, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      ParamNode(node_no=6, trait_name="y", param_no=2, multiplier=1., base_value=0.)],
                         )

# print plate.unit_work_ratio
# print pstudy.min_work_ratio
# reinforcement[0].p1u = 0.005
# reinforcement[0].p2u = 0.005
# print pstudy.min_work_ratio
# reinforcement[0].p1u = 0.002
# reinforcement[0].p2u = 0.002
# print pstudy.min_work_ratio

view = YLPATreeView(root=pstudy)
view.configure_traits()
