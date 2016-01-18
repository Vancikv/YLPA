'''
Created on 17. 11. 2014

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, \
    ParametricStudy, YieldLine, Parameter, \
    ParamNode, PlateLoadNodalForce, YLPATreeView

import numpy as np

b = 3.
a = 2.
n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=2 * b, y=0., w=0.)
n3 = Node(x=2 * b, y=2 * a, w=0.)
n4 = Node(x=0., y=2 * a, w=0.)

n5 = Node(x=0.99 * b, y=a)
n6 = Node(x=b, y=a, w=1.)
n7 = Node(x=1.01 * b, y=a)

sg1 = PlateSegment(node_nos=[1, 2, 7, 6, 5])
sg2 = PlateSegment(node_nos=[2, 3, 7])
sg3 = PlateSegment(node_nos=[3, 4, 5, 6, 7])
sg4 = PlateSegment(node_nos=[4, 1, 5])

yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5), YieldLine(7, 6), YieldLine(2, 7), YieldLine(3, 7)]
plate = Plate(nodes=[n1, n2, n3, n4, n5, n6, n7],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="simple",
                  load=[PlateLoadNodalForce()],
                  h=0.15,)

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=0.2 * b, minimum=0.01, maximum=b - 0.01),
                                 ],
                         param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      ParamNode(node_no=7, trait_name="x", param_no=1, multiplier=-1., base_value=2 * b)],
                         )
print pstudy.min_work_ratio
print n5.x, n7.x
view = YLPATreeView(root=pstudy)
view.configure_traits()

'''
Corner patterns, corners can lift.
'''

n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=0., y=0., w=0.)
n3 = Node(x=2 * b, y=0., w=0.)
n4 = Node(x=2 * b, y=0., w=0.)
n5 = Node(x=0., y=2 * a, w=0.)
n6 = Node(x=0., y=2 * a, w=0.)
n7 = Node(x=0., y=0., w=0.)
n8 = Node(x=0., y=0., w=0.)

n9 = Node(x=b, y=a, w=1.)

sg1 = PlateSegment(node_nos=[8, 1, 9])
sg2 = PlateSegment(node_nos=[1, 2, 9])
sg3 = PlateSegment(node_nos=[2, 3, 9])
sg4 = PlateSegment(node_nos=[3, 4, 9])
sg5 = PlateSegment(node_nos=[4, 5, 9])
sg6 = PlateSegment(node_nos=[5, 6, 9])
sg7 = PlateSegment(node_nos=[6, 7, 9])
sg8 = PlateSegment(node_nos=[7, 8, 9])

yl = [YieldLine(1, 9), YieldLine(2, 9), YieldLine(3, 9), YieldLine(4, 9),
      YieldLine(5, 9), YieldLine(6, 9), YieldLine(7, 9), YieldLine(8, 9)]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6, n7,
                     n8, n9],
                  segments=[sg1, sg2, sg3, sg4,
                            sg5, sg6, sg7, sg8],
                  yield_lines=yl,
                  plastic_moment_def_type="simple",
                  load=[PlateLoadNodalForce()],
                  h=0.15,)

pstudy = ParametricStudy(plate=plate,
                         params=[Parameter(base_value=0.2 * b, minimum=0.01, maximum=0.99),
                                 ],
                         param_nodes=[ParamNode(node_no=1, trait_name="x", param_no=1, multiplier=b, base_value=0.),
                                      ParamNode(node_no=2, trait_name="x", param_no=1, multiplier=-b, base_value=2 * b),
                                      ParamNode(node_no=3, trait_name="y", param_no=1, multiplier=a, base_value=0.),
                                      ParamNode(node_no=4, trait_name="y", param_no=1, multiplier=-a, base_value=2 * a),
                                      ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=-b, base_value=2 * b),
                                      ParamNode(node_no=6, trait_name="x", param_no=1, multiplier=b, base_value=0.),
                                      ParamNode(node_no=7, trait_name="y", param_no=1, multiplier=-a, base_value=2 * a),
                                      ParamNode(node_no=8, trait_name="y", param_no=1, multiplier=a, base_value=0.)],
                         )
print pstudy.min_work_ratio
print n1.x

'''
Corner patterns, corners cannot lift.
'''

n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=0., y=0., w=0.)
n3 = Node(x=2 * b, y=0., w=0.)
n4 = Node(x=2 * b, y=0., w=0.)
n5 = Node(x=0., y=2 * a, w=0.)
n6 = Node(x=0., y=2 * a, w=0.)
n7 = Node(x=0., y=0., w=0.)
n8 = Node(x=0., y=0., w=0.)

n9 = Node(x=b, y=a, w=1.)

sg1 = PlateSegment(node_nos=[8, 1, 9])
sg2 = PlateSegment(node_nos=[1, 2, 9])
sg3 = PlateSegment(node_nos=[2, 3, 9])
sg4 = PlateSegment(node_nos=[3, 4, 9])
sg5 = PlateSegment(node_nos=[4, 5, 9])
sg6 = PlateSegment(node_nos=[5, 6, 9])
sg7 = PlateSegment(node_nos=[6, 7, 9])
sg8 = PlateSegment(node_nos=[7, 8, 9])

yl = [YieldLine(1, 9), YieldLine(2, 9), YieldLine(3, 9), YieldLine(4, 9),
      YieldLine(5, 9), YieldLine(6, 9), YieldLine(7, 9), YieldLine(8, 9),
      YieldLine(8, 1), YieldLine(2, 3), YieldLine(4, 5), YieldLine(6, 7)]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6, n7,
                     n8, n9],
                  segments=[sg1, sg2, sg3, sg4,
                            sg5, sg6, sg7, sg8],
                  yield_lines=yl,
                  plastic_moment_def_type="simple",
                  load=[PlateLoadNodalForce()],
                  h=0.15,)

pstudy = ParametricStudy(plate=plate,
                         params=[Parameter(base_value=0.2 * b, minimum=0.01, maximum=0.99),
                                 ],
                         param_nodes=[ParamNode(node_no=1, trait_name="x", param_no=1, multiplier=b, base_value=0.),
                                      ParamNode(node_no=2, trait_name="x", param_no=1, multiplier=-b, base_value=2 * b),
                                      ParamNode(node_no=3, trait_name="y", param_no=1, multiplier=a, base_value=0.),
                                      ParamNode(node_no=4, trait_name="y", param_no=1, multiplier=-a, base_value=2 * a),
                                      ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=-b, base_value=2 * b),
                                      ParamNode(node_no=6, trait_name="x", param_no=1, multiplier=b, base_value=0.),
                                      ParamNode(node_no=7, trait_name="y", param_no=1, multiplier=-a, base_value=2 * a),
                                      ParamNode(node_no=8, trait_name="y", param_no=1, multiplier=a, base_value=0.)],
                         )
print pstudy.min_work_ratio
print n1.x
