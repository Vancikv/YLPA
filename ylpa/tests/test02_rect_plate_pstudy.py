'''
Created on 17. 11. 2014

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, PlateLoadUniform, PStudyBruteForce, \
    YieldLine

import numpy as np

def test_rect_plate_yl_pstudy():
    n1 = Node(x=0., y=0., w=0.)
    n2 = Node(x=4., y=0., w=0.)
    n3 = Node(x=4., y=2., w=0.)
    n4 = Node(x=0., y=2., w=0.)

    n5 = Node(x=2., y=1.)
    n6 = Node(x=3., y=1.)

    sg1 = PlateSegment(node_nos=[1, 2, 6, 5])
    sg2 = PlateSegment(node_nos=[2, 3, 6])
    sg3 = PlateSegment(node_nos=[3, 4, 5, 6])
    sg4 = PlateSegment(node_nos=[4, 1, 5])

    yl = [YieldLine(1, 5), YieldLine(4, 5), YieldLine(6, 5),
          YieldLine(2, 6), YieldLine(3, 6)]
    plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                      segments=[sg1, sg2, sg3, sg4],
                      yield_lines=yl,
                      load=[PlateLoadUniform()],
                      plastic_moment_def_type="simple")

    pstudy = PStudyBruteForce(plate=plate,
                             parameters=[(0.1, 0.9, 9), (0.1, 0.9, 9)],
                             param_nodes=[(4, "x", 0, 4., 0.), (4, "y", 1, 2., 0.), (5, "x", 0, -4., 4.)])

    assert np.allclose(pstudy.param_arr[:11, :], [[ 0.1 , 0.1], [ 0.1 , 0.2], [ 0.1 , 0.3],
                                                [ 0.1 , 0.4], [ 0.1 , 0.5], [ 0.1 , 0.6],
                                                [ 0.1 , 0.7], [ 0.1 , 0.8], [ 0.1 , 0.9],
                                                [ 0.2 , 0.1], [ 0.2 , 0.2]])

    assert np.allclose(pstudy.work_ratio_arr[:12], [8.63095238, 6.02678571, 5.22959184, 4.91071429,
                                                    4.82142857, 4.91071429, 5.22959184, 6.02678571,
                                                    8.63095238, 7.8525641 , 5.04807692, 4.18956044])

if __name__ == '__main__':
    test_rect_plate_yl_pstudy()
