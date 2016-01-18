'''
Created on 20. 4. 2015

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, PlateLoadUniform, \
    ParametricStudy, YieldLine, Parameter, \
    ParamNode, ParamPlate, YLPATreeView, \
    Reinforcement

b = 2.5
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

yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5), YieldLine(2, 6), YieldLine(3, 6),
      YieldLine(1, 2), YieldLine(2, 3), YieldLine(3, 4)]

reinforcement = [Reinforcement(p1=reinf, p2=reinf, p1u=reinf, p2u=reinf,
                               d1_1=0.04, d1_2=0.03, d1_1u=0.04, d1_2u=0.03, node_name='reinforcement')]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="ortho_reinf_dep",
                  load=[PlateLoadUniform()],
                  reinforcement=reinforcement,
                  p1=0.01,
                  p2=0.01,
                  p2u=0.01,
                  h=0.15,
                  d1_1=0.04,
                  d1_2=0.030,
                  d1_1u=0.04,
                  d1_2u=0.030,)

pstudy = ParametricStudy(plate=plate,
                         optimization_constrain_value=0.02,
                         node_params=[
                                Parameter(base_value=0.2 * b, minimum=0.01, maximum=b - 0.01),
                                Parameter(base_value=a, minimum=0.01, maximum=2 * a - 0.01),
                                Parameter(base_value=b + 0.8 * b, minimum=b + 0.01, maximum=2 * b - 0.01),
                                 ],
                         plate_params=[
                                 Parameter(base_value=0.005, minimum=0.0, maximum=0.02),
                                 Parameter(base_value=0.005, minimum=0.0, maximum=0.02),
                                 Parameter(base_value=0.005, minimum=0.0, maximum=0.02),
                                 Parameter(base_value=0.005, minimum=0.0, maximum=0.02),
                                 ],
                        param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                     ParamNode(node_no=5, trait_name="y", param_no=2, multiplier=1., base_value=0.),
                                     ParamNode(node_no=6, trait_name="x", param_no=3, multiplier=1., base_value=0.)],
                         param_plate=[ParamPlate(trait_name="p1", param_no=1, multiplier=1, base_value=0., reinf_layout_name='reinforcement'),
                                   ParamPlate(trait_name="p2", param_no=2, multiplier=1, base_value=0., reinf_layout_name='reinforcement'),
                                   ParamPlate(trait_name="p1u", param_no=3, multiplier=1, base_value=0., reinf_layout_name='reinforcement'),
                                   ParamPlate(trait_name="p2u", param_no=4, multiplier=1, base_value=0., reinf_layout_name='reinforcement'),
                                   ]
                         )

view = YLPATreeView(root=pstudy)
view.configure_traits()
