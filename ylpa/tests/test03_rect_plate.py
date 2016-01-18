'''
Created on 9. 2. 2015

@author: Kapsak

Conserving ex09
'''

from ylpa import \
    Plate, Node, PlateSegment, ParamNode, \
    ParametricStudy, YieldLine, \
    Parameter, PlateLoadUniform, Reinforcement

import numpy as np

a, b = 6., 4.

def test_rect_plate():
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

    reinforcement = [Reinforcement(p1=0.01, p2=0.01, d1_1=0.04, d1_2=0.04)]

    plate = Plate(nodes=[n1, n2, n3, n4, n5, n6],
                      segments=[sg1, sg2, sg3, sg4],
                      yield_lines=yl,
                      plastic_moment_def_type="ortho_reinf_indep",
                      load=[PlateLoadUniform()],
                      reinforcement=reinforcement,
                      h=0.2,
                      )

    pstudy = ParametricStudy(plate=plate,
                             node_params=[Parameter(base_value=0.1 * a, minimum=0.01, maximum=a / 2 - 0.01),
                                     Parameter(base_value=b / 2),
                                     Parameter(base_value=(a + 0.8 * a) / 2, minimum=a / 2 + 0.01, maximum=a - 0.01)],
                             param_nodes=[ParamNode(node_no=5, trait_name="x", param_no=1, multiplier=1., base_value=0.),
                                          ParamNode(node_no=5, trait_name="y", param_no=2, multiplier=1., base_value=0.),
                                          ParamNode(node_no=6, trait_name="x", param_no=3, multiplier=1., base_value=0.)])

    print pstudy.min_work_ratio
    assert np.allclose(n5.x, 2.378509)
    assert np.allclose(plate.unit_work_ratio, 155.737086)

    plate.reinforcement[0].p1 = 0.005
    print pstudy.min_work_ratio
    print n5.x
    assert np.allclose(n5.x, 1.90219978009)
    assert np.allclose(plate.unit_work_ratio, 127.187730434)

    plate.reinforcement[0].p1 = 0.0025
    print pstudy.min_work_ratio
    print n5.x
    assert np.allclose(n5.x, 1.46859009458)
    assert np.allclose(plate.unit_work_ratio, 108.990441774)

if __name__ == '__main__':
    test_rect_plate()
