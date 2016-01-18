'''
Created on 30. 1. 2015

@author: Kapsak
'''


from traitsui.api import \
    TreeEditor, TreeNode, View, Item, Group, \
    HSplit, HGroup

from traitsui.menu import \
    Menu, MenuBar, Separator

from traitsui.wx.tree_editor import \
    DeleteAction, NewAction

from tree_nodes import \
    PlateNodesTreeNode, PlateSegmentsTreeNode, \
    PlateYieldLinesTreeNode, PlateLoadTreeNode, \
    PlateReinforcementTreeNode

from node import \
    Node

from plate_segment import \
    PlateSegment

from tree_view_handler import \
    plot_self, calc_self

from yield_line import \
    YieldLine

from plate import \
    Plate

from parametric_study import \
    ParametricStudy

from plate_load import \
    PlateLoadUniform, PlateLoadNodalForce

from plasticity import \
    Reinforcement

node_container_treenode = TreeNode(node_for=[PlateNodesTreeNode],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self, NewAction),
                                     add=[Node]
                                     )

segment_container_treenode = TreeNode(node_for=[PlateSegmentsTreeNode],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self, NewAction),
                                     add=[PlateSegment]
                                     )

load_container_treenode = TreeNode(node_for=[PlateLoadTreeNode],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(NewAction),
                                     add=[PlateLoadUniform, PlateLoadNodalForce]
                                     )

reinf_container_treenode = TreeNode(node_for=[PlateReinforcementTreeNode],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(NewAction),
                                     add=[Reinforcement]
                                     )

yield_line_container_treenode = TreeNode(node_for=[PlateYieldLinesTreeNode],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self, NewAction),
                                     add=[YieldLine]
                                     )

yield_line_treenode = TreeNode(node_for=[YieldLine],
                                     auto_open=True,
                                     children='',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self, DeleteAction),
                                     )
#

reinforcement_treenode = TreeNode(node_for=[Reinforcement],
                                     auto_open=True,
                                     children='',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(DeleteAction),
                                     )

uniform_load_treenode = TreeNode(node_for=[PlateLoadUniform],
                                     auto_open=True,
                                     children='',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(DeleteAction),
                                     )

force_load_treenode = TreeNode(node_for=[PlateLoadNodalForce],
                                     auto_open=True,
                                     children='',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(DeleteAction),
                                     )

plate_treenode = TreeNode(node_for=[Plate],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self),
                                     )

node_treenode = TreeNode(node_for=[Node],
                                     auto_open=True,
                                     children='',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self, DeleteAction),
                                     )

segment_treenode = TreeNode(node_for=[PlateSegment],
                                     auto_open=True,
                                     children='',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self, DeleteAction),
                                     )

pstudy_treenode = TreeNode(node_for=[ParametricStudy],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(plot_self, calc_self),
                                     )

custom_treenode_list = [node_container_treenode, segment_container_treenode,
                     node_treenode, segment_treenode, load_container_treenode,
                     yield_line_container_treenode, uniform_load_treenode, force_load_treenode,
                     yield_line_treenode, plate_treenode, pstudy_treenode,
                     reinf_container_treenode, reinforcement_treenode]
