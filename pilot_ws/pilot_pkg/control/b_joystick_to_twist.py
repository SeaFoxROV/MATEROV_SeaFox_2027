import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32MultiArray, Bool


class MotionController(Node):
    def __init__(self):
        super().__init__("motion_controller_node")
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, "/desired_twist", 10)

        self.gripper_pub = self.create_publisher(Float32MultiArray, "/gripper_pwm", 10)

        # Subscribers
        self.create_subscription(
            Float32MultiArray, "/joystick_data", self.joy_callback, 100
        )

        self.last_user_velocity_command = Twist()

        self.pwms = Float32MultiArray()

        self.pwms.data = [1500.0] * 3

        self.last_command_time = self.get_clock().now()
        self.last_joy = self.get_clock().now()

        self.timer = self.create_timer(1.0 / 30.0, self.motion)

        self.create_timer(1.0, self.check_connection)

    def check_connection(self):
        joy_elapsed = (self.get_clock().now() - self.last_joy).nanoseconds / 1e9
        if joy_elapsed > 1.0:
            self.get_logger().error("Sin señal de joystick")

    def joy_callback(self, msg: Joy):

        if len(msg.data) < 6:
            return
        self.last_joy = self.get_clock().now()

        # [leftx,lefty,lefttrigger,rightx,righty,rightrigger,A,B,X,Y,LT,RT,BACK,SELECT,crossx,crossy]
        # Map joystick axes to velocity command
        left_joy_x = msg.data[0]  # Sides
        left_joy_y = msg.data[1]  # Forward/Back
        left_trigger = msg.data[2]  # doiwn
        right_trigger = msg.data[5]  # jup   Z
        right_joy_x = msg.data[3]
        right_joy_y = msg.data[4]
        cross_x = msg.data[14]

        self.last_user_velocity_command.linear.x = -left_joy_y
        self.last_user_velocity_command.linear.y = left_joy_x

        if right_trigger > -0.4:
            right_trigger = 1
        if left_trigger > -0.4:
            left_trigger = 1
        self.last_user_velocity_command.linear.z = (right_trigger - left_trigger) / 2

        self.last_user_velocity_command.angular.z = right_joy_x
        self.last_user_velocity_command.angular.y = right_joy_y
        self.last_user_velocity_command.angular.x = cross_x

        self.pwms.data[0] = 1500

        self.last_command_time = self.get_clock().now()

    def motion(self):
        now = self.get_clock().now()
        elapsed = (now - self.last_command_time).nanoseconds / 1e9
        if elapsed > 1.0:
            self.last_user_velocity_command = Twist()

        cmd_vel = Twist()

        cmd_vel.linear.x = self.last_user_velocity_command.linear.x
        cmd_vel.linear.y = -self.last_user_velocity_command.linear.y
        cmd_vel.linear.z = self.last_user_velocity_command.linear.z

        cmd_vel.angular.x = self.last_user_velocity_command.angular.x
        cmd_vel.angular.y = self.last_user_velocity_command.angular.y
        cmd_vel.angular.z = self.last_user_velocity_command.angular.z

        self.gripper_pub.publish(self.pwms)

        self.cmd_vel_pub.publish(cmd_vel)


def main(args=None):
    rclpy.init(args=args)
    node = MotionController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        del node
        rclpy.shutdown()


if __name__ == "__main__":
    main()
