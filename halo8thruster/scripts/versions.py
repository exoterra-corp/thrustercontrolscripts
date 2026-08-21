#!/usr/bin/python3
from halo8thruster.driver.version import Version
from halo8thruster.driver.ppu import PPU, parse_ppu_args
from halo8thruster.driver.console import Console

class Versions(PPU):
    def __init__(self):
        super().__init__()
        self.ver = Version(self.com, self.mr)
        self.cmds = {
            "2": {"name": "read_sw_version", "func": self.ver.read_sw, "help": "Read software versions"},
            "3": {"name": "read_hw_version", "func": self.ver.read_hw, "help": "Read hardware version"},
        }

        self.c = Console(self.mr, self.cmds)
        self.c.start()

def main():
    port, sid = parse_ppu_args("Read PPU Versions")
    Versions()

if __name__ == "__main__":
    main()
