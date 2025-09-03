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
        self.setCentralWidget(TimeGlobeWidget())
        # self.sphere = Sphere(self) 
        # self.setCentralWidget(self.sphere)
        
        self.set_up_backend()
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
    def __init__(self):
        super().__init__()

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

        self.sphere = Sphere()
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

class Satellites(QOpenGLWidget):
    #Bugs in this class:
    #1. Orbit doesn't align with the satellites. I've tried to make it work, but it doesn't.
    #2. Some satellites in the SATTLE.txt have positions that are 40,000,000km from earth, which don't make sense.
    #3. Time hasn't been included in this yet
    #
    #
    def __init__(self):
        self.satellites = {}
        self.read_file()
        #self.get_data_from_overlay()
        self.time = 0
        self.position = 0
        self.quadric = None
        
    def Quadric(self, quad=None):
        if quad != None:
            self.quadric = quad
        else:
            return self.quadric
        
    #Temp function just for visual. Need to update this gui to get one main loop
    def read_file(self):
        input_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), r"TLEs/SATTLE.txt")
        satellites = load.tle_file(input_file)
        if not satellites:
            print("No TLE Data Found")
            return
    
        satDict = {}
        for sat in satellites:
            satnum = sat.model.satnum
            if satnum != 19274 and satnum != 7924: continue
            if satnum not in satDict.keys():
                satDict[satnum] = []
            #Restricts Dictionary to 10 Positions, best to remove in the future
            if len(satDict[satnum]) > 10:
                continue
            satDict[satnum].append(sat)
       
        self.satellites = satDict
        
    def SatDraw(self):
        self.DrawSatellites()
        self.DrawOrbits()
        
    def tempColor(self, satnum):
        #Color to differentiate satellites
        r = (satnum // 10000)/100
        g = ((satnum // 100) % 100)/100
        b = (satnum % 100)/100
        glColor3f(r,g,b)
        
    def getXYZ(self, position):
        geocentric = position.at(load.timescale().utc(self.time)).position.km
        x,y,z = (pos/EARTH_RADIUS for pos in geocentric)
        return x,y,z
            
    def DrawSatellites(self, sphere_radius=0.05):
        for satnum,positions in self.satellites.items():
            x,y,z = self.getXYZ(positions[self.position])
            self.tempColor(satnum)
            glPushMatrix()
            glTranslatef(x,y,z)
            gluSphere(self.quadric, sphere_radius, 40, 40)
            glPopMatrix()
            
    def CalculateOrbit(self, p1, p2):
        #Doesn't work :(
        def normalize(v):
            norm = np.linalg.norm(v)
            return v / norm if norm != 0 else v
        p1 = np.array(p1, dtype=np.float64)
        p2 = np.array(p2, dtype=np.float64)

        center = (p1 + p2) / 2
        vec = p2 - p1

        # Find normal of the disk plane
        arbitrary = np.array([1, 0, 0]) if abs(vec[0]) < 0.9 else np.array([0, 1, 0])
        tangent = normalize(np.cross(vec, arbitrary))
        normal = normalize(np.cross(vec, tangent))

        # Compute rotation from [0,0,1] (XY disk normal) to this normal
        from_vec = np.array([0, 0, 1])
        to_vec = normal
        axis = normalize(np.cross(from_vec, to_vec))
        dot = np.clip(np.dot(from_vec, to_vec), -1.0, 1.0)
        angle = np.degrees(np.arccos(dot))

        if np.linalg.norm(axis) < 1e-6:
            axis = np.array([1, 0, 0])  # arbitrary axis if vectors are parallel or anti-parallel

        radius = np.linalg.norm(vec) / 2

        return center, normal, axis, angle, radius

    def DrawOrbits(self):
        for satnum,positions in self.satellites.items():
            center, normal, axis, angle, radius = self.CalculateOrbit(self.getXYZ(positions[self.position]), self.getXYZ(positions[self.position+1]))
            self.tempColor(satnum)
            glPushMatrix()
            glRotatef(angle*180/math.pi, *axis)
            glRotatef(angle*180/math.pi, *normal)
            gluDisk(self.quadric, 1.28, 1.3, 40, 1)
            glPopMatrix()

# ————————————————————————————————
#  3) Earth
# ————————————————————————————————

class  Sphere(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.xRot = 0.0
        self.yRot = 90.0  # Start with prime meridian facing front
        self.zRot = 0.0
        self.quadric = None
        self.textureID = 0
        
        
        self.satellites = Satellites()

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
        self.satellites.SatDraw()
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
        return_dict = {}

        for i in self.tle_dict:
            if(self.tle_status[i]):
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
        
    def add(self, name, line_1, line_2):
        self.tle_dict[name] = [line_1, line_2]
        self.tle_status[name] = True

    def delete(self, element_name):
        del self.tle_dict[element_name]
        del self.tle_status[element_name]
    
    def set_element_state(self, element_name, element_state):
        self.tle_status[element_name] =  element_state


#endregion


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())