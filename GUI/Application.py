import sys
import numpy as np
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QFontDatabase, QFont, QSurfaceFormat, QImage
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QOpenGLWidget
)
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QFrame, QGraphicsOpacityEffect

import math
import datetime
import os
import skyfield
from skyfield.api import load
from skyfield.api import Timescale
from skyfield.api import EarthSatellite

from Components.GraphDisplay import GraphDisplay
from Components.TLEDisplay import TLEDisplay

EARTH_RADIUS = 6378
increment = False

# ————————————————————————————————
#  1) Main Window
# ————————————————————————————————

class MainWindow(QMainWindow):
    
    def __init__(self): 
        super().__init__()
        #Initialize window and place OpengGL inside 
        self.setWindowTitle("S.P.A.C.E")
        self.setGeometry(100, 100, 640, 480)

        self.set_up_backend()

        self.setCentralWidget(TimeGlobeWidget(self.backend))
        # self.sphere = Sphere(self) 
        # self.setCentralWidget(self.sphere)
        
        self.set_up_tle_display()
        
        #self.set_up_graph_display()
        #self.buildUI()

    def set_up_tle_display(self):
        self.tle_display = TLEDisplay(self)
        self.tle_display.raise_()

    def set_up_graph_display(self):
        self.graph_display = GraphDisplay(self)
        self.graph_display.raise_()

    def set_up_backend(self):
        self.backend = Backend()

    #PATCHNOTE: Added ResizeEvent to main window, solved TLEDisplay resize issue
    #TODO: figure out resize update for tleDisplay scoll window
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.tle_display.update_size()
        #self.graph_display.update_height()

##-----------------
#class TimeSliderWidget(QWidget):
#
#    def __init__(self):
#        super().__init__()
#        self.parent().sphere
#        self.setWindowTitle("Clock Display")
#        self.setGeometry(100, 100, 800, 400)
#
#        font = QFont('Arial', 120, QFont.Bold)
#
#        layout = QVBoxLayout()
#
#        # Clock Display
#        self.time_display = QLineEdit(self)
#        self.time_display.setReadOnly(True)  # Prevent edits
#        self.time_display.setAlignment(Qt.AlignCenter)
#        self.time_display.setFont(font)
#        self.time_display.setStyleSheet("border: none; background: transparent;")  # look like QLabel
#
#        # Accessibility for testing automation
#        self.time_display.setAccessibleName("clock_Time")
#        self.time_display.setAccessibleDescription(QTime.currentTime().toString("hh:mm:ss"))
#
#
#         # Slider
#        self.slider = QSlider(Qt.Horizontal)
#        self.slider.setRange(0, 360)
#        self.slider.setValue(90)  
#        self.slider.setTickInterval(30)
#        self.slider.setTickPosition(QSlider.TicksBelow)
#        self.slider.valueChanged.connect(self.onSlider)
#
#        # Timer that updates clock
#        self.timer = QTimer(self)
#        self.timer.setInterval(1000)
#        self.timer.timeout.connect(self.tick)
#        self.now()
#        self.start()
#
#
#
#        # Play button
#        self.play_btn = QPushButton("▶")
#        self.play_btn.clicked.connect(self.scroll)
#        # Stop Button
#        self.stop_btn = QPushButton("Stop")
#        self.stop_btn.clicked.connect(self.stop)
#        # Start Button
#        self.start_btn    = QPushButton("Start")
#        self.start_btn.clicked.connect(self.start)
#        # Current Time Button
#        self.now_btn      = QPushButton("Now")
#        self.now_btn.clicked.connect(self.now)
#        # Reset Button
#        self.midnight_btn = QPushButton("Midnight")
#        self.midnight_btn.clicked.connect(self.midnight)
#
#
#        # Layout
#        layout.addWidget(self.time_display)
#        layout.addWidget(self.slider)
#        self.setLayout(layout)
#        h = QHBoxLayout()
#        for btn in (self.play_btn, self.start_btn, self.stop_btn, self.now_btn, self.midnight_btn):
#            h.addWidget(btn)
#        layout.addLayout(h)
#
#    # Animations Controls
#        self.anim = QPropertyAnimation(self.slider, b"value", self)
#        self.anim.setEasingCurve(QEasingCurve.Linear)
#        self.anim.setDuration(4000) #Orbit duration
#
#    # Time Controls
#    # Updates display clock every second
#    def tick(self):
#        self.time = self.time.addSecs(1)
#        self.time_display.setText(self.time.toString("hh:mm:ss"))
#        self.time_display.setAccessibleDescription(self.time.toString("hh:mm:ss"))
#
#    def start(self):
#        self.timer.start()
#
#    def now(self):
#        self.timer.stop()
#        self.time = QTime.currentTime()
#        self.time_display.setText(self.time.toString("hh:mm:ss"))
#        self.slider.setValue(seconds_to_degrees(QTime(0, 0).secsTo(self.time)))
#        self.timer.start()
#
#    def midnight(self):
#        self.timer.stop()
#        self.time = QTime(0, 0, 0)
#        self.slider.setValue(0)
#        self.time_display.setText(self.time.toString("hh:mm:ss"))
#
#    def stop(self):
#        self.timer.stop()
#        self.anim.stop()
#
#    # Slider Controls
#    def onSlider(self, value):
#        print(value)
#        self.timer.stop()
#        self.time = QTime(0,0).addSecs(degrees_to_sec(value))
#        self.time_display.setText(self.time.toString("hh:mm:ss"))
#        self.timer.start()
#        
#    def scroll(self):
#        self.anim.stop()
#        self.anim.setStartValue(self.slider.value())
#        self.anim.setEndValue(self.slider.maximum())
#        self.anim.start()
##---------------

