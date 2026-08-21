from enum import IntEnum
import time
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.od_defines import *
from halo8thruster.driver.mr_logger import *

class NMTD(IntEnum):
    INIT = 0
    STOPPED = 4
    OPERATIONAL = 5
    SLEEP = 80
    STANDBY = 96
    PRE_OPERATIONAL = 127

class TCS(IntEnum): #Thruster Control State
    """
        Thruster Control State, enums of the various states of the PPU.
    """
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
    State handles all things state with the ppu, its current thruster state, nmt state, and gathering state about it,
    with hsi and trace messages.  A connected comms class and logging class are required to use.
    """

    def __init__(self, comms: Comms, mr_logger: MrLogger):
        self.comms = comms
        self.mr = mr_logger
        self.thruster_state = 0

    def thruster_state_read(self):
        self.thruster_state = self.comms.read(IDX_THRUSTER_CMD, SUB_THRUSTER_STATUS, "<I")
        return TCS(self.thruster_state)

    def change(self, state: TCS, throttle_point=1):
        """
        change, will change the thruster state either by nmt message or direct call to the thruster cmd index
        throttle_point will only be used in steady state.  Allows for setting the throttle point while going to the state.
        """
        throttle_point = abs(throttle_point)
        # self.thread_lock.acquire()
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
            #need to find a way to pass in a value here, because steady state uses throttling
            self.mr.sys(f"Switching State Steady State throttle point {throttle_point}")
            self.comms.write(IDX_THRUSTER_CMD, SUB_STEADY_STATE, throttle_point, "<I")

    def thruster_state_wait(self, desired_thruster_state:TCS, max_delay=20, poll_time=1):
        """blocks until the correct thruster state is returned or the max delay is hit
        if max delay is 0 it will wait indefinitely.
        Args:
            tcs_state (TCS): the desired thruster state to look for.
            log_state (bool, optional): will print the status of each read to the log !noisy!. Defaults to True.
            max_delay (int, optional): the max amount of reads before the function exits ~15 seconds. Defaults to 15.
            poll_time (int, optional): how fast to query the ecp for thruster state changes in seconds.
        """
        timeout_cntr = 0
        while desired_thruster_state != cur_thruster_state:
            cur_thruster_state = self.thruster_state_read()
            time.sleep(poll_time)
            timeout_cntr+=1

            if timeout_cntr > max_delay:
                break

    def trace_read(self):
        """
            trace_read, gets a trace msg by first looking at the head and the tail to see if there is one to get.
            if the head and the tail are == then there are no messages just return.
        """
        msg = self.comms.read(IDX_TRACE_MSG, SUB_TRACE_MSG)
        # its a co_string type not sure how to read that

        if msg is not None:
            self.mr.trace(msg)
        return msg
        # self.send_udp_packet(msg, self.trace_udp_ip, self.trace_udp_port)

    def block_telem_read(self):
        """
        block_telem_read, gets hsi data and sends it out for parsing.
        """
        telem_block = self.comms.read(IDX_HSI_BLOCK, SUB_HSI_BLOCK)
        self.mr.hsi(telem_block)
        return None
        #self.trace_sock.sendto(data, (self.hsi_status_ip, self.hsi_block_udp_port))