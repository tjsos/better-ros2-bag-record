#!/usr/bin/env python3

# This script runs ros2 bag record and on closing saves the 
# params (.yaml) from the packages you define from the install folder
# of the ros2 workspace & saves it alongside the bag that you just recorded.

# To run this script from anywhere using bash.
# add the following to the .bashrc

# alias ros_record="python3 <location of this file>"
# source .bashrc

import subprocess
import time
import yaml
from pathlib import Path
import os

# User Defined Params
WORKSPACE_NAME = "auv_ws"
PACKAGE_NAMES = ["alpha_rise_bringup", "alpha_rise_config"]

def start_rosbag_record():
    print("[INFO] Starting 'ros2 bag record -a'...")
    rosbag_proc = subprocess.Popen(
        ["ros2", "bag", "record", "-a"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return rosbag_proc

def find_newest_rosbag2_dir(search_path=Path.cwd(), timeout=10):
    print("[INFO] Searching for new rosbag2 directory...")
    latest_dir = None
    latest_time = 0

    for _ in range(timeout):
        for entry in search_path.iterdir():
            if entry.is_dir() and entry.name.startswith("rosbag2_"):
                mtime = entry.stat().st_mtime
                if mtime > latest_time:
                    latest_time = mtime
                    latest_dir = entry
        if latest_dir:
            return latest_dir
        time.sleep(1)

    raise FileNotFoundError("Could not find rosbag2 directory.")

def find_all_config_dirs(package_path: Path) -> list[Path]:
    # Find subdirectories ending with "config"
    return [p for p in package_path.iterdir() if p.is_dir() and p.name.endswith("config")]

def merge_yaml_files_from_multiple_configs(config_paths: list[Path], output_path: Path):
    yaml_files = []
    for config_root in config_paths:
        if config_root.exists():
            found = list(config_root.rglob("*.yaml"))
            yaml_files.extend(found)
        else:
            print(f"[WARNING] Config path not found: {config_root}")

    if not yaml_files:
        raise FileNotFoundError("No YAML files found in any provided config path.")

    print("[INFO] Found YAML files:")
    # for f in yaml_files:
    #     print(f"  - {f}")

    master_data = {}
    for yfile in yaml_files:
        try:
            with open(yfile, 'r') as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    master_data.update(data)
                else:
                    print(f"[WARNING] Skipping non-dictionary YAML file: {yfile}")
        except yaml.YAMLError as e:
            print(f"[ERROR] Failed to parse {yfile}: {e}")

    output_file = output_path / "params.yaml"
    with open(output_file, 'w') as f:
        yaml.dump(master_data, f)

    print(f"[INFO] Merged YAML saved to: {output_file}")

def main():
    user_name = os.getlogin()

    # Create full paths like: /home/user/auv_ws/install/<pkg>/share/<pkg>
    base_path = Path(f"/home/{user_name}/{WORKSPACE_NAME}/install")
    package_paths = [
        base_path / pkg / "share" / pkg for pkg in PACKAGE_NAMES
]
    # Find all directories ending with 'config' in all packages
    config_paths = [
        config_dir
        for pkg_path in package_paths
        for config_dir in find_all_config_dirs(pkg_path)
    ]

    if not config_paths:
        print("[ERROR] No config directories ending with 'config' found in specified packages.")
        return

    try:
        rosbag_proc = start_rosbag_record()
        input("[INFO] Press Enter to stop recording and merge YAML files...")

        rosbag_proc.terminate()
        rosbag_proc.wait()
        print("[INFO] ros2 bag record stopped.")

        bag_dir = find_newest_rosbag2_dir()
        print(f"[INFO] Detected bag folder: {bag_dir}")

        merge_yaml_files_from_multiple_configs(config_paths, bag_dir)

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
