###############################################################################
# tmc5130_spi_interface.py
###############################################################################
import spidev

###############################################################################
# TMC5130 spi interface class
###############################################################################
class TMC5130SpiInterface(object):
  def __init__(self, bus, device, mode=3):
    self.spi = spidev.SpiDev()
    self.spi.open(bus, device)
    self.spi.max_speed_hz = 1000000
    self.spi.mode = mode
    self.spi.lsbfirst = False

  def xfer(self, data):
    return self.spi.xfer2(data)


#tmc5130_spi_interface.py
