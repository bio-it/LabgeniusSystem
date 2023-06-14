# -*- coding: utf-8 -*-
###############################################################################
# amt203.py
# with sc18is602b interface
# SERIES: AMT20 │ DESCRIPTION: MODULAR ABSOLUTE ENCODER
# AMT203-V
###############################################################################
from time import sleep
# import time
# import math

# def init_spi(bus, device, mode):
#     spi = spidev.SpiDev()
#     spi.open(bus, device)
#     # spi.max_speed_hz = 1000000
#     spi.max_speed_hz = 200000    # 200 kHz

#     ''' # @ 10 Aug. GitH. 
#     # sampling rate 1000 Hz
#     # spi.max_speed_hz = 1000000 # ng
#     # spi.max_speed_hz = 500000 # ng
#     # spi.max_speed_hz = 300000 # ng
#     # spi.max_speed_hz = 200000 # ng
#     # spi.max_speed_hz = 100000 # ok
#     # sampling rate 100 Hz
#     # spi.max_speed_hz = 1000000 # ng
#     # spi.max_speed_hz = 500000 # ng
#     # spi.max_speed_hz = 300000 # ng
#     spi.max_speed_hz = 200000 # ok
#     # spi.max_speed_hz = 100000 # ok
#     # spi.max_speed_hz = 100000 # ok
    
#     # @ 10 Aug. GitH. // '''


#     spi.mode = mode
#     spi.lsbfirst = False     # "SPI.beginTransaction(SPISettings(500000, MSBFIRST, SPI_MODE0));"
#     return spi


# optic spi test
# device = 3 (gpio 27)
# L6470 spi mode = 3
#spi = L6470SpiInterface(0, 3, 3)


