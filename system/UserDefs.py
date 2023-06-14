from enum import IntEnum
from struct import pack, unpack
from dataclasses import dataclass

class State(IntEnum):
    READY = 0x00,
    RUNNING = 0x01,

class Command(IntEnum):
    READY = 0x00,
    PCR_RUN = 0x01,
    PCR_STOP = 0x02,
    FAN_ON = 0x03,
    FAN_OFF = 0x04,
    MAGNETO = 0x05,

@dataclass
class Action:
    label:str
    temp:int
    time:int

class TxBuffer:
    def __init__(self):
        self.cmd = Command.READY
        self.currentTargetTemp = 0

        self.startTemp = 0
        self.targetTemp = 0

        self.Kp = .0
        self.Ki = .0
        self.Kd = .0
        self.integralMax = .0

        self.ledControl = 0
        self.led_wg = 0
        self.led_r = 0
        self.led_g = 0
        self.led_b = 0
        self.led_wg_pwm = 0
        self.led_r_pwm = 0
        self.led_g_pwm = 0
        self.led_b_pwm = 0
        self.compensation = 0
        self.currentCycle = 0

    def getParams(self):
        return self.__dict__

    def setParams(self, **kwargs):
        for key, val in kwargs.items():
            self.__dict__[key] = val

    def toBytes(self):
        pid = pack('fff', self.Kp, self.Ki, self.Kd)
        integralMax = pack('f', self.integralMax)
        buffer = [0] # reserved 
        buffer += [self.cmd, int(self.currentTargetTemp),
                  int(self.startTemp), int(self.targetTemp),
                  self.Kp, self.Ki, self.Kd, self.integralMax,
                  self.ledControl, self.led_wg, self.led_r, self.led_g, self.led_b,
                  self.compensation,
                  self.led_wg_pwm, self.led_r_pwm, self.led_g_pwm, self.led_b_pwm,
                  self.currentCycle]

        buffer += [0] * 33 # 31 ~ 64 reserved
        # total 65 bytes
        return pack('>5B4f44B', *buffer)
class RxBuffer:
    def __init__(self):
        self.state = State.READY
        self.chamber = 0
        self.temperature = 0
        self.photodiode = 0
        self.currentError = 0
        self.requestData = 0
        self.targetArrival = False

    def setParams(self, read_data):
        self.state = int(read_data[0])
        self.chamber = (int(read_data[1]) & 0x0f) * 256 + int(read_data[2])
        self.temperature = unpack('f', read_data[3:7])[0]
        self.photodiode = (int(read_data[7]) & 0x0f) * 256 + int(read_data[8])
        self.currentError = int(read_data[9])
        self.requestData = int(read_data[10])
        self.targetArrival = bool(read_data[11])

    def getParams(self):
        return self.__dict__
