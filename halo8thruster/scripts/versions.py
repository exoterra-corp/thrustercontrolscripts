#!/usr/bin/python3
from halo8thruster.driver.console import Console
from halo8thruster.driver.comms import Comms
from halo8thruster.driver.mr_logger import MrLogger
from halo8thruster.driver.version import Version

class Versions():
    def __init__(self):
        self.mr = MrLogger("logs")
        self.com = Comms(self.mr)
        self.ver = Version(self.com, self.mr)
        self.cmds = {
            "2": {"name": "read_sw_version", "func": self.ver.read_sw, "help": "Read software versions"},
            "3": {"name": "read_hw_version", "func": self.ver.read_hw, "help": "Read hardware version"},
        }
        self.c = Console(self.mr, self.cmds)
        self.c.start_console()

def main():
    Versions()

if __name__ == "__main__":
    main()
