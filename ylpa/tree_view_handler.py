'''
Created on 30. 1. 2015

@author: Kapsak
'''

from traitsui.api import \
    View, Item, Group, HGroup, Handler, \
    UIInfo, spring

from traitsui.menu import \
    Action

from traitsui.file_dialog import \
    open_file, save_file

from traits.api import \
    Button, Instance, WeakRef, HasTraits

from file_handler import \
    get_outfile

import pickle

plot_self = Action(name='Plot', action='plot_node')
'''Context menu action for plotting tree nodes
'''
calc_self = Action(name='Calculate', action='calc_node')
'''Context menu action for calculation and subsequent plotting
'''
menu_save = Action(name='Save', action='menu_save')
'''Menubar action for saving the root node to file
'''
menu_open = Action(name='Open', action='menu_open')
'''Menubar action for loading root node from file
'''
menu_exit = Action(name='Exit', action='menu_exit')
'''Menubar action for terminating the view
'''

class YLPATreeViewHandler(Handler):
    '''Handler for MxNTreeView class
    '''
    # The UIInfo object associated with the view:
    info = Instance(UIInfo)
    node = WeakRef

    ok = Button('OK')
    cancel = Button('Cancel')
    exit_dialog = ('Do you really wish to end '
                   'the session? Any unsaved data '
                   'will be lost.')

    exit_view = View(Item(name='', label=exit_dialog),
                     HGroup(Item('ok', show_label=False, springy=True),
                            Item('cancel', show_label=False, springy=True)
                            ),
                     title='Exit dialog',
                     kind='live'
                     )

    def plot_node(self, info, node):
        '''Handles context menu action Plot for tree nodes
        '''
        info.object.figure.clear()
        node.plot(info.object.figure)
        info.object.data_changed = True

    def calc_node(self, info, node):
        '''Handles context menu action Plot for tree nodes
        '''
        info.object.figure.clear()
        node.calculate(info.object.figure)
        info.object.data_changed = True

    def menu_save(self, info):
        file_name = get_outfile(folder_name='.ylpa', file_name='')
        file_ = save_file(file_name=file_name)
        if file_:
            pickle.dump(info.object.root, open(file_, 'wb'), 1)

    def menu_open(self, info):
        file_name = get_outfile(folder_name='.ylpa', file_name='')
        file_ = open_file(file_name=file_name)
        if file_:
            info.object.root = pickle.load(open(file_, 'rb'))

    def menu_exit(self, info):
        if info.initialized:
            self.info = info
            self._ui = self.edit_traits(view='exit_view')

    def _ok_fired (self):
        self._ui.dispose()
        self.info.ui.dispose()

    def _cancel_fired (self):
        self._ui.dispose()
