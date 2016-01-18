'''
Created on 25. 3. 2015

@author: Kapsak
'''

from plate import Plate
from parametric_study import ParametricStudy
from tree_view import YLPATreeView

plate = Plate(nodes=[],
                  segments=[],
                  yield_lines=[],
                  plastic_moment_def_type="simple",
                  load=[])

pstudy = ParametricStudy(plate=plate)

view = YLPATreeView(root=pstudy)
view.configure_traits()
