from enum import Enum
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.od_defines import *

class NMTD(Enum):
    INIT = 0
    STOPPED = 4
    OPERATIONAL = 5
    SLEEP = 80
    STANDBY = 96
    PRE_OPERATIONAL = 127

class TCS(Enum): #Thruster Control State
    """
        Thruster Control State, enums of the various states of the PPU.
    """
    TCS_CO_INVALID              = 0x0
    TCS_CO_INIT                 = 0x1
    TCS_CO_PREOP                = 0x2
    TCS_CO_OPERATIONAL          = 0x3
    TCS_CO_STOP                 = 0x4
    TCS_CO_MODE_NUM             = 0x5
    TCS_POWER_OFF               = 0x6
    TCS_TRANISTION_STANDBY      = 0x7
    TCS_STANDBY                 = 0x8
    TCS_TRANSITION_READY_MODE   = 0x9
    TCS_READY_MODE              = 0xA
    TCS_TRANSITION_STEADY_STATE = 0xB
    TCS_STEADY_STATE            = 0xC
    TCS_CONDITIONING            = 0xD
    TCS_BIT_TEST                = 0xE
    TCS_LOCKOUT                 = 0xF

class State():
    def __init__(self, comms: Comms):
        self.comms = comms
        self.thruster_state = 0
        self.nmt_state = 0
        pass

    def read_thruster_state(self):
        self.thruster_state = self.comms.read(IDX_THRUSTER_CMD, SUB_THRUSTER_STATUS, "<I")
        return self.thruster_state
    
    def read_thruster_state_str(self):
        self.thruster_state = self.comms.read(IDX_THRUSTER_CMD, SUB_THRUSTER_STATUS, "<I")
        return TCS(self.thruster_state)

    def read_nmt_state(self):
        None

    def read_nmt_state_str(self):
        None