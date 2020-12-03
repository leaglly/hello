# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QGraphicsObject
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor


class AirshipUp(QGraphicsObject):
	def __init__(self, parent=None):
		super(AirshipUp, self).__init__(parent)
		self.color = QColor(Qt.lightGray)

	def boundingRect(self):
		return QRectF(0, 0, 600, 250)

	def paint(self, painter, option, widget=None):
		painter.setBrush(self.color)
		painter.drawEllipse(0, 0, 600, 250)


class AirshipDown(QGraphicsObject):
	def __init__(self, parent=None):
		super(AirshipDown, self).__init__(parent)
		self.color = QColor(Qt.lightGray)

	def boundingRect(self):
		return QRectF(0, 0, 600, 250)

	def paint(self, painter, option, widget=None):
		painter.setBrush(self.color)
		painter.drawEllipse(0, 0, 600, 250)