'''
Created on Feb 10, 2015

@author: Werner

Modelling a plate from 'Jiangpeng Shu, David Fall, Mario Plos, Kamyab Zandi, Karin Lundgren,
Development of Modelling Strategies for Twoway RC Slabs'
'''
from ylpa import \
    Plate, Node, PlateSegment, \
    YieldLine, YLPATreeView, PlateLoadNodalForce

import numpy as np

n1 = Node(x=0.7, y=0., w=0.)
n2 = Node(x=1.7, y=0., w=0.)
n3 = Node(x=2.05, y=0.35)
n4 = Node(x=2.4, y=0.7, w=0.)
n5 = Node(x=2.4, y=1.7, w=0.)
n6 = Node(x=2.05, y=2.05)
n7 = Node(x=1.7, y=2.4, w=0.)
n8 = Node(x=0.7, y=2.4, w=0.)
n9 = Node(x=0.35, y=2.05)
n10 = Node(x=0., y=1.7, w=0.)
n11 = Node(x=0., y=0.7, w=0.)
n12 = Node(x=0.35, y=0.35)
n13 = Node(x=1.2, y=1.2)

sg1 = PlateSegment(node_nos=[1, 2, 3, 13, 12])
sg2 = PlateSegment(node_nos=[3, 4, 5, 6, 13])
sg3 = PlateSegment(node_nos=[6, 7, 8, 9, 13])
sg4 = PlateSegment(node_nos=[9, 10, 11, 12, 13])

yl = [YieldLine(3, 13), YieldLine(6, 13), YieldLine(9, 13), YieldLine(12, 13)]

plate = Plate(nodes=[n1, n2, n3, n4, n5, n6,
                     n7, n8, n9, n10, n11, n12, n13],
                  segments=[sg1, sg2, sg3, sg4],
                  yield_lines=yl,
                  plastic_moment_def_type="ortho_reinf_dep",
                  load=[PlateLoadNodalForce(x=1.2, y=1.2)],
                  p1=0.003682, p2=0.001841,
                  h=0.083,
                  d1_1=0.023, d1_2=0.029,
                  f_c=50900.,
                  f_y=666000.)

mb = plate.plastic_moment_def.get_plastic_moment(np.pi / 4.)
print '=======CALCULATION COMMENCING======='
print 'mb = %f' % mb

print plate.unit_work_ratio
print 8 * mb * 0.85 / 1.2
print '=======CALCULATION FINISHED======='

view = YLPATreeView(root=plate)
view.configure_traits()