# ————————————————————————————————
#  2) Time + UI Builder
# ————————————————————————————————
class TimeGlobeWidget(QWidget):
    def __init__(self, backend):
        super().__init__()

        self.backend = backend

        # Time Widget
        self.time = QTime.currentTime()
        self.welc_lbl     = QLabel("Welcome to S.P.A.C.E.")
        self.time_lbl     = QLabel(self.time.toString("hh:mm:ss"))
        self.start_btn    = QPushButton("Start")
        self.stop_btn     = QPushButton("Stop")
        self.now_btn      = QPushButton("Now")
        self.midnight_btn = QPushButton("Midnight")
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        
        self.buildUI()



    def buildUI(self):

        self.sphere = Sphere(self.backend)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setAccessibleName("slider_Time")

        self.slider.setRange(0, 360)
        self.slider.setValue(90)  # Start with Earth facing front
        self.slider.setTickInterval(30)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.onSlider)

        v = QVBoxLayout(self)
           
        v.addWidget(self.sphere, stretch=1)
        v.addWidget(self.slider)

        v.addWidget(self.welc_lbl, alignment=Qt.AlignHCenter)
        v.addWidget(self.time_lbl, alignment=Qt.AlignHCenter)

        h = QHBoxLayout()
        for btn in (self.start_btn, self.stop_btn, self.now_btn, self.midnight_btn):
            h.addWidget(btn)
        v.addLayout(h)

        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.now_btn.clicked.connect(self.now)
        self.midnight_btn.clicked.connect(self.midnight)

    def onSlider(self, value):
        self.sphere.yRot = float(value)
        self.sphere.update()

        self.now()
        self.start()

    def _tick(self):
        self.time = self.time.addSecs(1)
        self.time_lbl.setText(self.time.toString("hh:mm:ss"))

 
    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def now(self):
        self.timer.stop()
        self.time = QTime.currentTime()
        self.time_lbl.setText(self.time.toString("hh:mm:ss"))
        self.timer.start()

    def midnight(self):
        self.timer.stop()
        self.time = QTime(0, 0, 0)
        self.time_lbl.setText(self.time.toString("hh:mm:ss"))


# ————————————————————————————————
#  3) Satellites
# ————————————————————————————————

from skyfield.constants import ERAD

