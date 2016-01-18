'''
Created on 11. 2. 2015

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, ParamNode, \
    ParametricStudy, YieldLine, PlateLoadUniform, \
    Parameter, YLPATreeView, ParamPlate

import numpy as np
import matplotlib.pyplot as plt

a = 4.
b = 3.
no_of_segments = 40
inner_nodes = no_of_segments / 2 - 1
dx = 0.24 * a
reinf = 0.01
nds = []
segs = []
yls = []
npars = [Parameter(base_value=a * 0.5, minimum=0.01, maximum=a * 0.95)]
ppars = [Parameter(base_value=0.005, minimum=0.0, maximum=0.01),
        Parameter(base_value=0.005, minimum=0.0, maximum=0.01)]
parns = []
parps = [ParamPlate(trait_name="p1", param_no=1, multiplier=1, base_value=0.),
         ParamPlate(trait_name="p2", param_no=2, multiplier=1, base_value=0.)]

for fi in np.linspace(start=0., stop=np.pi * 2, num=no_of_segments, endpoint=False):
    nds.append(Node(x=a * np.cos(fi), y=b * np.sin(fi), w=0.))

for x in np.linspace(start=dx, stop=-dx, num=inner_nodes, endpoint=True):
    if x != 0.:
        nds.append(Node(x=x, y=0.))
        parns.append(ParamNode(node_no=len(nds), trait_name="x", param_no=1, multiplier=x / dx, base_value=0.))
    else:
        nds.append(Node(x=x, y=0.))

yls.append(YieldLine(no_of_segments / 2 + 1, no_of_segments + inner_nodes))
yls.append(YieldLine(1, no_of_segments + 1))
for i in range(no_of_segments + 1, no_of_segments + inner_nodes):
    yls.append(YieldLine(i, i + 1))

for i in range(1, no_of_segments / 4 + 1):
    if i == 1:
        segs.append(PlateSegment(node_nos=[1, 2, no_of_segments + 1]))
        segs.append(PlateSegment(node_nos=[no_of_segments / 2, no_of_segments / 2 + 1, no_of_segments + inner_nodes]))
        segs.append(PlateSegment(node_nos=[no_of_segments / 2 + 1, no_of_segments / 2 + 2, no_of_segments + inner_nodes]))
        segs.append(PlateSegment(node_nos=[no_of_segments, 1, no_of_segments + 1]))
    else:
        segs.append(PlateSegment(node_nos=[i, i + 1, no_of_segments + i, no_of_segments + i - 1]))
        segs.append(PlateSegment(node_nos=[no_of_segments / 2 - i + 1, no_of_segments / 2 - i + 2,
                                           no_of_segments + inner_nodes - i + 2, no_of_segments + inner_nodes - i + 1]))
        segs.append(PlateSegment(node_nos=[no_of_segments / 2 + i, no_of_segments / 2 + i + 1,
                                           no_of_segments + inner_nodes - i + 1, no_of_segments + inner_nodes - i + 2]))
        segs.append(PlateSegment(node_nos=[no_of_segments - i + 1, no_of_segments - i + 2, no_of_segments + i - 1, no_of_segments + i]))
        yls.append(YieldLine(i, no_of_segments + i - 1))
        yls.append(YieldLine(no_of_segments / 2 - i + 2, no_of_segments + inner_nodes - i + 2))
        yls.append(YieldLine(no_of_segments / 2 + i, no_of_segments + inner_nodes - i + 2))
        yls.append(YieldLine(no_of_segments - i + 2, no_of_segments + i - 1))

yls.append(YieldLine(no_of_segments / 4 + 1, no_of_segments + no_of_segments / 4))
yls.append(YieldLine(no_of_segments / 2 + no_of_segments / 4 + 1, no_of_segments + inner_nodes - no_of_segments / 4 + 1))

plate = Plate(nodes=nds,
                  segments=segs,
                  yield_lines=yls,
                  plastic_moment_def_type="ortho_reinf_dep",
                  load=[PlateLoadUniform()],
                  p1=0.0025, p2=0.005,
                  h=0.20,
                  d1_1=0.04, d1_2=0.03,
                  f_c=38000.,
                  f_y=500000.,
                  )

pstudy = ParametricStudy(plate=plate,
                         node_params=npars,
                         plate_params=ppars,
                         param_nodes=parns,
                         param_plate=parps
                         )

view = YLPATreeView(root=pstudy)
view.configure_traits()
