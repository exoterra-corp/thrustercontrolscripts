#!/usr/bin/python3
from halo8thruster.driver.ppu import PPU, parse_ppu_args
from halo8thruster.driver.console import Console
from halo8thruster.driver.version import Version
from halo8thruster.driver.conditoning import Conditioning
from halo8thruster.driver.defines import *
from threading import Thread
import struct
import time


def make_fake_hsi_packet() -> bytes:
    """
    Build a 122-byte HSI packet with unique values per field.
    Each value encodes its section (thousands digit) and field index within the section,
    so a misaligned display is immediately obvious.
    Values are packed in the exact order parse_hsi_packet() expects.

    Section prefixes:
      1xxx = Anode     2xxx = Keeper    3xxx = Mag Outer  4xxx = Mag Inner
      5xxx = Valves    6xxx = HK        7xxx = EFC         8xxx = SYS-MEM
    """
    return struct.pack(
        "<"
        "IIIHHHHHHH"    # anode:    1001-1010 (I I I H H H H H H H) = 3I+7H
        "IHHHHHHH"      # keeper:   2001-2008 (I H H H H H H H)     = 1I+7H
        "HHHHHH"        # mag out:  3001-3006
        "HHHHHH"        # mag in:   4001-4006
        "HHHiIHHHHH"   # valves:   5001-5010 (H H H i I H H H H H)
        "HHHHH"         # hk:       6001-6005
        "HHHH"          # efc:      7001-7004
        "III",          # sys-mem:  8001-8003
        # anode (10)
        1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
        # keeper (8)
        2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008,
        # mag outer (6)
        3001, 3002, 3003, 3004, 3005, 3006,
        # mag inner (6)
        4001, 4002, 4003, 4004, 4005, 4006,
        # valves (10) — va_temperature is signed i, va_tank_pressure is unsigned I
        5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010,
        # hk (5)
        6001, 6002, 6003, 6004, 6005,
        # efc (4) — displayed as hex, so 7001=0x1b59 etc.
        7001, 7002, 7003, 7004,
        # sys-mem (3) — displayed as hex, so 8001=0x1f41 etc.
        8001, 8002, 8003,
    )

class ThrusterCommand(PPU):
    def __init__(self):
        super().__init__()
        self.c = Console(self.mr, comms=self.com)
        self.v = Version(self.com, self.mr)
        self.cond = Conditioning(self.mr, self.com)
        self.cmds = {
        "2":{"name": "NMT STATE STOPPED", "func": self.state.change,
            "args": TCS.STOP,
            "help": "Changes the nmt state to stopped."},
        "2": {"name": "init", "func": self.state.change,
            "args": TCS.INIT,
            "help": "Changes nmt state to init."},
        "3": {"name": "preop", "func": self.state.change,
            "args": TCS.PREOP,
            "help": "Changes the nmt state to pre operational."},
        "4": {"name": "oper", "func": self.state.change,
            "args": TCS.OPERATIONAL,
            "help": "Changes NMT STATE to operational.  The client boards are powered on in this state."},
        "5": {"name": "readymode", "func": self.state.change,
            "args": TCS.READY_MODE,
            "help": "Takes the thruster state to ready mode and lights the keeper."},
        "6": {"name": "steadystate", "func": self.state.change,
            "args": TCS.STEADY_STATE,
            "help": "Takes the thruster to steady state and lights the anode."},
        "7": {"name": "thpoint", "func":self.c.get_write_value,
            "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x4, "type": "<I", "hex_en": False},
            "help": "Writes a throttle set point to the System Controller."},
        "8": {"name": "state", "func": lambda: self.state.thruster_state_read().name, "help": "read thruster state"},
        "9": {"name": "version", "func": self.v.read_sw, "help": "read sw versions"},
        "10": {"name": "start cond", "func": self.cond.start_conditioning,"help": "run the conditioning sequence."},
        "11": {"name": "stop cond", "func": self.cond.stop_conditioning,"help": "stops the condititons sequence"},
        "12": {"name": "print cond", "func": self.cond.print_conditoning_stats, "help": "show conditioning stats."},
        "13": {"name": "clear cond", "func": self.cond.erase_conditioning_stats, "help": "erase conditioning stats."},

        # "12": {"name": "telem", "func": self.query_block_hsi,
        #        "args": {"index": IDX_HSI_BLOCK, "subindex": SUB_HSI_BLOCK, "type": "<I"},
        #        "help": "Queries the HSI values using a segmented transfer"},
        # "13": {"name": "read fault status", "func": self.read_fault_status,
        #        "args": {"index": IDX_FAULT_STATUS, "subindex": SUB_FAULT_BASE, "type": "<I"},
        #        "help": "Read the Error Stats."},
        # "14": {"name": "run bit test", "func": self.get_write_value,
        #        "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x7, "type": "<I"},
        #        "help": "Run the BIT sequence."},
        # "15": {"name": "status print loop", "func": self.get_status_index,
        #       "args": {"index": IDX_THRUSTER_CMD},
        #       "help": "Prints Status of Ready Mode, Steady State, and ThrusterStatus continuously."},
        }

    # header = {"thruster state": self.state.thruster_state_read().name},
    # show_raw=True, show_hsi=True, show_trace=True)
    # Console exists now, so update_header() is safe to call from the thread
        self.c.update_cmds(self.cmds)
        Thread(target=self._gather, daemon=True).start()
        self.c.start()  # blocks until exit

    def _gather(self):
        cnt = 0
        while True:
            try:
                status = self.state.thruster_state_read()
                self.c.update_header("thruster state", status.name)
                self.state.trace_read()
                if cnt % 3 == 0:
                    self.mr.hsi(self.state.block_telem_read())  # swap back to self.state.block_telem_read() for real hardware
                cnt+=1
            except Exception as e:
                self.mr.sys(f"[gather] {e}")
            time.sleep(0.1)

def main():
    port, sid = parse_ppu_args("Thruster Command console")
    ThrusterCommand()

if __name__ == "__main__":
    main()
