#!/usr/bin/python3
from halo8thruster.driver.ppu import PPU, parse_ppu_args
from halo8thruster.driver.console import Console
from halo8thruster.driver.defines import *

class ThrusterCommand(PPU):
    def __init__(self):
        super().__init__()
        self.cmds = {
            "2":{"name": "NMT STATE STOPPED", "func": self.state.change,
                  "args": TCS.STOP,
                  "help": "Changes NMT STATE to STOP."},
            "2": {"name": "NMT STATE INIT", "func": self.state.change,
                  "args": TCS.INIT,
                  "help": "Changes NMT STATE to INIT."},
            "3": {"name": "NMT STATE PRE-OP", "func": self.state.change,
                  "args": TCS.PREOP,
                  "help": "Changes NMT STATE to PRE-OP."},
            "4": {"name": "NMT STATE OPERATIONAL", "func": self.state.change,
                  "args": TCS.OPERATIONAL,
                  "help": "Changes NMT STATE to OPERATIONAL."},

            "5": {"name": "get state", "func": self.state.thruster_state_read, "help": "read thruster state"},
            # "5": {"name": "Run Ready Mode", "func": self.get_write_value,
            #       "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x1, "type": "<I", "default": "1"},
            #       "help": "Writes a UINT-32 to the Thruster Ready Mode."},
            # "6": {"name": "Run Steady State", "func": self.get_write_value,
            #       "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x2, "type": "<I"},
            #       "help": "Writes a UINT-32 to the Thruster Steady State."},
            # "7": {"name": "Thruster Shutdown", "func": self.get_write_value,
            #       "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x3, "type": "<B", "default": "1"},
            #       "help": "Shutdown down the thruster."},

            # "8": {"name": "Status", "func": self.get_status_index,
            #       "args": {"index": IDX_THRUSTER_CMD},
            #       "help": "Prints Status of Ready Mode, Steady State, and ThrusterStatus continuously."},


            # "9": {"name": "Write Set Thrust", "func": self.get_write_value,
            #       "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x4, "type": "<I", "hex_en": False},
            #       "help": "Writes a throttle set point to the System Controller."},

            # "10": {"name": "Condition", "func": self.get_write_value,
            #        "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x6, "type": "<I"},
            #        "help": "Run the conditioning sequence."},
            # "11": {"name": "Test", "func": self.get_write_value,
            #        "args": {"index": IDX_THRUSTER_CMD, "subindex": 0x7, "type": "<I"},
            #        "help": "Run the BIT sequence."},

            # "12": {"name": "Query Block HSI", "func": self.query_block_hsi,
            #        "args": {"index": IDX_HSI_BLOCK, "subindex": SUB_HSI_BLOCK, "type": "<I"},
            #        "help": "Queries the HSI values using a segmented transfer"},

            # "13": {"name": "Read Fault Status", "func": self.read_fault_status,
            #        "args": {"index": IDX_FAULT_STATUS, "subindex": SUB_FAULT_BASE, "type": "<I"},
            #        "help": "Read the Error Stats."},

            # "15": {"name": "Print Stats", "func": self.print_conditoning_stats,
            #        "args": {"index": IDX_COND_STATS, "subindex": 0x0, "type": "<I", "default": "1"},
            #        "help": "Reset Conditioning Stats."},
        }
        self.c = Console(self.mr, self.cmds)
        self.c.start()


def main():
    port, sid = parse_ppu_args("Read PPU Versions")
    ThrusterCommand()

if __name__ == "__main__":
    main()
