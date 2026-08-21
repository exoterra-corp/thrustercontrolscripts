#!/usr/bin/python3
from halo8thruster.driver.update import UpdateFirmware
from halo8thruster.driver.ppu import PPU, parse_ppu_args

class Versions(PPU):
    def __init__(self):
        super().__init__(debug=True)
        self.ver = UpdateFirmware(self.com, )
        self.c.start_console()

def main():
    port, sid = parse_ppu_args("Read PPU Versions")
    Versions()

if __name__ == "__main__":
    main()
