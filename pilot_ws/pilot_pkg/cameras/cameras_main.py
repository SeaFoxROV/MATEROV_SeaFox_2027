import sys
import cv2
import numpy as np
import requests
import os
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QVBoxLayout,
    QLabel,
    QWidget,
    QSizePolicy,
    QGridLayout,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QBuffer
from PyQt5.QtGui import QImage, QPixmap

# from lib.vision.crabDetection import CrabDetector
# from components.websocket import WebSocket

from cameras_quick_config import ImageAdjuster
# TODO: Revisar como se va a comportar la camara con el resize en linux


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, name, url, adjuster):
        super().__init__()
        self.name = name
        self.url = url
        self._run_flag = True
        self.adjuster = adjuster
        self.session = requests.Session()
        self.apply_adjustments = False
        self.qimg = None

        # self.detecter = CrabDetector()
        self.isDetecting = False

        # self.websocket = WebSocket()
        self.annotated_results = None

    def run(self):
        while self._run_flag:
            try:
                # snapshot
                response = self.session.get(self.url, timeout=0.3)
                if response.status_code == 200:
                    array = np.frombuffer(response.content, dtype=np.uint8)
                    cv_img = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    # cv_img = cv2.rotate(cv_img, cv2.ROTATE_90_COUNTERCLOCKWISE)

                    if cv_img is not None:
                        cv_img = self.adjuster.apply(cv_img)
                        if self.isDetecting:
                            print("Haciendo deteccion")
                            # self.annotated_results = self.detecter.detect(cv_img)
                        height, width, channel = cv_img.shape
                        bytes_per_line = 3 * width

                        # to Qt
                        q_img = QImage(
                            cv_img.data,
                            width,
                            height,
                            bytes_per_line,
                            QImage.Format_RGB888,
                        ).rgbSwapped()
                        # label signal
                        self.change_pixmap_signal.emit(q_img)
                        self.qimg = q_img
            except Exception as e:
                self.msleep(100)

    def start_detection(self, name):
        print(self.name)
        if self.name == name:
            # print("ENTRASTE")
            self.isDetecting = True

    def stop_detection(self):
        self.isDetecting = False

    def stop(self):
        self._run_flag = False
        self.wait()

    def send_snapshot(self, name):
        if self.name != name:
            return
        if self.qimg is None:
            return
        qimg = self.qimg.scaled(320, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buffer = QBuffer()
        buffer.open(QBuffer.WriteOnly)
        qimg.save(buffer, "JPEG", quality=85)  # o "PNG" si prefieres sin pérdida
        image_bytes = buffer.data()  # Esto es QByteArray
        buffer.close()

        detections = self.annotated_results or {}
        # self.websocket._send_ws_message(image_bytes, detections)


class CameraWidget(QFrame):
    def __init__(self):
        super().__init__()

        self.camera_configs = {
            # "main": "http://admin:admin@192.168.1.27:6688/snapshot/PROFILE_000",
            "upper": "http://admin:admin@192.168.1.67:6688/snapshot/PROFILE_000",
            "middle": "http://admin:admin@192.168.1.68:6688/snapshot/PROFILE_000",
        }

        grid_positions = {
            "main": (0,0),
            "upper": (0,1),
            "middle": (1,0),
            "Status": (1,1),
        }

        
        self.titles = {}
        self.threads = {}
        self.labels = {}
        self.camera_containers = {}
        self.selected_camera = None
        self.setFrameShape(QFrame.StyledPanel)
    
        main_layout = QGridLayout()
        main_layout.setContentsMargins(5,5,5,5)
        main_layout.setSpacing(5)


        for name, url in self.camera_configs.items():
            adjuster = ImageAdjuster()

            title = QLabel(name.upper())
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet(
                "font-weight: bold; color: white; background-color: #333;"
            )
            self.titles[name] = title

            image_label = ScaledImageLabel("Conectando...")
            # if os.path.exists(url):
            #     image_label.setPixmap(QPixmap(url))
            # else:
            #     placeholder = QPixmap(640, 480)
            #     placeholder.fill(Qt.GlobalColor.darkGray)
            #     image_label.setPixmap(placeholder)
            # self.labels[name] = image_label

            container = QWidget()
            container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            camera_layout = QVBoxLayout(container)
            camera_layout.setContentsMargins(0, 0, 0, 0)
            camera_layout.setSpacing(5)
            camera_layout.addWidget(title)
            camera_layout.addWidget(image_label, stretch=1)

            row, col = grid_positions[name]
            main_layout.addWidget(container, row, col)
            self.camera_containers[name] = container

            thread = VideoThread(name, url, adjuster)
            thread.change_pixmap_signal.connect(
                lambda img, lbl=image_label: self.set_image(img, lbl)
            )
            thread.start()
            self.threads[name] = thread

        main_layout.setRowStretch(0,1)
        main_layout.setRowStretch(1,1)
        main_layout.setRowStretch(1,0)
        main_layout.setRowStretch(1,1)

        self.setLayout(main_layout)


    def set_image(self, q_img, label):
        label.setPixmap(QPixmap.fromImage(q_img))


    def closeEvent(self, event):
        for thread in self.threads.values():
            thread.stop()
        event.accept()

    def select_camera(self, camera_name):
        for name, thread in self.threads.items():
            thread.apply_adjustments = False
        if camera_name in self.threads:
            self.threads[camera_name].apply_adjustments = True
            self.selected_camera = camera_name

    def get_selected_camera(self):
        if self.selected_camera is None:
            return None
        return self.threads[self.selected_camera].adjuster

    def set_title_style(self, camera_name, style):
        for name in self.titles.keys():
            self.titles[name].setStyleSheet(
                "font-weight: bold; color: white; background-color: #333;"
            )
        if camera_name in self.titles:
            self.titles[camera_name].setStyleSheet(style)

    def maximize_camera(self, camera_name):
        for name, container in self.camera_containers.items():
            if name == camera_name:
                container.show()
            else:
                container.hide()

    def reset_camera_view(self):
        for container in self.camera_containers.values():
            container.show()

class ScaledImageLabel(QLabel):
    """QLabel that keeps its original pixmap + rescales"""
    def __init__(self, text=""):
        super().__init__(text)
        self._pixmap = None
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(1,1)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setStyleSheet("background-color: black; border: 1px solid gray;")

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self._rescale()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()

    def _rescale(self):
        if self._pixmap is None or self.width() < 2 or self.height() < 2:
            return
        super().setPixmap(
            self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    win_layout = QVBoxLayout()

    cam_widget = CameraWidget()
    win_layout.addWidget(cam_widget)

    window.setLayout(win_layout)
    window.setWindowTitle("SeaFox ROV - Multi-Camera System")
    window.show()
    sys.exit(app.exec_())