from enum import IntEnum
import time
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.od_defines import *
from halo8thruster.driver.mr_logger import MrLogger
from halo8thruster.driver.exceptions import StateError, StateTimeout

class NMTD(IntEnum):
    INIT = 0
    STOPPED = 4
    OPERATIONAL = 5
    SLEEP = 80
    STANDBY = 96
    PRE_OPERATIONAL = 127

class TCS(IntEnum):
    """Thruster Control State — enums of the various states of the PPU."""
    INVALID                 = 0x0
    INIT                    = 0x1
    PREOP                   = 0x2
    OPERATIONAL             = 0x3
    STOP                    = 0x4
    MODE_NUM                = 0x5
    POWER_OFF               = 0x6
    TRANISTION_STANDBY      = 0x7
    STANDBY                 = 0x8
    TRANSITION_READY_MODE   = 0x9
    READY_MODE              = 0xA
    TRANSITION_STEADY_STATE = 0xB
    STEADY_STATE            = 0xC
    CONDITIONING            = 0xD
    BIT_TEST                = 0xE
    LOCKOUT                 = 0xF

class State():
    """
    Handles thruster state, NMT state, trace, and HSI telemetry reads.
    Requires a connected Comms instance and an MrLogger.
    """

    def __init__(self, comms: Comms, mr_logger: MrLogger):
        self.comms = comms
        self.mr = mr_logger
        self.thruster_state = TCS.INVALID

    def thruster_state_read(self) -> TCS:
        """Read and return the current TCS state. Raises StateError for unknown values."""
        raw = self.comms.read(IDX_THRUSTER_CMD, SUB_THRUSTER_STATUS, "<I")
        try:
            self.thruster_state = TCS(raw)
        except ValueError:
            raise StateError(f"Unknown thruster state value: {raw}")
        return self.thruster_state

    def change(self, state: TCS, throttle_point=1):
        """
        Command a state transition via NMT or direct SDO write.
        throttle_point is only used for STEADY_STATE.
        Raises CommsError on SDO failure.
        """
        throttle_point = abs(throttle_point)
        if state == TCS.OPERATIONAL:
            self.mr.sys("Switching State Operational")
            self.comms.node.nmt.send_command(0x1)
        elif state == TCS.PREOP:
            self.mr.sys("Switching State Pre-Operational")
            self.comms.node.nmt.send_command(0x80)
        elif state == TCS.INIT:
            self.mr.sys("Switching State Init")
            self.comms.node.nmt.send_command(0x81)
        elif state == TCS.STOP:
            self.mr.sys("Switching State Stopped")
            self.comms.node.nmt.send_command(0x2)
        elif state == TCS.READY_MODE:
            self.mr.sys("Switching State Ready Mode")
            self.comms.write(IDX_THRUSTER_CMD, SUB_READY_MODE, 1, "<I")
        elif state == TCS.STEADY_STATE:
            self.mr.sys(f"Switching State Steady State throttle point {throttle_point}")
            self.comms.write(IDX_THRUSTER_CMD, SUB_STEADY_STATE, throttle_point, "<I")

    def thruster_state_wait(self, desired_thruster_state: TCS, max_delay=20, poll_time=1) -> TCS:
        """
        Block until the thruster reaches desired_thruster_state or max_delay polls expire.
        Returns the final state on success. Raises StateTimeout if max_delay is exceeded.
        poll_time is in seconds.
        """
        cur = self.thruster_state_read()
        for _ in range(max_delay):
            if cur == desired_thruster_state:
                return cur
            time.sleep(poll_time)
            cur = self.thruster_state_read()
        raise StateTimeout(
            f"Timed out waiting for {desired_thruster_state.name}, last state: {cur.name}"
        )

    def trace_read(self):
        """Read a trace message from the device and forward it to the trace log."""
        msg = self.comms.read(IDX_TRACE_MSG, SUB_TRACE_MSG)
        if msg is not None:
            self.mr.trace(msg)
        return msg

    def block_telem_read(self):
        """Read a block HSI telemetry packet and forward it to the HSI log."""
        telem_block = self.comms.read(IDX_HSI_BLOCK, SUB_HSI_BLOCK)
        self.mr.hsi(telem_block)
        return telem_block
