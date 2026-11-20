"""Puente para la simulación: convierte /pwm_values (salida de twist_to_pwm) en empuje
(Newtons) para los thrusters del ROV en Gazebo.

Publica std_msgs/Float64 en /model/seafox_rov/joint/thruster_N_joint/cmd_thrust.
El ros_gz_bridge (lo lanza gazebo_ws/launch_pool.sh) los pasa a Gazebo.

Si en la simulación un thruster empuja al revés, cambia su signo en THRUSTERS.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import Float64, Int16MultiArray, Int32

MODEL = "seafox_rov"

# índice en pwm_values -> (nombre del joint en model.sdf, signo)
THRUSTERS = {
    0: ("thruster_0_joint", 1.0),
    1: ("thruster_1_joint", 1.0),
    2: ("thruster_2_joint", 1.0),
    3: ("thruster_3_joint", 1.0),
    4: ("thruster_4_joint", 1.0),
    5: ("thruster_5_joint", 1.0),
}

# Modelo aproximado de un T200 a 12 V: lineal, con banda muerta
DEADBAND_US = 25
FULL_SCALE_US = 400  # 1500 ± 400 µs
MAX_FWD_N = 36.0
MAX_REV_N = 28.0


def pwm_to_newtons(offset_us: float) -> float:
    if abs(offset_us) <= DEADBAND_US:
        return 0.0
    frac = max(-1.0, min(1.0, offset_us / FULL_SCALE_US))
    return frac * (MAX_FWD_N if frac > 0 else MAX_REV_N)


class PwmToGzThrust(Node):
    def __init__(self):
        super().__init__("pwm_to_gz_thrust")
        self.zero = 1500

        self.pubs = {
            i: self.create_publisher(
                Float64, f"/model/{MODEL}/joint/{joint}/cmd_thrust", 10
            )
            for i, (joint, _) in THRUSTERS.items()
        }

        self.create_subscription(Int16MultiArray, "pwm_values", self.on_pwm, 10)
        zero_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.create_subscription(Int32, "zero_value", self.on_zero, zero_qos)

    def on_zero(self, msg: Int32):
        self.zero = msg.data

    def on_pwm(self, msg: Int16MultiArray):
        for i, (_, sign) in THRUSTERS.items():
            if i >= len(msg.data):
                continue
            out = Float64()
            out.data = sign * pwm_to_newtons(msg.data[i] - self.zero)
            self.pubs[i].publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = PwmToGzThrust()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
