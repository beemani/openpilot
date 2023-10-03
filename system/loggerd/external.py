#!/usr/bin/env python3
import subprocess
import os
import time
import threading


def is_mounted(mount_point):
  # Check if mount_point is in the list of current mounts
  result_output = subprocess.check_output(["mount"], universal_newlines=True)
  if mount_point not in result_output:
    return False

  # Test if we can read from the mount
  try:
    os.listdir(mount_point)
  except OSError:
    # If we can't read from the mount, it's likely the device was unplugged without unmounting
    subprocess.call(["umount", "-f", mount_point])
    return False

  return True


def detect_usb_or_nvme():
  result_output = subprocess.check_output(["lsblk", "-o", "NAME,TYPE,MOUNTPOINT,TRAN"], universal_newlines=True)
  lines = result_output.splitlines()

  # Filter out only USB and NVMe devices
  devices = [line.split()[0] for line in lines if "usb" in line or "nvme" in line]

  # Check lsusb to exclude ethernet adapters or any other non-storage USB devices
  lsusb_output = subprocess.check_output(["lsusb"], universal_newlines=True)
  for device in devices:
    if 'Ethernet' in lsusb_output or any(other_type in lsusb_output for other_type in ["Network", "Communications"]):
      devices.remove(device)

  if not devices:
    print("No appropriate devices detected.")
    return None

  if len(devices) > 1:
    print("Multiple devices detected. Please ensure only the desired device is connected.")
    return None

  return "/dev/{}".format(devices[0])


def format_and_mount(device):
  partition = device + "1"

  # If the specific directory structure doesn't exist, format the device
  if not os.path.exists("/data/external/media/0/realdata/"):
    # Unmount the device if it's mounted
    subprocess.call(["umount", partition])

    # Delete all partitions and create a new one
    subprocess.call(["sfdisk", "--delete", device])
    subprocess.call(["bash", "-c", "echo ';' | sfdisk {}".format(device)])

    # Format the new partition to ext4
    subprocess.call(["mkfs.ext4", "-F", partition])

  # Mount the device
  if not os.path.exists("/data/external"):
    os.mkdir("/data/external")
  subprocess.call(["mount", partition, "/data/external"])

  # Create the directory structure if it doesn't exist
  nested_dir = "/data/external/media/0/realdata/"
  if not os.path.exists(nested_dir):
    os.makedirs(nested_dir)


def external_thread(exit_event):
  while not exit_event.is_set():
    mount_point = "/data/external"
    if is_mounted(mount_point):
      print("{} is currently mounted.".format(mount_point))
      time.sleep(30)
    else:
      device = detect_usb_or_nvme()
      if device:
        format_and_mount(device)
        time.sleep(30)  # wait for 30 seconds after formatting and mounting

    time.sleep(30)  # check every 30 seconds for a new device


def main():
  external_thread(threading.Event())


if __name__ == "__main__":
  main()
