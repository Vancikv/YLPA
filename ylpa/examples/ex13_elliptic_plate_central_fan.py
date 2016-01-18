'''
Created on 20. 4. 2015

@author: Kapsak
'''

from ylpa import \
    Plate, Node, PlateSegment, ParamNode, \
    ParametricStudy, YieldLine, PlateLoadUniform, \
    Parameter, YLPATreeView, ParamPlate

import numpy as np
import matplotlib.pyplot as plt

a = 3.0
b = 3.
no_of_segments = 20
reinf = 0.01
nds = []
segs = []
yls = []
pars = [Parameter(base_value=0.005, minimum=0.0, maximum=0.02),
        Parameter(base_value=0.005, minimum=0.0, maximum=0.02)]
parps = [ParamPlate(trait_name="p1", param_no=1, multiplier=1, base_value=0.),
         ParamPlate(trait_name="p2", param_no=2, multiplier=1, base_value=0.)]

for fi in np.linspace(start=0., stop=np.pi * 2, num=no_of_segments, endpoint=False):
    nds.append(Node(x=a * np.cos(fi), y=b * np.sin(fi), w=0.))
    segs.append(PlateSegment(node_nos=[len(nds), len(nds) + 1, no_of_segments + 1]))
    yls.append(YieldLine(len(nds), no_of_segments + 1))

del segs[-1]
segs.append(PlateSegment(node_nos=[no_of_segments, 1, no_of_segments + 1]))
nds.append(Node(x=0., y=0.))

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
                         plate_params=pars,
                         param_nodes=[],
                         param_plate=parps
                         )


view = YLPATreeView(root=pstudy)
view.configure_traits()
