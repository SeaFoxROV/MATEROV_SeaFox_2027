import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray, Int16MultiArray, Int32  # NUEVO: Int32
from rclpy.qos import QoSProfile, DurabilityPolicy


class TwistToPWM(Node):
    STEP = 500
    deadzone = 40
    
    YAW_GAIN = 0.6

    def __init__(self):
        super().__init__("twist_to_pwm")

        self.zero = 1500  # NUEVO: ya no es class variable, inicia en 1500

        # 6 thrusters + 2 extras (ej: gripper)
        self.pwm_setpoints = [1500] * 6
        self.pwm_values = [1500] * 8

        self.create_subscription(Twist, "/desired_twist", self.setpoint_callback, 10)
        self.create_subscription(
            Float32MultiArray, "/joystick_data", self.gripper_callback, 10
        )
        # TRANSIENT_LOCAL: recibe el ultimo zero publicado aunque este nodo arranque despues
        zero_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.create_subscription(Int32, "zero_value", self.zero_callback, zero_qos)

        self.pwm_pub = self.create_publisher(Int16MultiArray, "pwm_values", 10)

        self.create_timer(0.1, self.pwm_callback)

    # NUEVO — actualiza zero cuando llega un mensaje del joystick publisher
    def zero_callback(self, msg: Int32):
        self.zero = msg.data
        self.get_logger().info(f"zero actualizado: {self.zero}")

    # ---------------- UTIL ----------------
    def normalize(self, val, scale=400):
        return int(val * scale)

    def clamp(self, val, min_v=1200, max_v=1800):
        return max(min(val, max_v), min_v)

    # ---------------- GRIPPER ----------------
    def gripper_callback(self, msg: Float32MultiArray):
        try:
            self.pwm_values[7] = self.zero
            if msg.data[11] == 1.0:
                self.pwm_values[7] = 1200
            elif msg.data[10] == 1.0:
                self.pwm_values[7] = 1800

        except:
            pass

        try:
            if msg.data[-1] == -1.0:
                self.pwm_values[6] = 1800
            elif msg.data[-1] == 1.0:
                self.pwm_values[6] = 1200
            else:
                self.pwm_values[6] = self.zero
        except:
            pass

    # ---------------- MIXING ----------------
    def setpoint_callback(self, msg: Twist):

        base = self.zero

        # Rango util de los horizontales alrededor del neutro (230 con zero=1570).
        # max(0, ...) evita invertir los thrusters si zero se sale de 1200-1800.
        limit = max(0, min(base - 1200, 1800 - base))

        # Horizontales escalados al limite real: 100% del stick = 100% del empuje
        x = -self.normalize(msg.linear.x, limit)
        y = self.normalize(-msg.linear.y, limit)
        yaw = self.normalize(msg.angular.z, limit * self.YAW_GAIN)

        # Verticales: sin cambios
        z = -self.normalize(msg.linear.z)
        roll = self.normalize(msg.angular.x)

        # Verticales (1 y 4)
        self.pwm_setpoints[1] = self.clamp(base + z - roll, 1100, 1900)
        self.pwm_setpoints[4] = self.clamp(base - z - roll, 1100, 1900)

        # Horizontales (0, 2, 3, 5): se calcula solo el desplazamiento respecto a base
        offsets = {
            # pitch NO se mezcla aqui: en los horizontales tendria el mismo
            # patron de signos que x (seria traslacion, no rotacion)
            0: -x + y + yaw,
            2: x - y + yaw,
            3: -x - y - yaw,
            5: x + y - yaw,
        }

        # Si alguno se pasa del rango, se escala todo en la misma proporción
        max_off = max(abs(v) for v in offsets.values())
        if max_off > limit:
            k = limit / max_off
            offsets = {i: v * k for i, v in offsets.items()}

        for i, off in offsets.items():
            self.pwm_setpoints[i] = int(base + off)

        # Zona muerta
        for i in range(6):
            if abs(self.pwm_setpoints[i] - base) < self.deadzone:
                self.pwm_setpoints[i] = base

    # ---------------- OUTPUT ----------------
    def pwm_callback(self):

        for i in range(6):
            diff = self.pwm_setpoints[i] - self.pwm_values[i]

            if abs(diff) <= self.STEP:
                self.pwm_values[i] = self.pwm_setpoints[i]
            elif diff > 0:
                self.pwm_values[i] += self.STEP
            else:
                self.pwm_values[i] -= self.STEP

        msg = Int16MultiArray()
        msg.data = self.pwm_values
        self.pwm_pub.publish(msg)


# ---------------- MAIN ----------------
def main(args=None):
    rclpy.init(args=args)
    node = TwistToPWM()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
