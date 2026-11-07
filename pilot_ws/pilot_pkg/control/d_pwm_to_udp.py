import json
import socket

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
# Todo para mostrar el pwm en el status
HOST = "172.17.0.1"  # IP del host vista desde el contenedor
PORT = 5005


class PwmUdpBridge(Node):
    def __init__(self):
        super().__init__("pwm_udp_bridge")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.create_subscription(Int16MultiArray, "pwm_values", self.on_pwm, 10)

    def on_pwm(self, msg):
        self.sock.sendto(json.dumps(list(msg.data)).encode(), (HOST, PORT))


def main():
    rclpy.init()
    rclpy.spin(PwmUdpBridge())


if __name__ == "__main__":
    main()