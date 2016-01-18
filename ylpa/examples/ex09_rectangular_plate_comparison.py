'''
Created on 9. 2. 2015

@author: Kapsak

This example shows the modelling of a rectangular plate and
comparison of the results with [Sobotka, 1973, page 46]

Input value:
a = 6 m
b = 4 m
h = 0.2 m
d1_1 = d1_2 = 0.04 m
p1 = 0.01, 0.005, 0.0025
p2 = 0.01
'''

from ylpa import \
    Plate, Node, PlateSegment, ParamNode, \
    ParametricStudy, YieldLine, Parameter, \
    PlateLoadUniform

import numpy as np

a, b = 6., 4.

n1 = Node(x=0., y=0., w=0.)
n2 = Node(x=a, y=0., w=0.)
n3 = Node(x=a, y=b, w=0.)
n4 = Node(x=0, y=b, w=0.)

n5 = Node(x=a / 3., y=b)
n6 = Node(x=2. * a / 3., y=b)

sg1 = PlateSegment(node_nos=[1, 2, 6, 5])
sg2 = PlateSegment(node_nos=[2, 3, 6])
sg3 = PlateSegment(node_nos=[3, 4, 5, 6])
sg4 = PlateSegment(node_nos=[4, 1, 5])

yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5), YieldLine(2, 6), YieldLine(3, 6)]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="ortho_reinf_indep",
                  p1=0.01, p2=0.01,
                  h=0.2,
                  d1_1=0.04, d1_2=0.04,
                  load=[PlateLoadUniform()])

pstudy = ParametricStudy(plate=plate,
                         node_params=[Parameter(base_value=0.1 * a, minimum=0.01, maximum=a / 2 - 0.01),
                                 Parameter(base_value=b / 2),
                                 Parameter(base_value=(a + 0.8 * a) / 2, minimum=a / 2 + 0.01, maximum=a - 0.01)],
                         param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                      ParamNode(node_no=5, trait_name="y", param_no=2, multiplier=1., base_value=0.),
                                      ParamNode(node_no=6, trait_name="x", param_no=3, multiplier=1., base_value=0.)])

m1 = plate.plastic_moment_def.get_plastic_moment(np.pi / 2.)
m2 = plate.plastic_moment_def.get_plastic_moment(0.)
lambda_ratio = m1 / m2
print '=======CALCULATION COMMENCING======='
print 'm1 = %f' % m1
print 'm2 = %f' % m2
print 'lambda = %f' % lambda_ratio

print pstudy.min_work_ratio
print 'Results [Results from Sobotka]'
print 'x_5 = %f [2.378510]' % n5.x
print 'limit load = %f  [155.737081]' % plate.unit_work_ratio

print '=======CALCULATION FINISHED======='
plate.p1 = 0.005
m1 = plate.plastic_moment_def.get_plastic_moment(np.pi / 2.)
m2 = plate.plastic_moment_def.get_plastic_moment(0.)
lambda_ratio = m1 / m2
print '=======CALCULATION COMMENCING======='
print 'm1 = %f' % m1
print 'm2 = %f' % m2
print 'lambda = %f' % lambda_ratio

print pstudy.min_work_ratio
print 'Results [Results from Sobotka]'
print 'x_5 = %f [1.935079]' % n5.x
print 'limit load = %f  [127.18763]' % plate.unit_work_ratio

print '=======CALCULATION FINISHED======='

plate.p1 = 0.0025
m1 = plate.plastic_moment_def.get_plastic_moment(np.pi / 2.)
m2 = plate.plastic_moment_def.get_plastic_moment(0.)
lambda_ratio = m1 / m2
print '=======CALCULATION COMMENCING======='
print 'm1 = %f' % m1
print 'm2 = %f' % m2
print 'lambda = %f' % lambda_ratio

print pstudy.min_work_ratio
print 'Results [Results from Sobotka]'
print 'x_5 = %f [1.509222]' % n5.x
print 'limit load = %f  [108.99035]' % plate.unit_work_ratio

print '=======CALCULATION FINISHED======='
