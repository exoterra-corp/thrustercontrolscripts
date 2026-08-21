#!/usr/bin/python3
from halo8thruster.driver.update import Update
from halo8thruster.driver.ppu import PPU
from halo8thruster.driver.console import Console


class UpdateFirmware(PPU):
    def __init__(self, serial_port, system_id, image_file):
        super().__init__(serial_port=serial_port, system_id=system_id, log_name="update_firmware")
        self.upd = Update(self.com, self.mr)
        self.cmds = {
            "2": {"name": "download", "func": lambda _: self.upd.download(image_file), "help": f"Download {image_file} to device"},
            "3": {"name": "verify",   "func": lambda _: self.upd.verify(),             "help": "Verify downloaded image, print result"},
            "4": {"name": "install",  "func": lambda _: self.upd.install(),            "help": "Flash image and wait for reboot"},
            "5": {"name": "run",      "func": lambda _: self.upd.run(image_file),      "help": "Full sequence: download → verify → install"},
        }
        self.c = Console(self.mr, self.cmds)
        self.c.start_console()

def main():
    import argparse
    p = argparse.ArgumentParser(description="Update PPU Firmware")
    p.add_argument("image_file",          help="Firmware binary (.bin) to flash")
    p.add_argument("--port", default="/dev/ttyUSB0", dest="serial_port", help="Serial port (default: /dev/ttyUSB0)")
    p.add_argument("--id",   default="0x22",         dest="system_id",   help="CANopen node ID (default: 0x22)")
    a = p.parse_args()
    UpdateFirmware(a.serial_port, int(a.system_id, 0), a.image_file)


if __name__ == "__main__":
    main()
