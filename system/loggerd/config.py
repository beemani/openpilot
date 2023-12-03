import os
from openpilot.system.hardware.hw import Paths


CAMERA_FPS = 20
SEGMENT_LENGTH = 60

STATS_DIR_FILE_LIMIT = 10000
STATS_SOCKET = "ipc:///tmp/stats"
STATS_FLUSH_TIME_S = 60

PATH_DICT = {
    "internal": Paths.log_root(),
    "external": Paths.log_root_external()
}

def get_available_percent(default=None, path_type="internal"):
  try:
    statvfs = os.statvfs(PATH_DICT[path_type])
    available_percent = 100.0 * statvfs.f_bavail / statvfs.f_blocks
  except OSError:
    available_percent = default

  return available_percent


def get_available_bytes(default=None, path_type="internal"):
  try:
    statvfs = os.statvfs(PATH_DICT[path_type])
    available_bytes = statvfs.f_bavail * statvfs.f_frsize
  except OSError:
    available_bytes = default

  return available_bytes
