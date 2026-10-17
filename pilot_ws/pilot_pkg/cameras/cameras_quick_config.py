import cv2

class ImageAdjuster:
    def __init__(self):
        self.brightness = 0
        self.contrast = 1.0
        self.saturation = 1.0

    def set_brightness(self, value):
        self.brightness = value

    def set_contrast(self, value):
        self.contrast = value

    def set_saturation(self, value):
        self.saturation = value

    def apply(self, frame):
        # Brillo y contraste
        frame = cv2.convertScaleAbs(
            frame,
            alpha=self.contrast,
            beta=self.brightness
        )

        # Saturación
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype("float32")
        hsv[...,1] *= self.saturation
        hsv[...,1] = hsv[...,1].clip(0,255)
        frame = cv2.cvtColor(hsv.astype("uint8"), cv2.COLOR_HSV2BGR)

        return frame