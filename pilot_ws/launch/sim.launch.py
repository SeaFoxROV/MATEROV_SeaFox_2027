from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    joystick_reader = Node(
        package="pilot_pkg",
        executable="joystick_reader",
        name="joystick_reader",
        output="screen",
    )

    joystick_to_twist = Node(
        package="pilot_pkg",
        executable="joystick_to_twist",
        name="joystick_to_twist",
        output="screen",
    )

    twist_to_pwm = Node(
        package="pilot_pkg",
        executable="twist_to_pwm",
        name="twist_to_pwm",
        output="screen",
    )

    pwm_to_gz_thrust = Node(
        package="pilot_pkg",
        executable="pwm_to_gz_thrust",
        name="pwm_to_gz_thrust",
        output="screen",
    )
    return LaunchDescription(
        [
            joystick_reader,
            joystick_to_twist,
            twist_to_pwm,
            pwm_to_gz_thrust,
        ]
    )
