# Author: Trevor Barrus

import sys
import os
import traceback
from PyQt4 import QtGui, QtCore
from byuam.project import Project
from byuam.environment import Environment, Department, Status

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
    
class PublishWindow(QtGui.QWidget):

    finished = QtCore.pyqtSignal()

    def __init__(self, src, parent, dept_list=Department.ALL):
        super(PublishWindow, self).__init__()
        self.environment = Environment()
        self.project = Project()
        self.eList = ElementList(self)
        self.parent = parent
        self.src = src
        self.result = None
        self.elementType = None
        self.initUI(dept_list)
        self.published = False
        
    def initUI(self, dept_list):
        #load checkout information
        src_dir = os.path.dirname(self.src)
        checkout_element = self.project.get_checkout_element(src_dir)
        checkout_dept = None
        checkout_body_name = None
        if checkout_element is not None:
            checkout_dept = checkout_element.get_department()
            checkout_body_name = checkout_element.get_parent()

        #define gui elements
        self.setGeometry(300,300,WINDOW_WIDTH,WINDOW_HEIGHT)
        self.setWindowTitle('Publish')
        self.menu = QtGui.QComboBox()
        self.menu.addItem('Asset')
        self.menu.addItem('Shot')
        self.departmentMenu = QtGui.QComboBox()
        checkout_idx = -1
        for i, dept in enumerate(dept_list):
            self.departmentMenu.addItem(dept)
            if dept==checkout_dept:
                checkout_idx = i
        
        self.departmentMenu.activated[str].connect(self.setElementType)
        self.filePath = QtGui.QLineEdit()
        self.filePath.setReadOnly(True)
        self.label = QtGui.QLabel('What did you change?')
        self.comment = QtGui.QTextEdit()
        self.publishBtn = QtGui.QPushButton('Publish')
        self.publishBtn.setEnabled(False)
        
        self.eList.currentItemChanged.connect(self.selectElement)
        self.publishBtn.clicked.connect(self.publish)

        if checkout_idx>-1:
            self.departmentMenu.setCurrentIndex(checkout_idx)
        self.setElementType()
        self.eList.setElement(checkout_body_name)
        
        #set gui layout
        self.grid = QtGui.QGridLayout(self)
        self.setLayout(self.grid)
        self.grid.addWidget(self.departmentMenu, 0, 0)
        self.grid.addWidget(self.label, 1, 1)
        self.grid.addWidget(self.eList, 2, 0)
        self.grid.addWidget(self.comment, 2, 1)
        self.grid.addWidget(self.filePath, 3, 0)
        self.grid.addWidget(self.publishBtn, 3, 1)
        
        self.show()
        
    def setElementType(self):
        department = str(self.departmentMenu.currentText())
        if department in Department.FRONTEND:
            self.elementType = 'Asset'
        else:
            self.elementType = 'Shot'
        self.eList.refreshList(self.elementType)
        
    def selectElement(self):
        currentItem = self.eList.currentItem()
        if currentItem is not None:
           self.filePath.setText(self.eList.currentItem().text())
           self.publishBtn.setEnabled(True)

    def publish(self):
        self.elementType = str(self.menu.currentText())
        try:
            body = self.project.get_body(str(self.filePath.text()))
            element = body.get_element(str(self.departmentMenu.currentText()))
        
            self.user = self.environment.get_current_username()
            self.comment = str(self.comment.toPlainText())
            self.result = element
            self.published = True
            self.close()
        except Exception, e:
            print e
            error = QtGui.QLineEdit()
            error.setText(str(e))
            self.grid.addWidget(error, 4, 1, 2, 1)
            traceback.print_stack()

    def closeEvent(self, event):
        self.finished.emit()
        event.accept()
        
class ElementList(QtGui.QListWidget):
    def __init__(self, parent):
        super(ElementList, self).__init__()
        self.parent = parent
        self.project = Project()
        self.elements = self.project.list_assets()
        self.initUI()       
        
    def initUI(self):
        #define gui elements
        self.refreshList('Asset')
            
    #Update the list based on the input element type
    def refreshList(self, element):
        if element == 'Asset':
            self.elements = self.project.list_assets()
        else:
            self.elements = self.project.list_shots()
            
        self.clear()
        for e in self.elements:
            self.addItem(e)

    def setElement(self, element):
        for idx in xrange(self.count()):
            eItem = self.item(idx)
            if str(eItem.text())==element:
                self.setCurrentRow(idx)
                break
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = PublishWindow(os.environ['BYU_TOOLS_DIR'] + '/byu_gui/test.txt', app)
    sys.exit(app.exec_())
