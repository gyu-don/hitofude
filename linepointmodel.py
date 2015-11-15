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

from collections import OrderedDict

from PyQt4 import QtCore

import graphicitem
import hitofude

class Lines(QtCore.QObject):
    lineAdded = QtCore.pyqtSignal(int)
    lineRemoved = QtCore.pyqtSignal(int)
    lineModified = QtCore.pyqtSignal(int)
    pointAdded = QtCore.pyqtSignal(int)
    pointRemoved = QtCore.pyqtSignal(int)
    pointModified = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self._lines = []
        self._points = OrderedDict()

    @QtCore.pyqtSlot(float, float, float, float)
    def addLine(self, x1, y1, x2, y2):
        p1 = x1, y1
        p2 = x2, y2
        if p1 == p2:
            raise ValueError('Not a line!')
        self._lines.append((p1, p2))
        for p in (p1, p2):
            if p in self._points:
                self._points[p] += 1
            else:
                self._points[p] = 1
                self.pointAdded.emit(len(self._points) - 1)
        self.lineAdded.emit(len(self._lines) - 1)

    @QtCore.pyqtSlot(int)
    def delLine(self, idx):
        #print('delLine', idx)
        #print('  pt:', self._points)
        #print('  ln:', self._lines)
        p1, p2 = self._lines[idx]
        del self._lines[idx]
        self.lineRemoved.emit(idx)
        for p in (p1, p2):
            if self._points[p] > 1:
                self._points[p] -= 1
            else:
                t = list(self._points.keys()).index(p)
                self.delPoint(t)

    def delPoint(self, idx):
        #print('delPoint', idx)
        #print('  pt:', self._points)
        #print('  ln:', self._lines)
        p = list(self._points.keys())[idx]
        i = 0
        while i < len(self._lines):
            if p in self._lines[i]:
                del self._lines[i]
                self.lineRemoved.emit(i)
            else:
                i += 1
        del self._points[p]
        self.pointRemoved.emit(idx)

    def lines(self):
        return iter(self._lines)

    def points(self):
        return iter(self._points)

    def linePointIndices(self):
        pts = list(self._points.keys())
        for p1, p2 in self._lines:
            yield pts.index(p1), pts.index(p2)

    def clear(self):
        self._lines = []
        self._points = OrderedDict()


class PointModel(QtCore.QAbstractTableModel):
    POINT_R = 5

    def __init__(self, lines, scene, parent=None):
        super().__init__(parent)

        self._lines = lines
        self._scene = scene
        self._p = list(self._lines.points())
        self._graphics = []
        for i in range(len(self._p)): self._addGraphic(i)

    def rowCount(self, _=None):
        return len(self._p)

    def columnCount(self, _=None):
        return 2

    def headerData(self, idx, orientation, role):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            return 'xy'[idx]
        else:
            return super().headerData(idx, orientation, role)

    def data(self, midx, role):
        if role == QtCore.Qt.DisplayRole:
            return self._p[midx.row()][midx.column()] 
        else:
            return None

    def _addGraphic(self, idx):
        x, y = self._p[idx]
        item = graphicitem.PointItem(x, y)
        self._graphics.insert(idx, item)
        self._scene.addItem(item)

    def _removeGraphic(self, idx):
        self._scene.removeItem(self._graphics[idx])
        del self._graphics[idx]
    
    @QtCore.pyqtSlot(int)
    def added(self, idx):
        self._p = list(self._lines.points())
        self._addGraphic(idx)
        self.rowsInserted.emit(QtCore.QModelIndex(), idx, idx)

    @QtCore.pyqtSlot(int)
    def removed(self, idx):
        self._removeGraphic(idx)
        self._p = list(self._lines.points())
        self.rowsInserted.emit(QtCore.QModelIndex(), idx, idx)

    def clear(self):
        self._p = []
        self._graphics = []
        self.reset()

    def graphic_to_index(self, item):
        return self._graphics.index(item)

class LineModel(QtCore.QAbstractTableModel):
    def __init__(self, lines, scene, parent=None):
        super().__init__(parent)

        self._lines = lines
        self._scene = scene
        self._lpi = list(self._lines.linePointIndices())
        self._ls = list(self._lines.lines())
        self._graphics = []
        for i in range(len(self._ls)): self._addGraphic(i)

    def rowCount(self, _=None):
        return len(self._lpi)

    def columnCount(self, _=None):
        return 2
    
    def headerData(self, idx, orientation, role):
        if (role == QtCore.Qt.DisplayRole and
                orientation == QtCore.Qt.Horizontal):
            return ['p1','p2'][idx]
        else:
            return super().headerData(idx, orientation, role)

    def data(self, midx, role):
        if role == QtCore.Qt.DisplayRole:
            return self._lpi[midx.row()][midx.column()] + 1
        else:
            return None

    def _addGraphic(self, idx):
        p1, p2 = self._ls[idx]
        item = graphicitem.LineItem(p1[0], p1[1], p2[0], p2[1])
        self._graphics.insert(idx, item)
        self._scene.addItem(item)

    def _removeGraphic(self, idx):
        self._scene.removeItem(self._graphics[idx])
        del self._graphics[idx]

    @QtCore.pyqtSlot(int)
    def added(self, idx):
        self._lpi = list(self._lines.linePointIndices())
        self._ls = list(self._lines.lines())
        self._addGraphic(idx)
        self.rowsInserted.emit(QtCore.QModelIndex(), idx, idx)

    @QtCore.pyqtSlot(int)
    def removed(self, idx):
        self._removeGraphic(idx)
        self._lpi = list(self._lines.linePointIndices())
        self._ls = list(self._lines.lines())
        self.rowsInserted.emit(QtCore.QModelIndex(), idx, idx)

    @QtCore.pyqtSlot()
    def updated(self):
        self._lpi = list(self._lines.linePointIndices())
        self.reset()

    def clear(self):
        self._lpi = []
        self._ls = []
        self._graphics = []
        self.reset()

    def query_solve(self):
        ans = hitofude.solve_hitofude(self._lpi)
        if ans:
            seq = [self._graphics[self._lpi.index(x)] for x in ans[1]]
            return seq
        else:
            return None

    def graphic_to_index(self, item):
        return self._graphics.index(item)
