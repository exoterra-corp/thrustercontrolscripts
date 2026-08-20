#!/usr/bin/python3
import datetime, os
from halo8thruster.driver.console import Console
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.mr_logger import MrLogger, LogType

class Versions():
    def __init__(self):
        self.storage_path = "./logs/versions/"
        self.cmds = {
            "2": {"name": "read_sw_version", "func": self.read_sw_version, "help": "Read software versions"},
            "3": {"name": "read_hw_version", "func": self.read_hw_version, "help": "Read hardware version"},
        }
        self.mr = MrLogger("logs")
        self.com = Comms(self.mr)
        self.c = Console(self.mr, self.cmds)
        self.version_info_str = ["Thruster Control", "Keeper", "Anode", "Outer Magnet", "Inner Magnet", "Valves", "Thruster Control Bootloader"]
        self.c.start_console()
        
def main():
    Versions()

if __name__ == "__main__":
    main()
