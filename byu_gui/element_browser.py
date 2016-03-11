from PyQt4 import QtGui, QtCore

import os

from byuam.body import Asset, Shot
from byuam.environment import AssetType, Department, Status
from byuam.project import Project

REF_WINDOW_WIDTH = 800
REF_WINDOW_HEIGHT = 500

class TreeComboBoxItem(QtGui.QComboBox):

    def __init__(self, tree_item, column):
        QtGui.QComboBox.__init__(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tree_item = tree_item
        self.column = column
        self.currentIndexChanged.connect(self._change_item)
        
    def _change_item(self, index):
        self.tree_item.setText(self.column, self.itemText(index))

    def wheelEvent(self, e):
        e.ignore() # do nothing

    def paintEvent(self, pe):
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        pen.setColor
        painter.setPen(pen)
        painter.drawRect(pe.rect())
        painter.end()
        
        QtGui.QComboBox.paintEvent(self, pe)

class TreeLineEdit(QtGui.QLineEdit):

    def __init__(self, contents, tree_item, column):
        QtGui.QLineEdit.__init__(self, contents)
        self.tree_item = tree_item
        self.column = column
        self.editingFinished.connect(self._change_item)

    def _change_item(self):
        self.tree_item.setText(self.column, self.text())

    def paintEvent(self, pe):
        painter = QtGui.QPainter()
        painter.begin(self)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        pen.setColor
        painter.setPen(pen)
        painter.drawRect(pe.rect())
        painter.end()
        
        QtGui.QLineEdit.paintEvent(self, pe)

class TreeLabel(QtGui.QLabel):

    def __init__(self, text=""):
        QtGui.QLabel.__init__(self, text)
        self.setAutoFillBackground(True)
    
    def paintEvent(self, pe):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QColor(30,30,30))
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        pen.setColor
        painter.setPen(pen)
        painter.drawRect(pe.rect())
        painter.end()
        
        QtGui.QLabel.paintEvent(self, pe)

class TreeGridDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        painter.save()
        # painter.setPen(option.palette.color(QtGui.QPalette.Text))
        painter.setPen(QtCore.Qt.black)
        painter.drawRect(option.rect)
        painter.restore()

        QtGui.QStyledItemDelegate.paint(self, painter, option, index)

