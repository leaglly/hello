# -*- coding: utf-8 -*-

import sys
import time
import struct
import serial
from serial.tools import list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QGraphicsScene
from PyQt5.QtCore import QTimer, pyqtSignal, QThread
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from ui_mainwindow import Ui_MainWindow
from airship import AirshipUp, AirshipDown

pg.setConfigOptions(leftButtonPan=False, antialias=True, background=(240, 240, 240))

# 串口接收线程
class ReceiveThread(QThread):
	rxSignal = pyqtSignal(bytes)

	def __init__(self, ser):
		super(ReceiveThread, self).__init__()
		self._running_ = False
		self.ser = ser

	def run(self):
		while self._running_:
			data = self.ser.read(1)
			if data and data==b'\x7E':
				data = self.ser.read(1)
				if data and data==b'\x7E':
					data = self.ser.read(36)
					if data and len(data)==36:
						self.rxSignal.emit(data)
			self.usleep(10)

# 主界面
class MainWindow(QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setupUi(self)
		self.makeCenter()
		self.initUi()
		self.plotAirship()
		self.attachSignals()

	def initUi(self):
		self.statusbar.showMessage('请连接设备...')
		self.ser = serial.Serial()
		self.ser.baudrate = 115200
		self.ser.timeout = 0.5
		self.rthread = ReceiveThread(self.ser)

	def makeCenter(self):
		'''
		使主界面居中
		'''
		cp = QDesktopWidget().availableGeometry()
		self.resize(int(cp.width()*0.85), int(cp.height()*0.9))
		qr = self.frameGeometry()
		qr.moveCenter(cp.center())
		self.move(qr.topLeft())

	def plotAirship(self):
		self.sceneUp = QGraphicsScene()
		self.sceneUp.addItem(AirshipUp())
		self.upView.setScene(self.sceneUp)
		self.sceneDown = QGraphicsScene()
		self.sceneDown.addItem(AirshipDown())
		self.downView.setScene(self.sceneDown)
		
		backgroundGrid = gl.GLGridItem()
		backgroundGrid.scale(2, 2, 1)
		self.mainView.addItem(backgroundGrid)
		md = gl.MeshData.sphere(rows=10, cols=20)
		ml = gl.GLMeshItem(meshdata=md, smooth=True, color=(0, 1, 0, 1), \
			edgeColor=(0, 0, 1, 1), shader='balloon', glOptions='additive', drawEdges=True, drawFaces=False)
		ml.translate(0, 0, 0)
		ml.scale(3, 3, 1)
		self.mainView.addItem(ml)
		# self.leftPlot = self.mainGraphics.addPlot(row=0, col=0)
		# self.leftPlot.hideAxis('left')
		# self.leftPlot.hideAxis('bottom')
		# self.leftAirship = self.leftPlot.plot(x=np.sin(np.linspace(0, 2*np.pi, 1000)), y=np.cos(np.linspace(0, 6*np.pi, 1000)), pen='r')
		# self.leftRobot = pg.CurveArrow(self.leftAirship)
		# self.leftRobot.setStyle(headLen=40)
		# self.leftPlot.addItem(self.leftRobot)
		# self.anim = self.leftRobot.makeAnimation(loop=-1)

		# self.rightPlot = self.mainGraphics.addPlot(row=0, col=1)
		# self.rightPlot.hideAxis('left')
		# self.rightPlot.hideAxis('bottom')
		# self.rightAirship = self.rightPlot.plot(x=np.sin(np.linspace(0, 2*np.pi, 1000)), y=np.cos(np.linspace(0, 6*np.pi, 1000)), pen='r')
		# self.rightRobot = pg.CurveArrow(self.rightAirship)
		# self.rightRobot.setStyle(headLen=40)

	def attachSignals(self):
		self.refreshTimer = QTimer()
		self.refreshTimer.timeout.connect(self.onRefresh)
		self.refreshTimer.start(1000)
		self.rthread.rxSignal[bytes].connect(self.onReadSerial)
		self.connectAction.triggered.connect(self.onConnect1)
		self.connectButton.clicked.connect(self.onConnect)

	def onRefresh(self):
		comports = [comport.device for comport in list_ports.comports()]
		comports_old = []
		count = self.comportCombobox.count()
		for n in range(count):
			comports_old.append(self.comportCombobox.itemText(n))
		if comports!=comports_old:
			self.comportCombobox.clear()
			self.comportCombobox.addItems(comports)

	def onReadSerial(self, data):
		print(time.perf_counter())
		res = struct.unpack('<9f', data)
		# print('{0:.2f}, {1:.2f}, {2:.2f}'.format(res[0], res[1], res[2]))

	def onConnect1(self, state):
		comports = [comport.device for comport in list_ports.comports()]
		if comports==[]:
			self.statusbar.showMessage(time.strftime('%Y-%m-%d %H:%M:%S') + ': 请连接设备...')
			return

	def onConnect(self):
		comport = self.comportCombobox.currentText()
		if comport=='':
			self.statusbar.showMessage('请连接设备...')
			return
		if self.connectButton.text()=='connect':
			try:
				self.ser.port = comport
				self.ser.open()
				self.rthread._running_ = True
				self.rthread.start()
				self.comportCombobox.setEnabled(False)
				self.connectButton.setText('disconnect')
				self.statusbar.showMessage('设备已连接...')
			except Exception as e:
				self.statusbar.showMessage('设备连接失败: {0}'.format(str(e)))
		else:
			self.rthread._running_ = False
			self.rthread.quit()
			self.ser.close()
			self.comportCombobox.setEnabled(True)
			self.connectButton.setText('connect')
			self.statusbar.showMessage('设备已关闭...')


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()
	sys.exit(app.exec_())
