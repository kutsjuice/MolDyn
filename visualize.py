# -*- coding: utf-8 -*-
"""
Created on Sat May  2 16:44:53 2020

@author: Mikhail Kuts
"""

import sys

from PySide2.QtCore import Qt, QSize, QObject, QTimer, Slot, QDir
from PySide2.QtGui import QScreen, QVector3D
from PySide2.QtWidgets import QApplication, QSizePolicy, QMainWindow, QWidget, \
    QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QMessageBox, QAction, QFileDialog
from PySide2.QtDataVisualization import QtDataVisualization

import numpy as np
from math import tau

class SimulatedSystem(object):
    def __init__(self, data):
        self._current_state = 0
        self._particles = data["particles"]
        self._box_width = data["box_width"]
        self._steps_num = data["steps_num"]
        self._time_step = data["time_step"]
        self._trajectory = data["mol_traj"]

    def getBoxWidth(self):
        return self._box_width
    
    def getTimeStep(self):
        return self._time_step
    
    def makeStep(self):
        if self._current_state < self._steps_num:
            self._current_state += 1
        else:
            self._current_state = 0
    def getCurrentCoordinates(self):
        return self._trajectory[:,:,self._current_state]
        
class ScatterDataMofifier(QObject):
    def __init__(self, scatter, s_data):
        self.scatter = scatter
        self._s_data = s_data
        self.timer = QTimer()
        
        self.series = QtDataVisualization.QScatter3DSeries()
        self.data = [QVector3D(0.5, 0.5, 0.5), QVector3D(-0.3, -0.5, -0.4), QVector3D(0.0, -0.3, 0.2)]
        self.series.dataProxy().addItems(self.data)
        self.series.setItemSize(0.5)
        self.series.setMeshSmooth(True)
 
        self.scatter.addSeries(self.series)
        self.scatter.setAspectRatio(1.0)
        self.scatter.setHorizontalAspectRatio(1.0)
        
        # Setting of plot limits
        self.scatter.axisX().setRange(0,s_data.getBoxWidth())
        self.scatter.axisY().setRange(0,s_data.getBoxWidth())
        self.scatter.axisZ().setRange(0,s_data.getBoxWidth())
        
        self._time_step = s_data.getTimeStep()*1000
        self.timer.timeout.connect(self.makeStep)
        # Drowing of the data and starting of the timer
        self.drawData()
        self.timer.start(self._time_step)
        
    def drawData(self):
        data = []
        for mol in self._s_data.getCurrentCoordinates():
            data.append(QVector3D(*mol[:3]))
        self.series.dataProxy().removeItems(0,len(data))
        self.series.dataProxy().addItems(data)

    def makeStep(self):
        self._s_data.makeStep()
        self.drawData()
    
    def toggleStopAnimate(self):
        if (self.timer.isActive()):
            self.timer.stop()
        else:
            self.timer.start(self._time_step)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("Molecular dynamics visualization")
        self.scatter = QtDataVisualization.Q3DScatter()
        self.container = QWidget.createWindowContainer(self.scatter)
        self.scatter.setAspectRatio(1.0)
        self.scatter.setHorizontalAspectRatio(1.0)
        
        # Setting of plot limits
        self.scatter.axisX().setRange(0.0,1.0)
        self.scatter.axisY().setRange(0.0,1.0)
        self.scatter.axisZ().setRange(0.0,1.0)
        
        if (not self.scatter.hasContext()):
            msgBox = QMessageBox()
            msgBox.setText("Couldn't initialze the OpenGL context.")
            msgBox.exec()
            sys.exit(-1)
            
        screenSize = self.scatter.screen().size()
        self.container.setMinimumSize(QSize(screenSize.width() / 2.0, screenSize.height() / 1.5))
        self.container.setMaximumSize(screenSize)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setFocusPolicy(Qt.StrongFocus)

        self.setCentralWidget(self.container)
        
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        
        self.open_action = QAction("Open file", self)
        self.open_action.setShortcut("Ctrl+O")
        self.quit_action = QAction("Quit", self)
        self.quit_action.setShortcut("Ctrl+Q")
        
        self.file_menu.addAction(self.open_action)
        self.open_action.triggered.connect(self.openFileDialog)
        self.file_menu.addAction(self.quit_action)
        self.quit_action.triggered.connect(self.exit_app)
        
    @Slot()
    def exit_app(self, checked):
        QApplication.instance().quit()
    @Slot()
    def openFileDialog(self):
        file_path = QFileDialog.getOpenFileName(self, "Find Files", QDir.currentPath())[0]
        file = open(file_path,"r")
        particles = int(file.readline())
        box_width = float(file.readline())
        steps_num = int(file.readline())
        time_step = float(file.readline())
        system_par = {"particles": particles,
              "box_width": box_width,
              "steps_num": steps_num,
              "time_step": time_step}
        system = np.zeros([particles,6,steps_num])
        for j in range(steps_num):
            file.readline()
            for i in range(particles):
                line = file.readline()
                system[i,:,j] = np.fromstring(line,sep = " ")
        system_par["mol_traj"] = system
        self.system = SimulatedSystem(system_par)
        self.modifier = ScatterDataMofifier(self.scatter, self.system)
        
             
if __name__ == "__main__":
    app = QApplication.instance()
    if app == None:
        app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()

    sys.exit(app.exec_())

