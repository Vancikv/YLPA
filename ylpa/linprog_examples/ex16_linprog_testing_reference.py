'''
Created on 28. 5. 2015

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, \
    ParametricStudy, YieldLine, Parameter, \
    ParamNode, ParamPlate, PlateLoadUniform, \
    Reinforcement

import numpy as np

b = 1.5
a = 1.0
reinf = 0.01
n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=2 * b, y=0., w=0.)
n3 = Node(x=2 * b, y=2 * a, w=0.)
n4 = Node(x=0., y=2 * a, w=0.)

n5 = Node(x=1., y=a)
n6 = Node(x=2.)

sg1 = PlateSegment(node_nos=[1, 2, 6, 5])
sg2 = PlateSegment(node_nos=[2, 3, 6])
sg3 = PlateSegment(node_nos=[3, 4, 5, 6])
sg4 = PlateSegment(node_nos=[4, 1, 5])

yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5), YieldLine(2, 6), YieldLine(3, 6)]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="simple",
                  load=[PlateLoadUniform()],
                  )

print plate.unit_work_ratio
print plate.dissipation_rate
print plate.unit_volume