class ElementBrowser(QtGui.QWidget):

    ASSETS = "Assets"
    SHOTS = "Shots"

    BODY_DATA_COLUMN = 1

    stylesheet = """
    QWidget
    {
        color: silver;
        background-color: #2E2E2E;
        selection-color: black;
        background-clip: border;
        border-image: none;
        outline: 0;
    }
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("Element Browser")
        self.setGeometry(0, 0, REF_WINDOW_WIDTH, REF_WINDOW_HEIGHT)
        self.setStyleSheet(self.stylesheet)

        # initialize project
        self.project = Project()
        self.userList = ["jmoborn", "render", "steve", "jmjohnson", "stella"] # TODO: get real user list

        # asset/shot menu
        self.body_menu = QtGui.QComboBox()
        self.body_menu.addItem(self.ASSETS)
        self.body_menu.addItem(self.SHOTS)
        self.current_body = self.ASSETS
        self._set_bodies()

        # new button
        self.new_button = QtGui.QPushButton("New")

        # refresh button
        self.refresh_button = QtGui.QPushButton("Refresh")

        # tree
        self.tree = QtGui.QTreeWidget()
        self.tree.setItemDelegate(TreeGridDelegate(self.tree))
        self.columnCount = 7
        self.tree.setColumnCount(self.columnCount)
        tree_header = QtGui.QTreeWidgetItem(["name", "", "assigned", "status", "start", "end", "publish"])
        self.tree.setHeaderItem(tree_header)

        self.init_tree = [None]*self.columnCount
        self.init_tree[0] = self.init_name
        self.init_tree[1] = self.init_dept
        self.init_tree[2] = self.init_assigned_user
        self.init_tree[3] = self.init_status
        self.init_tree[4] = self.init_start_date
        self.init_tree[5] = self.init_end_date
        self.init_tree[6] = self.init_last_publish

        self._build_tree()

        self.update_tree = [None]*self.columnCount
        self.update_tree[0] = self.update_name
        self.update_tree[1] = self.update_dept
        self.update_tree[2] = self.update_assigned_user
        self.update_tree[3] = self.update_status
        self.update_tree[4] = self.update_start_date
        self.update_tree[5] = self.update_end_date
        self.update_tree[6] = self.update_last_publish

        # status bar
        self.status_bar = QtGui.QStatusBar()

        # connect events
        self.body_menu.currentIndexChanged.connect(self._body_changed)
        self.new_button.clicked.connect(self._new_body)
        self.refresh_button.clicked.connect(self._refresh)
        self.tree.itemExpanded.connect(self._load_elements)
        self.tree.itemChanged.connect(self._item_edited)

        # layout
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setMargin(6)
        options_layout = QtGui.QGridLayout()
        options_layout.addWidget(self.body_menu, 0, 0)
        options_layout.addWidget(self.new_button, 0, 1)
        options_layout.addWidget(self.refresh_button, 0, 3)
        options_layout.setColumnMinimumWidth(0, 100)
        options_layout.setColumnMinimumWidth(1, 100)
        options_layout.setColumnMinimumWidth(3, 100)
        options_layout.setColumnStretch(2, 1)
        layout.addLayout(options_layout)
        layout.addWidget(self.tree)
        layout.addWidget(self.status_bar)
        self.setLayout(layout)

    def _build_tree(self):
        self.tree.clear()
        tree_state = self.tree.blockSignals(True)
        for body in self.bodies:
            tree_item = QtGui.QTreeWidgetItem([body])
            self.tree.addTopLevelItem(tree_item)
            tree_flags = tree_item.flags()
            tree_item.setFlags(tree_flags | QtCore.Qt.ItemIsEditable)
            # for col in xrange(self.columnCount):
            #     tree_item.setBackground(col, QtGui.QColor(30,30,30))
            body_obj = self.project.get_body(body)
            self._load_body(body_obj, tree_item)
            tree_item.addChild(QtGui.QTreeWidgetItem()) # empty item
        self.tree.blockSignals(tree_state)

    def _load_body(self, body, item):
        tree_state = self.tree.blockSignals(True)
        item.setText(0, body.get_name())
        namelabel = TreeLabel(body.get_name())
        self.tree.setItemWidget(item, 0, namelabel)
        if self.current_body==self.ASSETS:
            body_type = body.get_type()
            item.setText(self.BODY_DATA_COLUMN, body_type)
            combobox = TreeComboBoxItem(item, self.BODY_DATA_COLUMN)
            type_idx = 0
            for idx, type in enumerate(AssetType.ALL):
                combobox.addItem(type)
                if type == body_type:
                    type_idx = idx
            combobox.setCurrentIndex(type_idx)
            self.tree.setItemWidget(item, self.BODY_DATA_COLUMN, combobox)
        elif self.current_body==self.SHOTS:
            item.setText(1, str(body.get_frame_range()))
        else:
            self.status_bar.showMessage("Error: unknown body type")
        for col in xrange(self.BODY_DATA_COLUMN+1, self.columnCount): # disable remaining columns
            emptylabel = TreeLabel()
            self.tree.setItemWidget(item, col, emptylabel)
        self.tree.blockSignals(tree_state)

    def _load_elements(self, item):
        tree_state = self.tree.blockSignals(True)
        body = str(item.text(0))
        body_obj = self.project.get_body(body)
        elements = []
        for dept in Department.ALL:
            dept_elements = body_obj.list_elements(dept)
            for dept_element in dept_elements:
                elements.append((dept, dept_element))
        item.takeChildren() # clear children
        for dept, element in elements:
            element_obj = body_obj.get_element(dept, element)
            child_item = QtGui.QTreeWidgetItem()
            item.addChild(child_item)
            child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsEditable)
            for col, init in enumerate(self.init_tree):
                init(element_obj, child_item, col)
        self.tree.blockSignals(tree_state)

    def _set_bodies(self):
        if self.current_body == self.ASSETS:
            self.bodies = self.project.list_assets()
        elif self.current_body == self.SHOTS:
            self.bodies = self.project.list_shots()
        else:
            self.bodies = []

    def _item_edited(self, item, column):
        parent = item.parent()
        if parent is not None:
            body = str(parent.text(0))
            body_obj = self.project.get_body(body)
            element = str(item.text(0))
            dept = str(item.text(1))
            element_obj = body_obj.get_element(dept, element)
            self.update_tree[column](element_obj, item, column)
            # self.tree.resizeColumnToContents(column)
        else:
            body = str(item.text(0))
            body_obj = self.project.get_body(body)
            self._update_body_data(body_obj, item)

    def _refresh(self): # TODO: maintain expanded rows on refresh
        self._set_bodies()
        self._build_tree()
        self.status_bar.clearMessage()

    def _body_changed(self, index):
        self.current_body = str(self.body_menu.itemText(index))
        self._refresh()

    def _new_body(self):
        from byu_gui import new_asset_gui
        self.new_body_dialog = new_asset_gui.createWindow()
        if self.current_body == self.ASSETS:
            self.new_body_dialog.setCurrentIndex(self.new_body_dialog.ASSET_INDEX)
        elif self.current_body == self.SHOTS:
            self.new_body_dialog.setCurrentIndex(self.new_body_dialog.SHOT_INDEX)
        self.new_body_dialog.finished.connect(self._refresh)

    def _update_body_data(self, body, item):
        if self.current_body==self.ASSETS:
            body.update_type(str(item.text(self.BODY_DATA_COLUMN)))
        elif self.current_body==self.SHOTS:
            body.update_frame_range(int(item.text(self.BODY_DATA_COLUMN)))
        else:
            self.status_bar.showMessage("Error: unknown body type")

    def init_name(self, element, item, column):
        item.setText(column, element.get_name())
        namelabel = TreeLabel(element.get_name())
        self.tree.setItemWidget(item, column, namelabel)

    def init_dept(self, element, item, column):
        item.setText(column, element.get_department())
        deptlabel = TreeLabel(element.get_department())
        self.tree.setItemWidget(item, column, deptlabel)

    def init_assigned_user(self, element, item, column):
        user = element.get_assigned_user()
        item.setText(column, user)
        lineedit = TreeLineEdit(user, item, column)
        userCompleter = QtGui.QCompleter(self.userList)
        lineedit.setCompleter(userCompleter)
        self.tree.setItemWidget(item, column, lineedit)

    def init_status(self, element, item, column):
        item.setText(column, element.get_status())
        combobox = TreeComboBoxItem(item, column)
        element_type = element.get_status()
        type_idx = 0
        for idx, type in enumerate(Status.ALL):
            combobox.addItem(type)
            if type == element_type:
                type_idx = idx
        combobox.setCurrentIndex(type_idx)
        self.tree.setItemWidget(item, column, combobox)

    def init_start_date(self, element, item, column):
        item.setText(column, element.get_start_date())

    def init_end_date(self, element, item, column):
        item.setText(column, element.get_end_date())

    def init_last_publish(self, element, item, column):
        publish = element.get_last_publish()
        if publish is not None:
            item.setText(column, publish[0]+", "+publish[1]+", "+publish[2])
        else:
            item.setText(column, "")

    def update_name(self, element, item, column):
        self.status_bar.showMessage("can't change name")

    def update_dept(self, element, item, column):
        self.status_bar.showMessage("can't change department")

    def update_assigned_user(self, element, item, column):
        user = str(item.text(column))
        if user in self.userList:
            element.update_assigned_user(user)
            self.status_bar.clearMessage()
        else:
            # item.setText(column, element.get_assigned_user())
            self.tree.itemWidget(item, column).setText(element.get_assigned_user())
            self.status_bar.showMessage('"' + user + '" is not a valid user')

    def update_status(self, element, item, column):
        element.update_status(str(item.text(column)))
        self.status_bar.clearMessage()

    def update_start_date(self, element, item, column):
        # TODO: check for valid date
        element.update_start_date(str(item.text(column)))

    def update_end_date(self, element, item, column):
        # TODO: check for valid date
        element.update_end_date(str(item.text(column)))

    def update_last_publish(self, element, item, column):
        self.status_bar.showMessage("can't modify publish data")
        self.init_last_publish(element, item, column)

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = ElementBrowser()
    window.show()
    sys.exit(app.exec_())