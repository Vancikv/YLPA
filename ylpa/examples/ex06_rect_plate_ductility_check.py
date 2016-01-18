'''
Created on Apr 16, 2015

@author: Werner
'''

from ylpa import \
    Plate, Node, PlateSegment, PlateLoadUniform, \
    ParametricStudy, YieldLine, Parameter, \
    ParamNode


b = 4.
a = 2.
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
plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="ortho_reinf_dep_duct",
                  load=[PlateLoadUniform()],
                  p1=0.02,
                  p2=0.02,
                  h=0.15,
                  d1_1=0.04,
                  d1_2=0.035,)

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=0.2 * b, minimum=0.01, maximum=b - 0.01),
                                 Parameter(base_value=a),
                                 Parameter(base_value=b + 0.8 * b, minimum=b + 0.01, maximum=2 * b - 0.01),
                                 ],
                         param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      ParamNode(node_no=5, trait_name="y", param_no=2, multiplier=1., base_value=0.),
                                      ParamNode(node_no=6, trait_name="x", param_no=3, multiplier=1., base_value=0.)],
                         )

print pstudy.min_work_ratio
print n5.x, n6.x
print plate.check_ductility()
