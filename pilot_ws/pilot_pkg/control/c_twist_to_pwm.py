import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray, Int16MultiArray, Int32  # NUEVO: Int32


class TwistToPWM(Node):
    STEP = 500
    deadzone = 40

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
        self.create_subscription(Int32, "zero_value", self.zero_callback, 10)  # NUEVO

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

        x = -self.normalize(msg.linear.x)
        y = self.normalize(-msg.linear.y)
        z = -self.normalize(msg.linear.z)

        roll = self.normalize(msg.angular.x)
        pitch = self.normalize(msg.angular.y)
        yaw = self.normalize(msg.angular.z)

        base = self.zero

        self.pwm_setpoints[0] = self.clamp(base + z - roll, 1100, 1900)
        self.pwm_setpoints[1] = base + x + y + yaw - pitch
        self.pwm_setpoints[2] = base + x - y + yaw + pitch
        self.pwm_setpoints[3] = base + x - y - yaw - pitch
        self.pwm_setpoints[4] = self.clamp(base - z - roll, 1100, 1900)
        self.pwm_setpoints[5] = base + x + y - yaw + pitch

        for i in range(6):
            if i == 0 or i == 4:
                if self.pwm_setpoints[i] > (
                    self.zero - self.deadzone
                ) and self.pwm_setpoints[i] < (self.zero + self.deadzone):
                    self.pwm_setpoints[i] = self.zero
                    self.pwm_setpoints[i] = self.clamp(self.pwm_setpoints[i])
                self.pwm_setpoints[1] = self.clamp(self.pwm_setpoints[1], 1100, 1900)
                self.pwm_setpoints[4] = self.clamp(self.pwm_setpoints[4], 1100, 1900)
            else:
                self.pwm_setpoints[i] = self.clamp(self.pwm_setpoints[i])
                if self.pwm_setpoints[i] > (
                    self.zero - self.deadzone
                ) and self.pwm_setpoints[i] < (self.zero + self.deadzone):
                    self.pwm_setpoints[i] = self.zero

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
