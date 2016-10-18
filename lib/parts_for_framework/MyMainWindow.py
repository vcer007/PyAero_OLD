#!d:/python27/python -u

import sys
import math
from PyQt4 import QtGui, QtCore

class MyMainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MyMainWindow, self).__init__()
        
        self.initUI()

    def initUI(self):               
  
        # window size, position and title
        self.setGeometry(700, 100, 1200, 900)
        self.setWindowTitle('Airfoil Mesher')    
        self.show()

        scene = self.GraphicsScene()
        view = self.GraphicsView()
        view.setScene(self.scene)

        # Central Widget
        self.setCentralWidget(CentralWidget(self))


class GraphicsScene(QtGui.QGraphicsScene):
    def __init__(self):
        super(GraphicsScene, self).__init__(parent)

class GraphicsView(QtGui.QGraphicsView):
    def __init__(self):
        super(GraphicsView, self).__init__(parent)

        # set QGraphicsView attributes
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                QtGui.QPainter.SmoothPixmapTransform)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        # allow dragging, but set cursor to normal (arrow)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        # hide scrollbars
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self._isPanning = False
        self._mousePressed = False

        # setup scene
        self.scene = GraphicsScene()

        # pen and brush style
        pen = QtGui.QPen(QtCore.Qt.black, 6, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.MiterJoin)
        brush = QtGui.QBrush(QtCore.Qt.red)

        self.rect = self.scene.addRect(50, 50, 300, 200, pen, brush)

        # set scene rect so that all my objects always scroll
        self.width = 100000
        self.height = 100000
        self.scene.setSceneRect(-self.width/2, -self.height/2, self.width, self.height)

        # set background style
        self.canvasstyle = \
            'background-color:QLinearGradient(  \
            x1: 0.0, y1: 0.0, x2: 0.0, y2: 1.0,  \
            stop: 0.3 white,  \
            stop: 1.0 blue); \
            '
        self.setStyleSheet(self.canvasstyle)

        # invert y-coordinates for cartesian coordinate system
        self.scale(1, -1)

        self.setScene(self.scene)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mousePressed = True
            if self._isPanning:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
                self._dragPos = event.pos()
                event.accept()
        super(GraphicsView, self).mousePressEvent(event)            

    def mouseReleaseEvent(self, event):
        self._mousePressed = False
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.viewport().update()
        super(GraphicsView, self).mouseReleaseEvent(event)            

    def mouseMoveEvent(self, event):
        if self._mousePressed and self._isPanning:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
            event.accept()
        else:
            super(GraphicsView, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Control and not self._mousePressed:
            self._isPanning = True
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        elif key == QtCore.Qt.Key_Escape:
            sys.exit(QtGui.qApp.quit())
        else:
            super(GraphicsView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Control and not self._mousePressed:
            self._isPanning = False
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        else:
            super(GraphicsView, self).keyPressEvent(event)


app = QtGui.QApplication(sys.argv)
ex = MyMainWindow()
sys.exit(app.exec_())
