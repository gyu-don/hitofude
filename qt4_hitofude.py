'''Copyright (C) 2015 gyu-don

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
'''

import sys

from PyQt4 import QtGui
from PyQt4 import QtCore
import PyQt4.uic

import resource_rc

from linepointmodel import *
from graphicitem import *

class HitofudeWidget(QtGui.QMainWindow):
    UI_NAME = 'qt_hitofude.ui'
    MODE_DRAW = 1
    MODE_REMOVE = 2
    MODE_SOLVE = 3

    modeChanged = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.ui = PyQt4.uic.loadUi(self.UI_NAME, self)
        self.setWindowTitle('Hitofude gaki')

        actgrp = QtGui.QActionGroup(self)
        actgrp.addAction(self.ui.actionDraw)
        actgrp.addAction(self.ui.actionRemove)
        actgrp.addAction(self.ui.actionSolve)

        self.lines = Lines()

        self._setup_scene()
        self._setup_modelview()

        self.scene.setMode(self.MODE_DRAW)

    def _setup_scene(self):
        self.scene = Scene()
        self.scene.setMode(self.MODE_DRAW)
        self.ui.graphicsView.setScene(self.scene)
        self.scene.addLineRequest.connect(self.lines.addLine)
        self.scene.delLineRequest.connect(self.delLine)
        self.scene.delPointRequest.connect(self.delPoint)
        self.modeChanged.connect(self.scene.setMode)

    def _setup_modelview(self):
        self.ptmodel = PointModel(self.lines, self.scene)
        self.ui.pointView.setModel(self.ptmodel)
        self.ui.pointView.horizontalHeader().show()
        self.ui.pointView.verticalHeader().show()

        self.linemodel = LineModel(self.lines, self.scene)
        self.ui.lineView.setModel(self.linemodel)
        self.ui.lineView.horizontalHeader().show()
        self.ui.lineView.verticalHeader().show()

        self.lines.lineAdded.connect(self.linemodel.added)
        self.lines.lineRemoved.connect(self.linemodel.removed)
        self.lines.pointAdded.connect(self.ptmodel.added)
        self.lines.pointRemoved.connect(self.ptmodel.removed)
        self.lines.pointRemoved.connect(self.linemodel.updated)

    @QtCore.pyqtSlot(bool)
    def on_actionDraw_triggered(self, b):
        self.mode = self.MODE_DRAW
        self.modeChanged.emit(self.mode)

    @QtCore.pyqtSlot(bool)
    def on_actionRemove_triggered(self, b):
        self.mode = self.MODE_REMOVE
        self.modeChanged.emit(self.mode)

    @QtCore.pyqtSlot(bool)
    def on_actionSolve_triggered(self, b):
        self.mode = self.MODE_SOLVE
        if len(list(self.lines.lines())):
            ans = self.linemodel.query_solve()
        else:
            ans = None

        if ans:
            self.scene.setanimation(ans)
        else:
            self.scene.setanimation([])
            QtGui.QMessageBox.information(self, None, 'No answer!')
        self.modeChanged.emit(self.mode)

    @QtCore.pyqtSlot()
    def on_actionClear_triggered(self):
        self.lines.clear()
        self.ptmodel.clear()
        self.linemodel.clear()
        self.scene.clear()

    @QtCore.pyqtSlot(graphicitem.LineItem)
    def delLine(self, item):
        self.lines.delLine(self.linemodel.graphic_to_index(item))

    @QtCore.pyqtSlot(graphicitem.PointItem)
    def delPoint(self, item):
        self.lines.delPoint(self.ptmodel.graphic_to_index(item))

class Scene(QtGui.QGraphicsScene):
    addLineRequest = QtCore.pyqtSignal(float, float, float, float)
    delLineRequest = QtCore.pyqtSignal(graphicitem.LineItem)
    delPointRequest = QtCore.pyqtSignal(graphicitem.PointItem)

    def __init__(self):
        super().__init__()
        self._mode = None

        self._line_start = None
        self._line_mousetracking = QtGui.QGraphicsLineItem(0,0,0,0)
        self._line_mousetracking.setPen(QtCore.Qt.magenta)

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.next_animation)
        self._timer.start(200)

        self._animation = False
        self._animationseq = []
        self._animationnext = 0

    def mousePressEvent(self, ev):
        item = self.itemAt(ev.scenePos())
        if item is None:
            pos = ev.scenePos()
        elif isinstance(item, graphicitem.PointItem):
            pos = item.centerPos()
        else:
            pos = None

        if self._mode == HitofudeWidget.MODE_DRAW:
            if self._line_start:
                if pos and pos != self._line_start:
                    self.addLineRequest.emit(
                            self._line_start.x(), self._line_start.y(),
                            pos.x(), pos.y())
                self._line_start = None
                self.removeItem(self._line_mousetracking)
            else:
                if pos:
                    self._line_start = pos
                    self._line_mousetracking.setLine(
                            pos.x(), pos.y(), pos.x(), pos.y())
                    self.addItem(self._line_mousetracking)
        elif self._mode == HitofudeWidget.MODE_REMOVE:
            if isinstance(item, graphicitem.LineItem):
                self.delLineRequest.emit(item)
            elif isinstance(item, graphicitem.PointItem):
                self.delPointRequest.emit(item)
        return super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._line_start:
            self._line_mousetracking.setLine(
                    self._line_start.x(), self._line_start.y(),
                    ev.scenePos().x(), ev.scenePos().y())
        return super().mouseMoveEvent(ev)

    @QtCore.pyqtSlot(int)
    def setMode(self, mode):
        self._mode = mode
        if self._line_start:
            self._line_start = None
            self.removeItem(self._line_mousetracking)
        if mode == HitofudeWidget.MODE_SOLVE:
            self._animation = True
        if self._animation and mode != HitofudeWidget.MODE_SOLVE:
            self.stopAnimation()

    def setanimation(self, seq):
        self._animationseq = seq
        self._animationnext = len(seq)

    def stopAnimation(self):
        self._animation = False
        for item in self._animationseq:
            item.show()
        self._animationseq = []

    @QtCore.pyqtSlot()
    def next_animation(self):
        if self._animation:
            if self._animationnext < len(self._animationseq):
                self._animationseq[self._animationnext].show()
                self._animationnext += 1
            else:
                for item in self._animationseq:
                    item.hide()
                self._animationnext = 0

    def clear(self):
        self._animationseq = []
        super().clear()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = HitofudeWidget()
    w.show()

    sys.exit(app.exec_())
