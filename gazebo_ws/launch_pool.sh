#!/usr/bin/env bash
# Lanza la piscina en Gazebo Fortress y, si ROS 2 está disponible, el ros_gz_bridge
# para los thrusters del ROV (ROS -> Gazebo).
DIR="$(cd "$(dirname "$0")" && pwd)"
# Con --network host, ign-transport puede elegir una interfaz bloqueada por el firewall
# del host y el GUI se queda en negro. Servidor y GUI corren aquí mismo: usar localhost.
export IGN_IP="${IGN_IP:-127.0.0.1}"
export IGN_GAZEBO_RESOURCE_PATH="$DIR/models${IGN_GAZEBO_RESOURCE_PATH:+:$IGN_GAZEBO_RESOURCE_PATH}"

if command -v ros2 >/dev/null 2>&1; then
  BRIDGE_ARGS=()
  for i in 0 1 2 3 4 5; do
    # ']' = sentido ROS -> Gazebo
    BRIDGE_ARGS+=("/model/seafox_rov/joint/thruster_${i}_joint/cmd_thrust@std_msgs/msg/Float64]ignition.msgs.Double")
  done
  ros2 run ros_gz_bridge parameter_bridge "${BRIDGE_ARGS[@]}" &
  BRIDGE_PID=$!
  trap 'kill $BRIDGE_PID 2>/dev/null' EXIT
else
  echo "ros2 no encontrado: se lanza Gazebo sin el bridge de thrusters" >&2
fi

ign gazebo -r "$DIR/worlds/pool.world" "$@"
