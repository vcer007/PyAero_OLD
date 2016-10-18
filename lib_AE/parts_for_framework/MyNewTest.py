#!d:/python27/python -u

import sys
from PyQt4 import QtGui, QtCore

class GraphicsItem(QtGui.QGraphicsItem):
    """
     From the QT docs:
     To write your own graphics item, you first create a subclass
     of QGraphicsItem, and then start by implementing its two pure 
     virtual public functions: boundingRect(), which returns an estimate
     of the area painted by the item, and paint(), 
     which implements the actual painting.
    """
    # call constructor of GraphicsItem
    def __init__(self, rect, brush=QtGui.QBrush(QtCore.Qt.red), tooltip=None, parent=None):
        # call constructor of QtGui.QGraphicsItem (syntax for new style classes; inherited from "object")
        super(GraphicsItem, self).__init__()

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)

        self.setAcceptsHoverEvents(True)

        self.pen = QtGui.QPen(QtCore.Qt.SolidLine)
        self.pen.setColor(QtCore.Qt.blue)
        self.penwidth = 8
        self.pen.setWidth(self.penwidth)
        self.brush = brush
        self.setToolTip(tooltip)
        self.parent = parent
        
        self.rect = QtCore.QRectF(rect[0], rect[1], rect[2], rect[3])
        self.focusrect = QtCore.QRectF(rect[0]-self.penwidth/2,
                rect[1]-self.penwidth/2, rect[2]+self.penwidth, rect[3]+self.penwidth)

    def mouseMoveEvent(self, event):
        # move object
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        print 'from GraphicsItem'
        # select object
        QtGui.QGraphicsItem.mousePressEvent(self, event)
        # set item as topmost in stack
        self.setZValue(self.parent.scene.items()[0].zValue() + 1)
        self.setSelected(True)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)
        if self.isSelected():
            self.drawFocusRect(painter)

    def drawFocusRect(self, painter):
        self.focusbrush = QtGui.QBrush()
        self.focuspen = QtGui.QPen(QtCore.Qt.DotLine)
        self.focuspen.setColor(QtCore.Qt.black)
        self.focuspen.setWidth(2)
        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)
        painter.drawRect(self.focusrect)

    def hoverEnterEvent(self, event):
        # set item as topmost in stack
        #self.setZValue(self.parent.scene.items()[0].zValue() + 1)
        pass

    def hoverLeaveEvent(self, event):
        pass


class MyMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

        width = 1000
        height = 800
        self.scene = QtGui.QGraphicsScene(-width/2, -height/2, width, height)

        self.graphicsItem = GraphicsItem((-100, -100, 200, 200),
                QtGui.QBrush(QtCore.Qt.red), 'My first item', self)
        self.scene.addItem(self.graphicsItem)
        self.graphicsItem1 = GraphicsItem((100, 100, 200, 200),
                QtGui.QBrush(QtCore.Qt.yellow), 'My second item', self)
        self.scene.addItem(self.graphicsItem1)
        self.graphicsItem2 = GraphicsItem((0, 150, 250, 250),
                QtGui.QBrush(QtCore.Qt.green), 'My third item', self)
        self.scene.addItem(self.graphicsItem2)

        self.view = QtGui.QGraphicsView()
         # set QGraphicsView attributes
        self.view.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.HighQualityAntialiasing)
        self.view.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

    def mousePressEvent(self, event):
        print 'from MainWindow'

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Escape:
            sys.exit(QtGui.qApp.quit())
        else:
            super(GraphicsView, self).keyPressEvent(event)

def main():
    app = QtGui.QApplication(sys.argv)
    form = MyMainWindow()
    form.setGeometry(700, 100, 1050, 850)
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
