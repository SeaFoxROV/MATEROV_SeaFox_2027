import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import cv2
import numpy as np

# puerto -> (nombre, color BGR)
CAMERAS = {
    8001: ("CAM 1 (main)", (60, 60, 200)),
    8002: ("CAM 2 (upper)", (60, 200, 60)),
    8003: ("CAM 3 (gripper)", (200, 120, 40)),
}


def make_handler(name, color):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            if not self.path.startswith("/snapshot"):
                self.send_error(404)
                return
            img = np.full((480, 640, 3), color, dtype=np.uint8)
            t = time.time()
            x = int(320 + 250 * np.sin(t * 2))  # círculo en movimiento
            cv2.circle(img, (x, 360), 30, (255, 255, 255), -1)
            cv2.putText(img, name, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
            cv2.putText(img, time.strftime("%H:%M:%S"), (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            ok, jpg = cv2.imencode(".jpg", img)
            body = jpg.tobytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass  # sin spam en la terminal

    return Handler


for port, (name, color) in CAMERAS.items():
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(name, color))
    Thread(target=server.serve_forever, daemon=True).start()
    print(f"{name}: http://127.0.0.1:{port}/snapshot/PROFILE_000")

print("Cámaras falsas activas. Ctrl+C para salir.")
while True:
    time.sleep(1)