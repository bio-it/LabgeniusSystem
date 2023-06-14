# -*- coding: utf-8 -*-
###############################################################################
# syringe_emulator.py
###############################################################################
import time
import magneto.actuators.tmc5130 as tmc5130


class SyringeEmulator():
  def __init__(self):
    self.busy_end_time = time.time()  # emulator only
    # self._load_bottom_position()
    print(f'syringe emulator initialized')

  def get_registers(self):
    registers = {r.name: r.value for r in tmc5130._registers}
    for name in registers.keys():
      no = tmc5130.name_to_no(name)
      value = self.get_register(no)
      registers[name] = value
    return registers

  def get_register(self, no):
    return 234

  def set_register(self, no, value):
    print(f"SyringeEmulator.set_register({no}, {value})")
    pass

  def get_pos(self):
      return 456.789

  def get_encoder_position(self):
      return 456.789

  def get_velocity(self):
    return 5.0

  def get_status(self):
    return 0xff

  def clear_status(self):
    print(f"SyringeEmulator.clear_status()")

  def jog(self, direction, shift=None):
    self.busy_end_time = time.time() + 2
    print(f"SyringeEmulator.jog({direction}, {shift})")

  # def move(self, position):
  #   self.busy_end_time = time.time() + 2
  #   print(f"SyringeEmulator.move({position})")

  def position(self, position):
    self.busy_end_time = time.time() + 2
    print(f"SyringeEmulator.position({position})")

  def volume(self, volume):
    self.busy_end_time = time.time() + 2
    print(f"SyringeEmulator.volume({volume})")

  def pumping(self, action, volume):
    self.busy_end_time = time.time() + 2
    print(f"SyringeEmulator.pumping({action}, {volume})")

  def stop(self):
    print(f"SyringeEmulator.stop()")
    self.busy_end_time_count = time.time()

  def wait(self):
    if time.time() >= self.busy_end_time:
      return False  # not waiting
    return True  # waiting

  def is_busy(self):
    return self.wait()

  def hard_stop(self):
      print(f"SyringeEmulator.hard_stop()")
      self.busy_end_time_count = time.time()

  def soft_stop(self):
      print(f"SyringeEmulator.soft_stop()")
      self.busy_end_time_count = time.time()

  def reset(self):
      print(f"SyringeEmulator.reset()")
      self.busy_end_time_count = time.time()

  def set_encoder_zero_position(self):
    print(f"SyringeEmulator.set_encoder_zero_position()")

  def update_encoder_multi_turn(self):
      pass

  # def go_until(self):
  #     self.busy_end_time = time.time() + 2
  #     print(f"SyringeEmulator.go_until()")

  # def release_switch(self):
  #     self.busy_end_time = time.time() + 2
  #     print(f"SyringeEmulator.release_switch()")

  # def home_shift(self):
  #     self.busy_end_time = time.time() + 2
  #     print(f"SyringeEmulator.home_shift()")

  def release_switch(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.release_switch()")

  def search_switch(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.search_switch()")

  def go_to_switch_latch_position(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.go_to_switch_latch_position()")

  def search_encoder_n_signal(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.search_encoder_n_signal()")

  def go_to_encoder_n_signal(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.go_to_encoder_n_signal()")

  def set_home_position(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.set_home_position()")

  def shift_from_home(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.shift_from_home()")

  def finish_home(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.finish_home()")

  def stop_home(self):
    self.busy_end_time = time.time() + 1
    print(f"SyringeEmulator.stop_home()")

  def save_bottom_position(self):
    print(f"SyringeEmulator.save_bottom_position()")


# syringe_emulator.py
