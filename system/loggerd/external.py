#!/usr/bin/env python3
import subprocess
import os
import time
import threading


def is_mounted(mount_point):
  # Check if mount_point is in the list of current mounts
  result = subprocess.run(["mount"], capture_output=True, text=True)
  if mount_point not in result.stdout:
    return False
  
  # Test if we can read from the mount
  try:
    os.listdir(mount_point)
  except OSError:
    # If we can't read from the mount, it's likely the device was unplugged without unmounting
    subprocess.run(["umount", "-f", mount_point], check=False)
    return False
  
  return True


def detect_usb_or_nvme():
  result = subprocess.run(["lsblk", "-o", "NAME,TYPE,MOUNTPOINT,TRAN"], capture_output=True, text=True)
  lines = result.stdout.splitlines()

  # Filter out only USB and NVMe devices
  devices = [line.split()[0] for line in lines if "usb" in line or "nvme" in line]

  # Check lsusb to exclude ethernet adapters or any other non-storage USB devices
  lsusb_output = subprocess.run(["lsusb"], capture_output=True, text=True).stdout
  for device in devices:
    if 'Ethernet' in lsusb_output or any(other_type in lsusb_output for other_type in ["Network", "Communications"]):
      devices.remove(device)

  if not devices:
    print("No appropriate devices detected.")
    return None

  if len(devices) > 1:
    print("Multiple devices detected. Please ensure only the desired device is connected.")
    return None

  return f"/dev/{devices[0]}"


def format_and_mount(device):
  partition = device + "1"

  # If the specific directory structure doesn't exist, format the device
  if not os.path.exists("/data_external/media/0/realdata/"):
    # Unmount the device if it's mounted
    subprocess.run(["umount", partition], check=False)

    # Delete all partitions and create a new one
    subprocess.run(["sfdisk", "--delete", device], check=True)
    subprocess.run(["echo", ";", "|", "sfdisk", device], check=True)

    # Format the new partition to ext4
    subprocess.run(["mkfs.ext4", partition], check=True)

  # Mount the device
  if not os.path.exists("/data_external"):
    os.mkdir("/data_external")
  subprocess.run(["mount", partition, "/data_external"], check=False)  # Removed check=True to handle scenarios where it's already mounted

  # Create the directory structure if it doesn't exist
  nested_dir = "/data_external/media/0/realdata/"
  if not os.path.exists(nested_dir):
    os.makedirs(nested_dir)


def external_thread(exit_event):
  while not exit_event.is_set():
    mount_point = "/data_external"
    if is_mounted(mount_point):
      print(f"{mount_point} is currently mounted.")
      time.sleep(30)
    else:
      device = detect_usb_or_nvme()
      if device:
        format_and_mount(device)
        time.sleep(30)  # wait for 30 seconds after formatting and mounting

    exit_event.wait(30)  # check every 30 seconds for a new device


def main():
  external_thread(threading.Event())


if __name__ == "__main__":
  main()