class Satellite():
    #A class to hold all information relating to a satellite to not overcrowd a dictionary
    def __init__(self, satellite):
        self.satellite = satellite
        self.positions = self.PopulateSatellitePositions()
        self.show = True #When needed its here

        #Constants
        self.color = self.Color()
        self.sphereRadius = 0.03

    def Color(self): #Temp Color for differentiation, will change to label instead and also be able to show or hide label
        tempColor = hash(self.satellite.model.satnum)
        return (tempColor%253/255, tempColor%254/255, tempColor%255/255)

    def PopulateSatellitePositions(self):
        year = self.satellite.model.epochyr
        day, month = divmod(self.satellite.model.epochdays, 12) #Split the days of epoch day into months and days in month
        revolutionsPerDay = self.satellite.model.no_kozai * 229.1831 #MinutesInADay/2Pi
        
        orbitalPeriod = 1 / (revolutionsPerDay - 1) #-1 to make orbits overlap slightly so other orbits can close

        orbitResolution = 1000 #How smooth the orbit is

        ts = load.timescale()
        times = ts.utc(year, month, np.linspace(day, day+orbitalPeriod, orbitResolution))

        positions = []
        for t in times:
            geocentric = self.satellite.at(t)
            x,y,z = (pos/(ERAD/1000) for pos in geocentric.position.km)
            positions.append((x,y,z))

        return positions

    def DrawLabel(self, quadric):
        if not self.show: return
        pass

    def DrawSatellite(self, quadric, position=0):
        if not self.show: return
        x,y,z = self.positions[position%len(self.positions)]
        glColor3f(*self.color)
        glPushMatrix()
        glTranslate(x,y,z)
        gluSphere(quadric, self.sphereRadius, 40, 40)
        glPopMatrix()

    def DrawOrbit(self):
        if not self.show: return
        glColor3f(*self.color)
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        for x,y,z in self.positions:
            glVertex3f(x,y,z)
        glEnd()

class Satellites(QOpenGLWidget):#Technically not needed, just here to show the satellites and their orbits, otherwise a list of Satellite objects would do
    def __init__(self, backend, parent=None):
        super().__init__(parent)
        
        self.backend = backend
        self.backend.subscribe(self.update_satellites)

        self.satellites = {}
        self.update_satellites()
        
        self.quadric = gluNewQuadric()
        self.position = 0
        
    def Quadric(self, quad=None):
        if quad:
            self.quadric = quad
        else:
            return self.quadric

    #If sticking with the read_tle_file function from the sat_sim_handler, then this code works, otherwise use other read_file function
    def update_satellites(self):
        
        tle_data = self.backend.get_data_from_enabled_tle_slots()

        if not tle_data:
            print("Null passed")
            return
        
        for i in tle_data:
            name = str(i)
            line_1 = tle_data[name][0]
            line_2 = tle_data[name][1]

            satellite = EarthSatellite(line_1, line_2, name, None)
            self.satellites[name] = Satellite(satellite)

    def Draw(self):
        for satellite in self.satellites.values():
            satellite.DrawSatellite(self.quadric, self.position)
            satellite.DrawOrbit()

# ————————————————————————————————
#  3) Earth
# ————————————————————————————————