class AMT203(object):
    def __init__(self, interface, reverse_dir=False):
        self.interface = interface
        self.reverse_dir = reverse_dir

        self.timoutLimit = 10       # this will be our SPI timout limit
        # self.timoutLimit = 1000   #@ 10 Aug. GitH.    # this will be our SPI timout limit

        self.nop = 0x00             # no operation  //SPI commands used by the AMT20
        self.rd_pos = 0x10          # read position
        self.set_zero_point = 0x70  # set zero point
 
        self.data = 0               # this will hold our returned data from the AMT20
        self.timeoutCounter = 0     # our timeout incrementer
        self.current_amt20_pos = 0  # this 16 bit variable will hold our 12-bit position    

        self._start()       # Initialize Device (task) blow
        print(f'{"AMT203 abs encoder_SPI_initialized"}')

    # • Tracking mode:
    # 1. MCU 12 bit position register is updated from every 48 μs.
    # 2. For accurate position information without the 48 μs incremental outputs A/B can be used for tracking. These outputs are
    #    operational up to 8000 RPM without speed error.
    # 3. When using the incremental output there also is a Z index pulse that occurs once per turn.

    # Command 0x00: nop_a5 (no operation)
    # Command 0x10: rd_pos (read position)
    # This command causes a read of the current position.
    # To read position this sequence should be followed:
    # 1. Master sends rd_pos command. Encoder responds with idle character.
    # 2. Continue sending nop_a5 command while encoder response is 0xA5
    # 3. If response was 0x10 (rd_pos), send nop_a5 and receive MSB position (lower 4 bits of this byte are the upper 4 of the 12-bit
    # position)
    # 4. Send second nop_a5 command and receive LSB position (lower 8 bits of 12-bit positon)
    # Note that it is possible to overlap commands. For instance, instead of issuing nop_a5 for steps 3 and 4, you could begin another read
    # position sequence since the position data is already in the buffer. The read and write FIFOs for the streams are 16 bytes long and it is
    # up to the user to avoid overflow.
    def read_abs_pos(self):
        self.timeoutCounter = 0
        self.data = self.interface.xfer_cmd(self.rd_pos)    #send the rd_pos command to have the AMT20 begin obtaining the current position
        self.data = self.interface.xfer_cmd(self.nop)
        # print(self.timeoutCounter)

        while (self.data != self.rd_pos) and ((self.timeoutCounter) < self.timoutLimit):   # we need to send nop commands while the encoder processes the current position. We
            self.timeoutCounter += 1
            # print(self.timeoutCounter)
            self.data = self.interface.xfer_cmd(self.nop)                                        # will keep sending them until the AMT20 echos the rd_pos command, or our timeout is reached.
            # sleep(0.001)

        if (self.timeoutCounter < self.timoutLimit):  #rd_pos echo received
            # We received the rd_pos echo which means the next two bytes are the current encoder position.
            # Since the AMT20 is a 12 bit encoder we will throw away the upper 4 bits by masking.
        
            # Obtain the upper position byte. Mask it since we only need it's lower 4 bits, and then
            # shift it left 8 bits to make room for the lower byte.
            self.current_amt20_pos = (self.interface.xfer_cmd(self.nop) & 0x0F) << 8
            # OR the next byte with the current position
            self.current_amt20_pos = self.current_amt20_pos | self.interface.xfer_cmd(self.nop)

        else:    #timeout reached
            # This means we had a problem with the encoder, most likely a lost connection. For our
            # purposes we will alert the user via the serial connection, and then stay here forever.
            # print(f'Error obtaining position.')
            # print(f'Reset AMT20-V to restart program.')
            # while(true);
            self.current_amt20_pos = -1

        return (self.current_amt20_pos, self.timeoutCounter)    # @ 11 Aug. GitH. _ Impl. returns "self.timeoutCounter"
    def get_pos(self):
        position, _ = self.read_abs_pos()
        if self.reverse_dir:
            position = 4096 - position
            if position >= 4096:
                position = 0
        return position

    # Command 0x70: set_zero_point (zero set)
    #   This command sets the current position to zero and saves this setting in the EEPROM.
    #     To set the zero point this sequence should be followed:
    #     1. Send set_zero_point command
    #     2. Send nop_a5 command while response is not 0x80
    #     3. A response of 0x80 means that the zero set was successful and the new position offset is stored in EEPROM.
    #     4. The encoder must be power cycled. If the encoder is not power cycled, the position values will not be calculated
    def set_zero_position(self):      
        self.data = self.interface.xfer_cmd(self.set_zero_point)    #send the rd_pos command to have the AMT20 begin obtaining the current position
        self.timeoutCounter = 0
        while (self.data != 0x80) and ((self.timeoutCounter) < self.timoutLimit):   # we need to send nop commands while the encoder processes the current position. We
            self.timeoutCounter += 1
            # print(self.timeoutCounter)
            self.data = self.interface.xfer_cmd(self.nop)                                        # will keep sending them until the AMT20 echos the rd_pos command, or our timeout is reached.
            sleep(0.001)
        if (self.timeoutCounter < self.timoutLimit):
            pass
        else:    #timeout reached
            print(f'AMT20-V set zero point timeouted.')

    #######################################
    # private functions
    #######################################
    # • Initialization mode: At power up the encoder goes through an initiation and stabilization procedure. This includes microprocessor
    #   stabilization and the program for getting the absolute start position. This takes less than 100 milliseconds.
    def _start(self):
        sleep(0.1)


# E.O.F _ amt203.py

# Serial.write("Current position: ");
# Serial.print(currentPosition, DEC); //current position in decimal
# //    Serial.write("\t 0x");
# //    Serial.print(currentPosition, HEX); //current position in hexidecimal
# //    Serial.write("\t 0b");
# //    Serial.print(currentPosition, BIN); //current position in binary
# Serial.write("\n");


''' @ 7 Jul
# optic spi test
# device = 3 (gpio 27)    # Hdr.pin> 13
# L6470 spi mode = 3
spi = L6470SpiInterface(0, 3, 3)
//
# real chamber
# device = 2 (gpio 17)  # Hdr.pin> 11
# L6470 spi mode = 3
spi = L6470SpiInterface(0, 2, 3)
//
@ on 16 Jun
  spi-cs-extend.dts    // cs-gpios = <&gpio 8 1>, <&gpio 7 1>, <&gpio 17 1>, <&gpio 27 1>, <&gpio 22 1>;   # Hdr.pin> 15
'''