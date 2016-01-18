'''
Created on Nov 14, 2014

@author: Werner
'''

from ylpa import \
    Plate, Node, PlateSegment, PlateLoadUniform, \
    ParametricStudy, Parameter, ParamNode, YieldLine, YLPATreeView

import numpy as np

a = 2.
b = 3.
n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=2 * b, y=0., w=0.)
n3 = Node(x=2 * b, y=2 * a, w=0.)
n4 = Node(x=0., y=2 * a, w=0.)

n5 = Node(x=0.5 * b, y=a, w=1.)
n6 = Node(x=1.5 * b, y=a)

sg1 = PlateSegment(node_nos=[1, 2, 6, 5])
sg2 = PlateSegment(node_nos=[2, 3, 6])
sg3 = PlateSegment(node_nos=[3, 4, 5, 6])
sg4 = PlateSegment(node_nos=[4, 1, 5])

yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5), YieldLine(2, 6), YieldLine(3, 6)]
plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  load=[PlateLoadUniform()],
                  plastic_moment_def_type="simple"
                  )

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=0.2 * b, minimum=0.01, maximum=b - 0.01),
                                 ],
                         param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      ParamNode(node_no=6, trait_name="x", param_no=1, multiplier=-1., base_value=2 * b)],
                         )

print pstudy.min_work_ratio
view = YLPATreeView(root=pstudy)
view.configure_traits()
