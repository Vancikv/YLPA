'''
Created on 28. 1. 2015

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, ParamNode, \
    ParametricStudy, YLPATreeView, YieldLine, \
    Parameter, PlateLoadUniform

n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=4., y=-1., w=0.)
n3 = Node(x=4., y=3., w=0.)
n4 = Node(x=0.5, y=1.9, w=0.)

n5 = Node(x=2., y=1., w=1.)
n6 = Node(x=3., y=1.)

sg1 = PlateSegment(node_nos=[1, 2, 6, 5])
sg2 = PlateSegment(node_nos=[2, 3, 6])
sg3 = PlateSegment(node_nos=[3, 4, 5, 6])
sg4 = PlateSegment(node_nos=[4, 1, 5])

yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5), YieldLine(2, 6), YieldLine(3, 6)]
plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="simple",
                  load=[PlateLoadUniform()])

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=2.),
                                 Parameter(base_value=0.99),
                                 Parameter(base_value=1.02)],
                         param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      ParamNode(node_no=5, trait_name="y", param_no=2, multiplier=1., base_value=0.),
                                      ParamNode(node_no=6, trait_name="y", param_no=3, multiplier=1., base_value=0.)])

view = YLPATreeView(root=pstudy)
view.configure_traits()
