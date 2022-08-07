#!/usr/bin/python3

# Arducam 64MP camera app
# Some of the code has been copied and modified from various sources including
# Arducam and some of the examples from Pcamera2 github page
# Initial creation date: Jun 2022 by David Peck
# App Name: Arducam_Hawk-Eye_Camera_V1.0.py

import sys
import time

from PyQt5 import QtCore
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from picamera2.previews.qt import QGlPicamera2

from Focuser import Focuser

# Initial settings

focuser = Focuser(1)
focus = 420  # Initial Focus Setting
focuser.set(Focuser.OPT_FOCUS, focus)

zoom_count = 0  # Initial Zoom Setting

recording = False

captured = 0  # Initial number of Images Captured
vid_count = 0  # Initial number of Images Captured

picam2 = Picamera2()
main_stream = {"size": (2312, 1736)}
lores_stream = {"size": (1920, 1080)}
video_config = picam2.create_video_configuration(main_stream, lores_stream, encode="lores")
picam2.configure(video_config)


############# GUI Class and Definitions ##############

class ArduCam(QtWidgets.QMainWindow):
    # JPG Image Capture
    def on_jpg_clicked(self):
        global captured
        data = time.strftime("%Y-%b-%d_(%H%M%S)")
        captured = captured + 1
        request = picam2.capture_request()
        request.save("main", '/home/pi/Pictures/%s.jpg' % data)
        request.release()
        self.jpg_count_label.setText(str(captured))

    # MP4 Video Capture (no sound)        
    def on_vid_clicked(self):
        global recording
        global vid_count
        data = time.strftime("%Y-%b-%d_(%H%M%S)")
        if not recording:
            self.vid_capture.setText("Stop Recording")
            self.vid_capture.setStyleSheet("background-color : red")
            encoder = H264Encoder(10000000)
            encoder.output = FfmpegOutput('/home/pi/Videos/%s.mp4' % data)
            picam2.start_encoder(encoder)
            recording = True
        else:
            picam2.stop_encoder()
            vid_count = vid_count + 1
            self.vid_capture.setText("Capture MP4: Saved = ")
            self.vid_capture.setStyleSheet("background-color : #efefef")
            self.mp4_count_label.setText(str(vid_count))

    # Zoom In Control
    def on_zoom_button_clicked(self):
        global zoom_count
        self.zoom_minus.setText("Zoom - ")
        zoom_count = zoom_count + 1
        size = picam2.capture_metadata()['ScalerCrop'][2:]
        size = [int(s * 0.95) for s in size]
        offset = [(r - s) // 2 for r, s in zip(picam2.sensor_resolution, size)]
        picam2.set_controls({"ScalerCrop": offset + size})

        if zoom_count == 52:
            size_1 = [9216, 6944]
            offset_1 = [0, 0]
            picam2.set_controls({"ScalerCrop": offset_1 + size_1})
            zoom_count = 0

        if zoom_count < 50:
            self.zoom_plus.setText("Zoom + " + str(zoom_count))
            self.zoom_plus.setStyleSheet("background-color : #efefef")

        if zoom_count == 50:
            self.zoom_plus.setText("Max")
            self.zoom_plus.setStyleSheet("background-color : red")

    # Zoom Out Control
    def on_zoom_down_button_clicked(self):
        global zoom_count
        size = picam2.capture_metadata()['ScalerCrop'][2:]

        if zoom_count == 0:
            size = [9216, 6944]
            offset = [0, 0]
            picam2.set_controls({"ScalerCrop": offset + size})
            zoom_count = 0

        else:
            zoom_count = zoom_count - 1
            size = [int(s / 0.95) for s in size]
            offset = [(r - s) // 2 for r, s in zip(picam2.sensor_resolution, size)]
            picam2.set_controls({"ScalerCrop": offset + size})

            if zoom_count < 50:
                self.zoom_plus.setText("Zoom + ")
                self.zoom_minus.setText("Zoom - " + str(zoom_count))
                self.zoom_plus.setStyleSheet("background-color : #efefef")

            if zoom_count == 50:
                print(zoom_count)
                self.zoom_plus.setText("Max")
                self.zoom_plus.setStyleSheet("background-color : red")

    # Zoom Reset
    def on_zoom_reset(self):
        global zoom_count
        size = [9216, 6944]
        offset = [0, 0]
        picam2.set_controls({"ScalerCrop": offset + size})
        zoom_count = 0
        self.zoom_plus.setStyleSheet("background-color : #efefef")
        self.zoom_plus.setText("Zoom + ")
        self.zoom_minus.setText("Zoom - ")

    # Focus Control
    def focus_value_changed(self, f):
        global focus
        focus = f
        focuser.set(Focuser.OPT_FOCUS, f)
        self.focus_reset_button.setText("(Click to Reset Focus) - Value: " + str(focus))

    # Focus Reset
    def on_focus_reset_button_clicked(self):
        f = 420
        focuser.set(Focuser.OPT_FOCUS, f)
        self.focus_slider.setValue(420)

    # App Exit
    def on_exit(self):
        app.quit()

        ############## Load and Initilise GUI ################

    def __init__(self):
        super(ArduCam, self).__init__()
        self.exit_button = None
        self.exit_button = None
        self.focus_reset_button = None
        self.focus_reset_button = None
        self.focus_slider = None
        self.focus_slider = None
        self.focus_slider = None
        self.focus_slider = None
        self.zoom_reset_button = None
        self.zoom_minus = None
        self.jpg_count_label = None
        self.focus_slider = None
        self.focus_reset_button = None
        self.zoom_minus = None
        self.zoom_minus = None
        self.jpg_count_label = None
        self.jpg_capture = None
        self.zoom_minus = None
        self.mp4_count_label = None
        self.vid_capture = None
        self.zoom_plus = None
        uic.loadUi('ArduCam.ui', self)  # PyQt Designer File fo GUI
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)  # Enable Window Flags
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)  # Disable Close Window

        # Capture Control
        # noinspection PyUnresolvedReferences
        self.jpg_capture.clicked.connect(self.on_jpg_clicked)
        self.jpg_count_label.setStyleSheet("background-color : #A3F2CF")

        self.vid_capture.clicked.connect(self.on_vid_clicked)
        self.mp4_count_label.setStyleSheet("background-color : #A3F2CF")

        # Zoom Control
        self.zoom_plus.clicked.connect(self.on_zoom_button_clicked)

        self.zoom_minus.clicked.connect(self.on_zoom_down_button_clicked)

        self.zoom_reset_button.clicked.connect(self.on_zoom_reset)

        # Focus Control
        self.focus_slider.setRange(200, 900)
        self.focus_slider.setValue(420)
        self.focus_slider.valueChanged.connect(self.focus_value_changed)
        self.focus_slider.setStyleSheet("background-color : #f5fefe")

        self.focus_reset_button.clicked.connect(self.on_focus_reset_button_clicked)
        self.focus_reset_button.setText("(Click to Reset Focus) - Value: " + str(focus))

        # Exit App
        self.exit_button.clicked.connect(self.on_exit)
        self.exit_button.setStyleSheet("background-color : red")

        ######################################################


# Camera Widget
app = QtWidgets.QApplication([])

window = QWidget()
window.setWindowTitle("Arducam Camera")
window.setWindowFlags(window.windowFlags() | QtCore.Qt.CustomizeWindowHint)  # Enable Window Flags
window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)  # Disable Close Window in Camera Widget
qpicamera2 = QGlPicamera2(picam2, width=800, height=500)
layout_h = QHBoxLayout()
layout_h.addWidget(qpicamera2)
window.resize(800, 600)
window.setLayout(layout_h)

# Run GUI
win = ArduCam()
picam2.start()
window.show()
win.show()
sys.exit(app.exec())

######################################################
