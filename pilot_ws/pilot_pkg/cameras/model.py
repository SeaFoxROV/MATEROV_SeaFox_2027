from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ModelWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)

        layout = QHBoxLayout()
        label = QLabel("3D Model Widget")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)