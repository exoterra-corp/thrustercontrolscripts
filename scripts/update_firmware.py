#!/usr/bin/python3
import sys, canopen, argparse, time

BOOTUP_TIMEOUT = 10

class FirmwareUpdater():
    def __init__(self, serial_port, system_id, image_file):
        self.bytes = bytearray()
        self.boot_msg_found = False
        hexFileObject = open(image_file, 'rb')
        data = hexFileObject.readlines()
        for line in data:
            self.bytes += bytearray(line)

        self.network = canopen.Network()
        if serial_port.lower() == "can":
            self.network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)  # 1MHZ
        else:
            self.network.connect(bustype="exoserial", channel=serial_port, baudrate=115200)
        self.node = self.network.add_node(system_id)
        self.network.add_node(self.node)
        self.node.sdo.RESPONSE_TIMEOUT = 5

    def do_update(self, args):
        run = True
        if not args.v:
            print("Updating Firmware.  This will take a few minutes. A y/n install prompt will be shown to finish the install.")
            self.update_image_download()
        verify_result = self.update_image_verify()
        print("verify result = ", hex(int.from_bytes(verify_result, "little"))[2:].zfill(8))
        while run:
            cmd = input("install image? y/n $ ")
            cmd = cmd.lower()
            if 'y' in cmd:
                try:
                    self.update_image_install()
                except canopen.sdo.exceptions.SdoCommunicationError:
                    self.network.subscribe(0x722, self.notify_bootup)
                    cnt = 0
                    # wait for bootup msg from the device
                    print("Image Flashed; Waiting for 0x722 NMT msg from PPU.")
                    while cnt <= BOOTUP_TIMEOUT and not self.boot_msg_found:
                        time.sleep(0.1)

                    if not self.boot_msg_found:
                        print("PPU Failed to boot.")
                run = False
            elif 'n' in cmd:
                run = False
            else:
                print("please enter y or n")

    def notify_bootup(self, can_id, data, timestamp):
        self.boot_msg_found = True
        print("PPU Booted Successfully.")
    def update_image_download(self):
        self.node.sdo.download(0x5500, 1, self.bytes, force_segment=True)

    def update_image_verify(self):
        # placeholder data, currently doesn't matter what we send
        data = bytes(4)
        self.node.sdo.download(0x5500, 2, data, force_segment=False)
        return self.node.sdo.upload(0x5500, 2)

    def update_image_install(self):
        # placeholder data, currently doesn't matter what we send
        data = bytes(1)
        self.node.sdo.download(0x5500, 3, data, force_segment=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update firmware uploads the firmware to the SAM over RS458.')
    parser.add_argument('serial_port', action='store', type=str, help='The Serial Port to use for RS485.',
                        default="/dev/ttyUSB0")
    parser.add_argument('system_id', action='store', type=str, help='The System Id for the connection usually 0x22.',
                        default=0x22)
    parser.add_argument('image_file', action='store', type=str, help='The SAM firmware image file.')
    parser.add_argument('-v', action='store_true', help='Run just the verify and install option.')
    args = parser.parse_args()
    updater = FirmwareUpdater(args.serial_port, args.system_id, args.image_file)
    try:
        updater.do_update(args)
    except KeyboardInterrupt:
        print("Connection Aborted Mid-Update, please reset the PPU to INIT before trying another install.")
