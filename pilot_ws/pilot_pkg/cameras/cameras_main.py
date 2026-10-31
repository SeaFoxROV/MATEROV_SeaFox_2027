import sys
import cv2
import numpy as np
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QWidget,
    QSizePolicy,
    QPlainTextEdit,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QBuffer
from PyQt5.QtGui import QImage, QPixmap

# Para mostrar el pwm en el status
import json
from PyQt5.QtNetwork import QUdpSocket, QHostAddress
# from lib.vision.crabDetection import CrabDetector
# from components.websocket import WebSocket

from cameras_quick_config import ImageAdjuster
# TODO: Revisar como se va a comportar la camara con el resize en linux
import os


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

        if os.environ.get("FAKE_CAMERAS"):
            self.camera_configs = {
                "main": "http://admin:admin@127.0.0.1:8001/snapshot/PROFILE_000",
                "upper": "http://admin:admin@127.0.0.1:8002/snapshot/PROFILE_000",
                "gripper": "http://admin:admin@127.0.0.1:8003/snapshot/PROFILE_000",
            }
        else:
            self.camera_configs = {
                "main": "http://admin:admin@192.168.1.27:6688/snapshot/PROFILE_000",
                "upper": "http://admin:admin@192.168.1.67:6688/snapshot/PROFILE_000",
                "gripper": "http://admin:admin@192.168.1.68:6688/snapshot/PROFILE_000",
            }
        self.grid_pos = {"main": (0, 0), "upper": (0, 1), "gripper": (1, 0)}
        self.titles = {}
        self.threads = {}
        self.labels = {}
        self.camera_containers = {}
        self.selected_camera = None
        self.setFrameShape(QFrame.StyledPanel)
        main_layout = QGridLayout()

        for name, url in self.camera_configs.items():
            adjuster = ImageAdjuster()

            container = QWidget()
            camera_layout = QVBoxLayout()
            camera_layout.setContentsMargins(0, 0, 0, 0)

            title = QLabel(name.upper())
            title.setAlignment(Qt.AlignCenter)
            title.setFixedHeight(22)
            title.setStyleSheet(
                "font-weight: bold; color: #000000; background-color: #FFD700;"
            )
            self.titles[name] = title

            image_label = QLabel("Conectando...")
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setMinimumSize(1, 1)
            image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            image_label.setStyleSheet(
                "background-color: black; border: 1px solid #1E90FF;"
            )
            self.labels[name] = image_label

            camera_layout.addWidget(title, 0)
            camera_layout.addWidget(image_label, 1)
            container.setLayout(camera_layout)

            row, col = self.grid_pos[name]
            main_layout.addWidget(container, row, col)
            self.camera_containers[name] = container

            thread = VideoThread(name, url, adjuster)
            thread.change_pixmap_signal.connect(
                lambda img, lbl=image_label: self.set_image(img, lbl)
            )
            thread.start()
            self.threads[name] = thread

        # Terminal de status (abajo a la derecha), FUERA del for
        self.status_box = QPlainTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setMaximumBlockCount(500)
        self.status_box.setStyleSheet(
            "background-color: black; color: #1E90FF; "
            "font-family: monospace; font-size: 20px; border: 4px solid #FFFF00;"
        )
        main_layout.addWidget(self.status_box, 1, 1)
        self.pwm_socket = QUdpSocket(self)
        self.pwm_socket.bind(QHostAddress.Any, 5005)
        self.pwm_socket.readyRead.connect(self.read_pwm)

        # Columna izquierda ancha, derecha angosta; fila de abajo más alta
        main_layout.setColumnStretch(0, 3)
        main_layout.setColumnStretch(1, 1)
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 1)

        self.setLayout(main_layout)
    
    def log(self, message):
        self.status_box.appendPlainText(message)
    
    def swap_cameras(self, a="upper", b="gripper"):
        ta, tb = self.threads[a], self.threads[b]
        ta.url, tb.url = tb.url, ta.url
        ta.adjuster, tb.adjuster = tb.adjuster, ta.adjuster

        title_a, title_b = self.titles[a].text(), self.titles[b].text()
        self.titles[a].setText(title_b)
        self.titles[b].setText(title_a)

    def read_pwm(self):
        while self.pwm_socket.hasPendingDatagrams():
            data, _, _ = self.pwm_socket.readDatagram(
                self.pwm_socket.pendingDatagramSize()
            )
            try:
                values = json.loads(bytes(data).decode())
            except ValueError:
                continue
            lines = [f"M{i + 1}: {v}" for i, v in enumerate(values)]
            self.status_box.setPlainText("PWM\n" + "\n".join(lines))

    def set_image(self, q_img, label):
        pixmap = QPixmap.fromImage(q_img).scaled(
            label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        label.setPixmap(pixmap)

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
                "font-weight: bold; color: #000000; background-color: #FFD700;"
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