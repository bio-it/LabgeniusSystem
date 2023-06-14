# -*- coding: utf-8 -*-
###############################################################################
# chamber_emulator.py
###############################################################################
import magneto.actuators.tmc5130 as tmc5130
import time


class ChamberEmulator():
  def __init__(self):
    self.busy_end_time = time.time()  # emulator only
    print(f'chamber emulator initialized')
    # for ch in range(1, 26+1):
    #     print(f'ch no={ch}, ch pos={self._no_to_deggree(ch)}')

  def get_registers(self):
    registers = {r.name: r.value for r in tmc5130._registers}
    for name in registers.keys():
      no = tmc5130.name_to_no(name)
      value = self.get_register(no)
      registers[name] = value
    return registers

  def get_register(self, no):
    return 123

  def set_register(self, no, value):
    pass

  def get_min_chamber_no(self):
    return 1

  def get_max_chamber_no(self):
    return 13

  def get_pos(self):
    return 123.456

  def get_encoder_position(self):
      return 234.567

  def get_velocity(self):
    return 720.0

  def set_encoder_zero_position(self):
      print(f"ChamberEmulator.set_encoder_zero_position()")

  def update_encoder_multi_turn(self):
      pass

  def set_pos(self, pos):
    print(f"ChamberEmulator.set_pos())")

  def get_status(self):
    return 0xffff

  def jog(self, direction, shift=None):
    self.busy_end_time = time.time() + 2
    print(f"ChamberEmulator.jog({direction}, {shift})")

  def goto(self, no):
    self.busy_end_time = time.time() + 2
    print(f"ChamberEmulator.goto({no}))")

  def position(self, position):
    self.busy_end_time = time.time() + 2
    print(f"ChamberEmulator.position({position}))")

  def hard_stop(self):
      print(f"ChamberEmulator.hard_stop()")
      self.busy_end_time = time.time()

  def soft_stop(self):
      print(f"ChamberEmulator.soft_stop()")
      self.busy_end_time = time.time()

  def reset(self):
      print(f"ChamberEmulator.reset()")
      self.busy_end_time = time.time()

  def clear_status(self):
      print(f"ChamberEmulator.clear_status()")

  def stop(self):
    print(f"ChamberEmulator.stop()")
    self.busy_end_time = time.time()

  def wait(self):
    if time.time() >= self.busy_end_time:  # emulator only
      return False  # not waiting
    return True  # waiting

  def is_busy(self):
    return self.wait()

  def goto_home(self):
      self.busy_end_time = time.time() + 2
      print(f"ChamberEmulator.goto_home())")

  def sync_with_encoder_position(self):
      print(
          f'chamber sync_with_encoder_position, enc pos={self.get_encoder_position()}, pos={self.get_pos()}')

  def set_driver_position_to_zero(self):
      print(f"ChamberEmulator.set_driver_position_to_zero()")

  def search_encoder_n_signal(self):
    self.busy_end_time = time.time() + 1
    print(f"ChamberEmulator.search_encoder_n_signal()")

  def go_to_encoder_n_signal(self):
    self.busy_end_time = time.time() + 1
    print(f"ChamberEmulator.go_to_encoder_n_signal()")

  def go_to_offset_position(self):
    self.busy_end_time = time.time() + 1
    print(f"ChamberEmulator.go_to_offset_position()")

  def set_home_position(self):
    self.busy_end_time = time.time() + 1
    print(f"ChamberEmulator.set_home_position()")

  def shift_from_home(self):
    self.busy_end_time = time.time() + 1
    print(f"ChamberEmulator.shift_from_home()")

  def finish_home(self):
    self.busy_end_time = time.time() + 1
    print(f"ChamberEmulator.finish_home()")

  def save_offset_position(self):
    print(f"ChamberEmulator.save_offset_position()")

# chamber_emulator.py
