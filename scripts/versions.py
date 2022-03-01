#!/usr/bin/python3
import sys,canopen, argparse
import serial.tools.list_ports
import struct, datetime
from os.path import exists
from os import mkdir

class Versions():
    def __init__(self, sys_id, device):
        self.storage_path = "logs/versions/"
        network = canopen.Network()
        self.sys_id = sys_id
        if device == "pcan":
            print("pcan")
            network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)  # 1MHZ
        elif "tty" or "COM" in device:
            network.connect(bustype="exoserial", channel=device, baudrate=115200)
            
        #create a node to communicate with
        self.node = network.add_node(self.sys_id)

        network.add_node(self.node)
        self.node.sdo.RESPONSE_TIMEOUT = 1
        self.co_index = 0x5000

        self.version_info_str = ["Thruster Control", "Keeper", "Anode", "Outer Magnet", "Inner Magnet", "Valves", "Thruster Control Bootloader"]

    def create_folder(self, folder_name):
        if not exists(folder_name):
            print(f"Creating {folder_name}.")
            try:
                mkdir(folder_name)
                return True
            except OSError as e:
                print(f"Error {folder_name} could not be created. {e}")
        return False

    def read_sw_version(self):
        try:
            self.create_folder(self.storage_path)
            now = datetime.datetime.now()
            time_string = now.strftime("%Y_%m_%d_%H_%M_%S")
            version_file = open(f"{self.storage_path}sw_version_{time_string}.txt", "w")
            version_file.write(f"========== Version Read Time {time_string} ==========\n")

            num_components = 7
            num_subindices = self.node.sdo.upload(0x5000, 0)

            version_line = "Id: Version  : gitsha   : git sha 1 : Exec V 1  : git sha 2 : Exec V 2  : git sha 3 : Exec V 3 : Device Name "
            print(version_line)
            version_file.write(version_line + "\n")

            for i in range(num_components):
                device_name = ""
                if i < len(self.version_info_str):
                    device_name = self.version_info_str[i]
                version_line = ""
                self.node.sdo.download(0x5000, 1, struct.pack("B", i))
                for j in range(2,num_subindices[0]):
                    v_g = bytearray(self.node.sdo.upload(0x5000, j))
                    # endian swap
                    v_g[0], v_g[1] = v_g[1], v_g[0]
                    v_g[2], v_g[3] = v_g[3], v_g[2]
                    v_g[0:2], v_g[2:4] = v_g[2:4], v_g[0:2]
                    version_line += " : " + str(v_g.hex())
                line = f"{i}{version_line} : {device_name}"
                print(line)
                version_file.write(line+"\n")
            version_file.close()
        except canopen.sdo.exceptions.SdoCommunicationError as e:
            print(f"Device failed to respond. {e}")

    def read_hw_version(self):
        return self.node.sdo.upload(0x1009, 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script pulls and prints the versions from the System Control Module.')
    parser.add_argument('device', action='store', type=str, help='"pcan" or "serial"',default="/dev/ttyUSB0")
    parser.add_argument('system_id', action='store', type=str, help='The System Id for the connection usually 0x22.',
                        default=0x22)
    args = parser.parse_args()
    system_id = 0
    try:
        system_id = int(args.system_id, 16)
    except ValueError as e:
        print(f"Check system_id, {args.system_id} is not a  hex number.")
        sys.exit(1)
    err_reg = Versions(system_id, device=args.device)
    version_sw = err_reg.read_sw_version()

