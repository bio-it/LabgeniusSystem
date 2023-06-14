# -*- coding: utf-8 -*-
###############################################################################
# magnet_emulator.py
###############################################################################
import time


class MagnetEmulator():
  def __init__(self):
    self.busy_end_time = time.time()  # dummy only
    print(f'magnet emulator initialized')

  def on(self):
    self.busy_end_time = time.time() + 2
    print(f"MagnetEmulator.on()")

  def off(self):
    self.busy_end_time = time.time() + 2
    print(f"MagnetEmulator.off()")

  def home(self):
    self.busy_end_time = time.time() + 2
    print(f"MagnetEmulator.home()")

  def stop(self):
      self.busy_end_time_count = time.time()
      print(f"MagnetEmulator.stop()")

  def wait(self):
    if time.time() >= self.busy_end_time:
        return False # not waiting
    return True # waiting

  def is_busy(self):
    return self.wait()

#magnet_emulator.py
