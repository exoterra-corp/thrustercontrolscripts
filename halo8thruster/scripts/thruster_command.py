#!/usr/bin/python3
from halo8thruster.driver.ppu import PPU, parse_ppu_args
from halo8thruster.driver.console import Console
from halo8thruster.driver.version import Version
from halo8thruster.driver.conditoning import Conditioning
from halo8thruster.driver.defines import *
from threading import Thread
import struct
import time

class ThrusterCommand(PPU):
    def __init__(self,port,sid,tui):
        super().__init__(serial_port=port, system_id=sid)
        self._tui = tui
        self._v = Version(self.com, self.mr)
        self._cond = Conditioning(self.mr, self.com)
        if self._tui: # all the bells and whistles enabled
            self.c = Console(self.mr, comms=self.com,
            header = {"thruster state": ""},
            show_raw=False, show_hsi=True, show_trace=True)
        else: #simple console, no tui
            self.c = Console(self.mr, comms=self.com)

        self.cmds = {
        "2":{"name": "stop", "func": self.state.change,
            "args": TCS.STOP,
            "help": "changes the nmt state to stopped."},
        "2": {"name": "init", "func": self.state.change,
            "args": TCS.INIT,
            "help": "changes nmt state to init."},
        "3": {"name": "preop", "func": self.state.change,
            "args": TCS.PREOP,
            "help": "changes nmt state to pre operational."},
        "4": {"name": "oper", "func": self.state.change,
            "args": TCS.OPERATIONAL,
            "help": "changes nmt state to operational.  the client boards are powered on in this state."},
        "5": {"name": "ready", "func": self.state.change,
            "args": TCS.READY_MODE,
            "help": "takes the thruster state to ready mode and lights the keeper."},
        "6": {"name": "steady", "func": self.state.change,
            "args": TCS.STEADY_STATE,
            "help": "takes the thruster to steady state and lights the anode."},
        "7": {"name": "tpoint", "func":self.c.get_write_value,
            "args": {"index": IDX_THRUSTER_CMD, "subindex": SUB_THRUST_POINT, "type": "<I", "hex_en": False},
            "help": "writes a throttle set point to the System Controller."},
        "8": {"name": "shutdown", "func": self.com.write,
            "args": {"index": IDX_THRUSTER_CMD, "subindex": SUB_SHUTDOWN, "type": "<I", "val":1},
             "help": "shuts down the thruster."},
        "9": {"name": "state", "func": lambda: self.state.thruster_state_read().name, "help": "read thruster state"},
        "10": {"name": "version", "func": self._v.read_sw, "help": "read sw versions"},
        "11": {"name": "start cond", "func": self._cond.start_conditioning,"help": "run the conditioning sequence."},
        "12": {"name": "stop cond", "func": self._cond.stop_conditioning,"help": "stops the condititons sequence"},
        "13": {"name": "print cond", "func": self._cond.print_conditoning_stats, "help": "show conditioning stats."},
        "14": {"name": "clear cond", "func": self._cond.erase_conditioning_stats, "help": "erase conditioning stats."},
        "15": {"name": "telem", "func": self.query_block_hsi, "help": "queries the HSI values using a segmented transfer"},
        "16": {"name": "fault stats", "func": self.query_fault_status, "help": "queries and prints the error stats."},
        "17": {"name": "bit", "func": self.c.get_write_value,
               "args": {"index": IDX_THRUSTER_CMD, "subindex": SUB_BIT, "type": "<I"},
               "help": "runs a specified bit sequence.  check trace for status."},
        }

        #update the cmd list to the console obj
        self.c.update_cmds(self.cmds)
        Thread(target=self._gather, daemon=True).start()
        self.c.start()  # start the console 

    def _gather(self):
        cnt = 0
        while True:
            try:
                status = self.state.thruster_state_read()
                self.c.update_header("thruster state", status.name)
                self.c.update_status_args(f"thruster state: {status.name.lower()} ")
                self.state.trace_read()
                if cnt % 3 == 0:
                    self.mr.hsi(self.state.block_telem_read())  # swap back to self.state.block_telem_read() for real hardware
                cnt+=1
            except Exception as e:
                self.mr.sys(f"[gather] {e}")
            time.sleep(0.1)

    def query_block_hsi(self):
        """
        query_block_hsi, reads and prints the hsi to the console
        """
        telem = self.state.block_telem_read()
        parsed = HSIDefines().parse_hsi_packet(telem)
        self.mr.sys(parsed)

    def query_fault_status(self):
        faults = []
        for i in range(0,5):
            subidx = SUB_FAULT_BASE + i
            val = self.com.read(IDX_FAULT_STATUS, subidx, "<I")
            self.mr.sys(f"{i}:{hex(val)}")
            faults.append(val)
    
def main():
    port, sid, tui = parse_ppu_args("Thruster Command console")
    ThrusterCommand(port, sid, tui)

if __name__ == "__main__":
    main()
