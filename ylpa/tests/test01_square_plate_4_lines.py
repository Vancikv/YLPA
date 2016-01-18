'''
Created on 13. 11. 2014

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, YieldLine, \
    PlateLoadUniform

import numpy as np

def test_square_plate_yl():
    n1 = Node(x=0., y=0., w=0.)
    n2 = Node(x=4., y=0., w=0.)
    n3 = Node(x=4., y=4., w=0.)
    n4 = Node(x=0., y=4., w=0.)

    n5 = Node(x=2., y=2., w=1.)

    sg1 = PlateSegment(node_nos=[1, 2, 5])
    sg2 = PlateSegment(node_nos=[2, 3, 5])
    sg3 = PlateSegment(node_nos=[3, 4, 5])
    sg4 = PlateSegment(node_nos=[4, 1, 5])

    yl = [YieldLine(1, 5), YieldLine(2, 5), YieldLine(3, 5), YieldLine(4, 5)]
    plate = Plate(nodes=[n1, n2, n3, n4, n5],
                      segments=[sg1, sg2, sg3, sg4],
                      yield_lines=yl,
                      load=[PlateLoadUniform()],
                      plastic_moment_def_type="simple",
                      )

    assert np.allclose(plate.unit_work_ratio, 1.5)

if __name__ == '__main__':
    test_square_plate_yl()
