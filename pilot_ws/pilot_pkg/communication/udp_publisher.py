import sys
import socket

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray


ESP_IP = "192.168.1.21"
ESP_PORT = 8888

TIMER_MS = 70  # ms


class PwmUdpSender(Node):
    def __init__(self):
        super().__init__("pwm_udp_sender")

        self.declare_parameter("esp_ip", ESP_IP)
        self.declare_parameter("esp_port", ESP_PORT)

        ip = self.get_parameter("esp_ip").get_parameter_value().string_value
        port = self.get_parameter("esp_port").get_parameter_value().integer_value

        self.target = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_pwm = [1500] * 6  # neutro hasta recibir algo

        self.create_subscription(Int16MultiArray, "pwm_values", self.pwm_callback, 10)

        self.create_timer(TIMER_MS / 1000.0, self.send_udp)

        self.get_logger().info(f"PWM UDP sender listo → {ip}:{port}  @ {TIMER_MS}ms")

    def pwm_callback(self, msg: Int16MultiArray):
        """Guarda los últimos valores recibidos."""
        self.last_pwm = list(msg.data)

    def send_udp(self):
        """Manda los últimos PWM por UDP cada TIMER_MS ms."""

        payload = ";".join(str(v) for v in self.last_pwm)
        # print(payload)
        self.sock.sendto(payload.encode(), self.target)
        self.get_logger().debug(f"Enviado: {payload}")

    def __del__(self):
        neutral = ";".join(["1500"] * 6)
        try:
            self.sock.sendto(neutral.encode(), self.target)
        except Exception:
            pass
        self.sock.close()


def main(args=None):
    rclpy.init(args=args)
    node = PwmUdpSender()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        del node
        rclpy.shutdown()


if __name__ == "__main__":
    main(sys.argv)
