from email.mime import message
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout
from PyQt5.QtCore import Qt

from camera import CameraWidget
# from components.model import ModelWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pilot GUI")
        self.setGeometry(100, 100, 800, 500)
        self.all_cameras = False
        self.selected_camera = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.left_widget = CameraWidget()
        # self.right_widget = ModelWidget()

        layout.addWidget(self.left_widget)
        # layout.addWidget(self.right_widget)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

    def keyPressEvent(self, event):
        # Camera selection
        if event.text() == "1":
            if self.selected_camera == "1":
                self.left_widget.maximize_camera("main")
            self.selected_camera = "1"
            self.left_widget.select_camera("main")
            self.all_cameras = False
            self.left_widget.set_title_style(
                "main", "font-weight: bold; color: white; background-color: #2BCF47;"
            )
        elif event.text() == "2":
            if self.selected_camera == "2":
                self.left_widget.maximize_camera("upper")
            self.selected_camera = "2"
            self.left_widget.select_camera("upper")
            self.all_cameras = False
            self.left_widget.set_title_style(
                "upper", "font-weight: bold; color: white; background-color: #2BCF47;"
            )
        elif event.text() == "3":
            if self.selected_camera == "3":
                self.left_widget.maximize_camera("middle")
            self.selected_camera = "3"
            self.left_widget.select_camera("middle")
            self.all_cameras = False
            self.left_widget.set_title_style(
                "middle", "font-weight: bold; color: white; background-color: #2BCF47;"
            )
        elif event.text() == "0":
            self.selected_camera = 0
            self.all_cameras = True
            for name in self.left_widget.threads.keys():
                self.left_widget.set_title_style(
                    name, "font-weight: bold; color: white; background-color: #333;"
                )
        elif event.key() == Qt.Key_Escape:
            self.left_widget.reset_camera_view()

        # WebSocket conf
        elif event.key() == Qt.Key_Space and self.selected_camera:
            if self.selected_camera:
                for thread in self.left_widget.threads.values():
                    print(self.left_widget.selected_camera)
                    thread.send_snapshot(self.left_widget.selected_camera)
                # self.left_widget.get_snapshot()

        # Crab detection
        elif event.text() == "D":
            if self.selected_camera:
                for thread in self.left_widget.threads.values():
                    print(self.left_widget.selected_camera)
                    thread.start_detection(self.left_widget.selected_camera)

        elif event.text() == "d":
            for thread in self.left_widget.threads.values():
                thread.stop_detection()

        # Quick conf
        elif event.text() == "B":
            if self.all_cameras:
                for name in self.left_widget.threads.keys():
                    adjuster = self.left_widget.threads[name].adjuster
                    adjuster.set_brightness(adjuster.brightness + 10)
            else:
                adjuster = self.left_widget.get_selected_camera()
                if adjuster:
                    adjuster.set_brightness(adjuster.brightness + 10)
        elif event.text() == "b":
            if self.all_cameras:
                for name in self.left_widget.threads.keys():
                    adjuster = self.left_widget.threads[name].adjuster
                    adjuster.set_brightness(adjuster.brightness - 10)
            else:
                adjuster = self.left_widget.get_selected_camera()
                if adjuster:
                    adjuster.set_brightness(adjuster.brightness - 10)
        elif event.text() == "C":
            if self.all_cameras:
                for name in self.left_widget.threads.keys():
                    adjuster = self.left_widget.threads[name].adjuster
                    adjuster.set_contrast(adjuster.contrast + 0.1)
            else:
                adjuster = self.left_widget.get_selected_camera()
                if adjuster:
                    adjuster.set_contrast(adjuster.contrast + 0.1)
        elif event.text() == "c":
            if self.all_cameras:
                for name in self.left_widget.threads.keys():
                    adjuster = self.left_widget.threads[name].adjuster
                    adjuster.set_contrast(adjuster.contrast - 0.1)
            else:
                adjuster = self.left_widget.get_selected_camera()
                if adjuster:
                    adjuster.set_contrast(adjuster.contrast - 0.1)
        elif event.text() == "S":
            if self.all_cameras:
                for name in self.left_widget.threads.keys():
                    adjuster = self.left_widget.threads[name].adjuster
                    adjuster.set_saturation(adjuster.saturation + 0.1)
            else:
                adjuster = self.left_widget.get_selected_camera()
                if adjuster:
                    adjuster.set_saturation(adjuster.saturation + 0.1)
        elif event.text() == "s":
            if self.all_cameras:
                for name in self.left_widget.threads.keys():
                    adjuster = self.left_widget.threads[name].adjuster
                    adjuster.set_saturation(adjuster.saturation - 0.1)
            else:
                adjuster = self.left_widget.get_selected_camera()
                if adjuster:
                    adjuster.set_saturation(adjuster.saturation - 0.1)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
