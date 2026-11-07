#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
export IGN_GAZEBO_RESOURCE_PATH="$DIR/models${IGN_GAZEBO_RESOURCE_PATH:+:$IGN_GAZEBO_RESOURCE_PATH}"
exec ign gazebo -r "$DIR/worlds/pool.world" "$@"
