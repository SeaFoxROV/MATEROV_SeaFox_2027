from setuptools import find_packages, setup
import os
from glob import glob


package_name = "pilot_pkg"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        # Required for ament to find the package
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        # package.xml
        ("share/" + package_name, ["package.xml"]),
        # Launch files
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Your Name",
    maintainer_email="you@example.com",
    description="Turtlebot package",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "joystick_reader = pilot_pkg.control.a_joystick_reader:main",
            "joystick_to_twist = pilot_pkg.control.b_joystick_to_twist:main",
            "twist_to_pwm = pilot_pkg.control.c_twist_to_pwm:main",
            "udp_publisher = pilot_pkg.communication.udp_publisher:main",
        ],
    },
)
