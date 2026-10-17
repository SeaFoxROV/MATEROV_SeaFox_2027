from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtNetwork import QAbstractSocket


class WebSocket:
    def __init__(self):
        self.ws_url = "ws://10.4.65.90:3001"
        self.ws_pending_message = None
        self.websocket = QWebSocket()
        self.websocket.connected.connect(self._on_ws_connected)
        self.websocket.disconnected.connect(self._on_ws_disconnected)

    def _on_ws_connected(self):
        print(f"WebSocket conectado a {self.ws_url}")
        if self.ws_pending_message:
            self.websocket.sendBinaryMessage(self.ws_pending_message)
            print(f"Mensaje WebSocket enviado: {self.ws_pending_message}")
            self.ws_pending_message = None

    def _on_ws_disconnected(self):
        print("WebSocket desconectado")

    def _send_ws_message(self, message):
        if self.websocket.state() == QAbstractSocket.ConnectedState:
            self.websocket.sendBinaryMessage(message)
            print(f"Mensaje WebSocket enviado: {message}")
            return

        elif self.websocket.state() == QAbstractSocket.ConnectingState:
            self.ws_pending_message = message
            print(f"WebSocket aún conectando a {self.ws_url}...")
            return

        self.ws_pending_message = message
        print(f"Conectando WebSocket a {self.ws_url}...")
        self.websocket.open(QUrl(self.ws_url))

    def _on_ws_error(self, error):
        print("WebSocket error:", self.websocket.errorString())

    def _on_ws_message(self, message):
        print("Mensaje recibido:", message)