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
            # "send_coords = turtlebot_pkg.send_coords:main",
            # "turtle_go_to_coords = turtlebot_pkg.turtle_go_to_coords:main",
        ],
    },
)
