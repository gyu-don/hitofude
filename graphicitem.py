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

from PyQt4 import QtGui
from PyQt4 import QtCore

class PointItem(QtGui.QGraphicsEllipseItem):
    R = 9.0

    def __init__(self, x, y):
        super().__init__(x-self.R, y-self.R, self.R*2, self.R*2)

        self._point = QtCore.QPointF(x, y)
        self._brush = QtGui.QBrush(QtCore.Qt.blue)
        self._brush_onmouse = QtGui.QBrush(QtCore.Qt.cyan)
        self.setAcceptHoverEvents(True)
        self.setBrush(self._brush)
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))

    def hoverEnterEvent(self, _):
        self.setBrush(self._brush_onmouse)
        self.update()

    def hoverLeaveEvent(self, _):
        self.setBrush(self._brush)
        self.update()

    def centerPos(self):
        return self._point


class LineItem(QtGui.QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)

        self._pen = QtGui.QPen(QtCore.Qt.red)
        self._pen.setWidth(2)
        self._pen_onmouse = QtGui.QPen(QtCore.Qt.red)
        self._pen_onmouse.setWidth(2)
        self._pen_onmouse.setStyle(QtCore.Qt.DotLine)
        self.setAcceptHoverEvents(True)
        self.setPen(self._pen)

    def hoverEnterEvent(self, _):
        self.setPen(self._pen_onmouse)
        self.update()

    def hoverLeaveEvent(self, _):
        self.setPen(self._pen)
        self.update()
