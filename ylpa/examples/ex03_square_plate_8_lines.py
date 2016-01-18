'''
Created on 13. 11. 2014

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, PlateLoadUniform, \
    ParametricStudy, YieldLine, Parameter, \
    ParamNode

a = 3.

n1 = Node(x=0., y=0.)
n2 = Node(x=2 * a, y=0.)
n3 = Node(x=2 * a, y=2 * a)
n4 = Node(x=0., y=2 * a)

n5 = Node(x=0., y=0., w=0.)
n6 = Node(x=0., y=0., w=0.)
n7 = Node(x=2 * a, y=0., w=0.)
n8 = Node(x=2 * a, y=0., w=0.)
n9 = Node(x=0., y=2 * a, w=0.)
n10 = Node(x=0., y=2 * a, w=0.)
n11 = Node(x=0., y=0., w=0.)
n12 = Node(x=0., y=0., w=0.)

n13 = Node(x=a, y=a)

sg1 = PlateSegment(node_nos=[1, 5, 13, 12])
sg2 = PlateSegment(node_nos=[5, 6, 13])
sg3 = PlateSegment(node_nos=[6, 2, 7, 13])
sg4 = PlateSegment(node_nos=[7, 8, 13])
sg5 = PlateSegment(node_nos=[3, 9, 13, 8])
sg6 = PlateSegment(node_nos=[9, 10, 13])
sg7 = PlateSegment(node_nos=[10, 4, 11, 13])
sg8 = PlateSegment(node_nos=[11, 12, 13])

yl = [YieldLine(5, 13), YieldLine(6, 13), YieldLine(7, 13), YieldLine(8, 13),
      YieldLine(9, 13), YieldLine(10, 13), YieldLine(11, 13), YieldLine(12, 13)]
plate = Plate(nodes=[n1, n2, n3, n4, n5, n6, n7,
                     n8, n9, n10, n11, n12, n13],
                  segments=[sg1, sg2, sg3, sg4,
                            sg5, sg6, sg7, sg8],
                  yield_lines=yl,
                  plastic_moment_def_type="simple",
                  load=[PlateLoadUniform()])

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=0.5, minimum=0.01, maximum=0.99)],
                         param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=-a, base_value=a),
                                      ParamNode(node_no=6, trait_name="x", param_no=1, multiplier=a, base_value=a),
                                      ParamNode(node_no=7, trait_name="y", param_no=1, multiplier=-a, base_value=a),
                                      ParamNode(node_no=8, trait_name="y", param_no=1, multiplier=a, base_value=a),
                                      ParamNode(node_no=9, trait_name="x", param_no=1, multiplier=a, base_value=a),
                                      ParamNode(node_no=10, trait_name="x", param_no=1, multiplier=-a, base_value=a),
                                      ParamNode(node_no=11, trait_name="y", param_no=1, multiplier=a, base_value=a),
                                      ParamNode(node_no=12, trait_name="y", param_no=1, multiplier=-a, base_value=a)]
                         )

print pstudy.min_work_ratio
print pstudy.plate.unit_work_ratio
