'''
Created on 26. 4. 2015

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, PlateLoadUniform, \
    ParametricStudy, Parameter, ParamNode, YieldLine

a = 2.
b = 3.
n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=b, y=0.)
n3 = Node(x=2 * b, y=0., w=0.)
n4 = Node(x=2 * b, y=a, w=0.)
n5 = Node(x=b, y=a)
n6 = Node(x=0, y=a, w=0.)

sg1 = PlateSegment(node_nos=[1, 2, 5, 6])
sg2 = PlateSegment(node_nos=[2, 3, 4, 5])

yl = [YieldLine(2, 5)]
plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2],
                  yield_lines=yl,
                  load=[PlateLoadUniform()],
                  plastic_moment_def_type="simple"
                  )

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=b, minimum=0.01, maximum=2 * b - 0.01),
                                 ],
                         param_nodes=[ParamNode(node_no=2, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      # ParamNode(node_no=6, trait_name="x", param_no=1, multiplier=-1., base_value=2 * b)
                                      ],
                         )

print pstudy.min_work_ratio
