from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

import cv2 as cv
import numpy as np
import sys

class TStream(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, url):
        super().__init__()
        self._run_flag = True
        self.url = url

    def run(self):
        cap = cv.VideoCapture(self.url)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.cam1_url = 'rtsp://192.168.0.60:6010/11'
        self.cam2_url = 'rtsp://192.168.0.61:6011/11'
        self.setWindowTitle("Visualisateur de caméras de surveillance")
        self.disply_width = 640
        self.display_height = 480
        self.cam1_label = QLabel(self)
        self.cam1_label.resize(self.disply_width, self.display_height)
        self.cam2_label = QLabel(self)
        self.cam2_label.resize(self.disply_width, self.display_height)
        layout = QGridLayout()
        layout.addWidget(QLabel("Caméra #1: {} - Porte de garage".format(self.cam1_url)), 0, 0, Qt.AlignCenter | Qt.AlignBottom)
        layout.addWidget(QLabel("Caméra #2: {} - Porte principale".format(self.cam2_url)), 2, 0, Qt.AlignCenter | Qt.AlignBottom)
        layout.addWidget(self.cam1_label, 1, 0)
        layout.addWidget(self.cam2_label, 3, 0)
        layout.setRowMinimumHeight(0, 20)
        layout.setRowMinimumHeight(2, 40)
        self.setLayout(layout)
        self.cam1 = TStream(self.cam1_url)
        self.cam2 = TStream(self.cam2_url)
        self.cam1.change_pixmap_signal.connect(self.cam1_update)
        self.cam2.change_pixmap_signal.connect(self.cam2_update)
        self.cam1.start()
        self.cam2.start()

    def closeEvent(self, event):
        self.cam1.stop()
        self.cam2.stop()
        event.accept()

    @pyqtSlot(np.ndarray)
    def cam1_update(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.cam1_label.setPixmap(qt_img)

    @pyqtSlot(np.ndarray)
    def cam2_update(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.cam2_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

if __name__ == '__main__':
    appctxt = ApplicationContext()
    app = QApplication(sys.argv)
    application = App()
    application.setWindowFlags(Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
    application.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)