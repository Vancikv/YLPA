'''
Created on 28. 1. 2015

@author: Kapsak
'''

from traits.api import \
    HasTraits, Instance, Button, Event

from traitsui.api import \
    TreeEditor, TreeNode, View, Item, Group, \
    HSplit, HGroup

from figure_editor import \
    MPLFigureEditor

from matplotlib.figure import \
    Figure

from traitsui.menu import \
    Menu, MenuBar, Separator

from traitsui.wx.tree_editor import \
    DeleteAction

from tree_nodes import \
    YLPATreeNode, YLPALeafNode

from custom_tree_nodes import \
    custom_treenode_list

from tree_view_handler import \
    YLPATreeViewHandler, menu_exit, \
    menu_save, menu_open

tree_node = TreeNode(node_for=[YLPATreeNode],
                                     auto_open=True,
                                     children='tree_node_list',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(DeleteAction),  # plot_self,
                                     )

leaf_node = TreeNode(node_for=[YLPALeafNode],
                                     auto_open=True,
                                     children='',
                                     label='node_name',
                                     view='tree_view',
                                     menu=Menu(DeleteAction)  # plot_self
                                     )

tree_editor = TreeEditor(
                    nodes=custom_treenode_list + [ tree_node, leaf_node],  # custom_node_list +
                    selected='selected_node',
                    orientation='vertical'
                             )

class YLPATreeView(HasTraits):
    '''View object for a cross section state.
    '''
    root = Instance(YLPATreeNode)

    selected_node = Instance(HasTraits)

    figure = Instance(Figure)
    def _figure_default(self):
        figure = Figure(facecolor='white')
        figure.add_axes([0.08, 0.13, 0.85, 0.74])
        return figure

    data_changed = Event

    replot = Button
    def _replot_fired(self):
        self.figure.clear()
        self.selected_node.plot(self.figure)
        self.data_changed = True

    calculate = Button
    def _calculate_fired(self):
        self.figure.clear()
        self.selected_node.calculate(self.figure)
        self.data_changed = True

    clear = Button()
    def _clear_fired(self):
        self.figure.clear()
        self.data_changed = True

    view = View(HSplit(Group(Item('root',
                            editor=tree_editor,
                            resizable=True,
                            show_label=False),
                           ),
                       Group(HGroup(Item('replot', show_label=False),
                                    Item('calculate', show_label=False),
                                    Item('clear', show_label=False),
                                   ),
                             Item('figure', editor=MPLFigureEditor(),
                             resizable=True, show_label=False),
                             label='plot sheet',
                             dock='tab',
                             )
                    ),
                    id='treeview_id',
                    width=0.7,
                    height=0.4,
                    title='YLPA - Yield Line Plate Analysis',
                    resizable=True,
                    handler=YLPATreeViewHandler(),
                    menubar=MenuBar(Menu(menu_exit, Separator(),
                                         menu_save, menu_open,
                                    name='File'))
                    )

if __name__ == '__main__':

    tr = YLPATreeNode(node_name='root',
                     tree_node_list=[YLPATreeNode(node_name='subnode 1'),
                                     YLPATreeNode(node_name='subnode 2'),
                                     ])

    tv = YLPATreeView(root=tr)
    tv.configure_traits()