class  Sphere(QOpenGLWidget):
    def __init__(self, backend, parent=None):
        super().__init__(parent)

        self.backend = backend

        self.xRot = 0.0
        self.yRot = 90.0  # Start with prime meridian facing front
        self.zRot = 0.0
        self.quadric = None
        self.textureID = 0
        
        
        self.satellites = Satellites(self.backend)

    def initializeGL(self):
        self.quadric = gluNewQuadric()
        gluQuadricTexture(self.quadric, GL_TRUE)
        self.satellites.Quadric(self.quadric)

        glClearColor(0.2, 0.3, 0.3, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        self.textureID = self.loadTexture(".\\GUI\\Assests\\Earth.png")
        if not self.textureID:
            glDisable(GL_TEXTURE_2D)
        else:
            print(f"[OK] Texture loaded. ID: {self.textureID}")

        # Flip texture vertically
        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glScalef(1.0, -1.0, 1.0)  # Flip vertically
        glMatrixMode(GL_MODELVIEW)

        self.quadric = gluNewQuadric()
        gluQuadricTexture(self.quadric, GL_TRUE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width() / (self.height() or 1), 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def loadTexture(self, path):
        img = QImage(path)
        if img.isNull():
            print(f"[Warning] Failed to load texture: {path}")
            return 0

        img = img.convertToFormat(QImage.Format_RGBA8888)
        w, h = img.width(), img.height()
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        arr = np.array(ptr, dtype=np.uint8).reshape(h, w, 4)

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, arr)
        glBindTexture(GL_TEXTURE_2D, 0)
        return tex

    def drawCone(self, radius, height, num_slices):
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(1.0, 0.5, 0.0, 0.5)  # Transparent orange
        glVertex3f(0, height / 2, 0)
        for i in range(num_slices + 1):
            angle = i * (2.0 * np.pi) / num_slices
            x = radius * np.cos(angle)
            z = radius * np.sin(angle)
            glVertex3f(x, -height / 2, z)
        glEnd()

    def paintGL(self):
        self.satellites.Draw()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Position the camera
        gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)

        # FIX 1: Align poles vertically (Z → Y)
        glRotatef(-90, 1, 0, 0)  # Rotate globe forward so poles face up/down

        # FIX 2: Rotate east–west around vertical (Z now acts as vertical)
        glRotatef(self.yRot, 0, 0, 1)

        # Draw Earth (opaque)
        if self.textureID:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textureID)

        glColor4f(1.0, 1.0, 1.0, 1.0)  # Ensure Earth is fully opaque
        gluSphere(self.quadric, 1.0, 40, 40)

        if self.textureID:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

        # Draw transparent cone
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        self.drawCone(radius=1.5, height=2.0, num_slices=40)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#region - Backend
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import sys

# setting path
sys.path.append('../SPACE')

import module_factory
from module_factory import ModuleKey

from workflows import flomps

import json

class Backend():

    def __init__(self):
        print("Backend - Init Started")

        self._subscribers = []

        self.tle_dict = {}
        self.tle_status = {}

        options = self.read_options_file()
        self.sat_sim_module = module_factory.create_sat_sim_module()
        self.sat_sim_module.config.read_options(options["sat_sim"])

        self.instance = self.sat_sim_module.handler.sat_sim
        
        print("Backend - Init complete")

    #Yoinked from main.py
    def read_options_file(self):
        """Parse the current JSON file in use for options configuration."""
        file = self.get_config_file()
        with open(file) as f:
            return json.load(f)

    def get_config_file(self):
        """Get the current JSON file in use for options configuration."""
        config_file = ''
        with open('settings.json') as f:
            options = json.load(f)
            config_file = options['config_file']

        return config_file
    
    def get_data_from_enabled_tle_slots(self):
        return_dict = None

        for i in self.tle_dict:
            if(self.tle_status[i]):
                if return_dict is None:
                    return_dict = {}

                name = str(i)
                line_1 = self.tle_dict[name][0]
                line_2 = self.tle_dict[name][1]
                
                return_dict[name] = [line_1, line_2]
        
        return return_dict

    #TODO: add functionality to manipulate tle_dict (Add, Remove, RemoveAt)
    def add_elements(self, tle_data):
        print("Backend - Adding Elements")
        for i in tle_data:
            name = str(i)
            line_1 = tle_data[name][0]
            line_2 = tle_data[name][1]

            self.add(name, line_1, line_2)

        self._notify()
        
    def add(self, name, line_1, line_2):
        self.tle_dict[name] = [line_1, line_2]
        self.tle_status[name] = True

    def delete(self, element_name):
        del self.tle_dict[element_name]
        del self.tle_status[element_name]

        self._notify()
    
    def set_element_state(self, element_name, element_state):
        self.tle_status[element_name] =  element_state

    def subscribe(self, callback):
        """Register a function to be called on update."""
        self._subscribers.append(callback)

    def _notify(self):
        """Call all subscribed functions."""
        for callback in self._subscribers:
            callback()
#endregion


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())