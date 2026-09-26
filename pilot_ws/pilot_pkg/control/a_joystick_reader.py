import pygame
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Int32  # NUEVO

pygame.init()


# [leftx,lefty,lefttrigger,rightx,righty,rightrigger,A,B,X,Y,LT,RT,BACK,SELECT,crossx,crossy]
class JoystickPublisher(Node):
    def __init__(self):
        super().__init__("joystick_publisher")
        self.publisher_ = self.create_publisher(Float32MultiArray, "joystick_data", 10)
        self.zero_publisher_ = self.create_publisher(Int32, "zero_value", 10)  # NUEVO
        self.zero = 1570  # NUEVO — contador inicializado en 1500
        self.prev_select = 0  # NUEVO — estado anterior del botón SELECT (índice 6)
        self.prev_back = 0  # NUEVO — estado anterior del botón BACK   (índice 7)
        self.joysticks = {}
        pygame.joystick.init()
        self.init_joysticks()

    def init_joysticks(self):
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.joysticks[joy.get_instance_id()] = joy
            print(f"Joystick {joy.get_instance_id()} connected")

    def publish_joystick_data(self):
        msg = Float32MultiArray()
        data = []

        for joystick in self.joysticks.values():
            for i in range(joystick.get_numaxes()):
                data.append(round(float(joystick.get_axis(i)), 3))

            for i in range(8):
                data.append(round(float(joystick.get_button(i)), 3))

            for i in range(joystick.get_numhats()):
                hat = joystick.get_hat(i)
                data.extend([round(float(hat[0]), 3), round(float(hat[1]), 3)])

            # NUEVO — detectar flanco de subida de SELECT (botón 6) y BACK (botón 7)
            select = joystick.get_button(6)
            back = joystick.get_button(7)

            if select == 1 and self.prev_select == 0:
                self.zero += 5
                self.get_logger().info(f"SELECT presionado → zero = {self.zero}")
                self._publish_zero()

            if back == 1 and self.prev_back == 0:
                self.zero -= 5
                self.get_logger().info(f"BACK presionado   → zero = {self.zero}")
                self._publish_zero()

            self.prev_select = select  # NUEVO
            self.prev_back = back  # NUEVO

        msg.data = data
        self.publisher_.publish(msg)

    def _publish_zero(self):  # NUEVO — método auxiliar para publicar zero
        zero_msg = Int32()
        zero_msg.data = self.zero
        self.zero_publisher_.publish(zero_msg)


def main():
    rclpy.init()
    node = JoystickPublisher()
    clock = pygame.time.Clock()

    try:
        while rclpy.ok():
            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    joy = pygame.joystick.Joystick(event.device_index)
                    joy.init()
                    node.joysticks[joy.get_instance_id()] = joy
                    print(f"Joystick {joy.get_instance_id()} connected")
                elif event.type == pygame.JOYDEVICEREMOVED:
                    del node.joysticks[event.instance_id]
                    print(f"Joystick {event.instance_id} disconnected")

            node.publish_joystick_data()
            clock.tick(30)

    except KeyboardInterrupt:
        pass
    finally:
        pygame.joystick.quit()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
