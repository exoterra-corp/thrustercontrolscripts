#!/usr/bin/python3
import sys,canopen, argparse
import serial.tools.list_ports
import struct, datetime

class versions():
    def __init__(self, device):
        network = canopen.Network()

        if device == "pcan":
            print("pcan")
            network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=1000000)  # 1MHZ
        elif "tty" or "COM" in device:
            network.connect(bustype="exoserial", channel=device, baudrate=115200)
            
        #create a node to communicate with
        self.node = network.add_node(0x22)

        network.add_node(self.node)
        self.node.sdo.RESPONSE_TIMEOUT = 1
        self.co_index = 0x5000

    def read_sw_version(self):
        now = datetime.datetime.now()
        time_string = now.strftime("%Y_%m_%d_%H_%M_%S")
        version_file = open(f"sw_version_{time_string}.txt", "w")
        version_file.write(f"========== Version Test Time {time_string} ==========\n")

        num_components = 7
        num_subindices = self.node.sdo.upload(0x5000, 0) 
        
        version_line = "Id: Version  :gitsha    :git sha 1 :Exec V 1  :git sha 2 :Exec V 2  :git sha 3 :Exec V 3 "
        print(version_line)
        version_file.write(version_line + "\n")

        for i in range(num_components):
            version_line = ""
            self.node.sdo.download(0x5000, 1, struct.pack("B", i))
            for j in range(2,num_subindices[0]):
                v_g = bytearray(self.node.sdo.upload(0x5000, j))
                # endian swap
                v_g[0], v_g[1] = v_g[1], v_g[0] 
                v_g[2], v_g[3] = v_g[3], v_g[2]
                v_g[0:2], v_g[2:4] = v_g[2:4], v_g[0:2]
                version_line += " : " + str(v_g.hex())
            print(str(i) + version_line)
            line = str(i) + version_line + "\n"
            version_file.write(line)
        version_file.close()

    def read_hw_version(self):
        return self.node.sdo.upload(0x1009, 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This script pulls and prints the versions from the System Control Module.')
    parser.add_argument('device', action='store', type=str, help='"pcan" or "serial"',default="/dev/ttyUSB0")
    args = parser.parse_args()

    err_reg = versions(device=args.device)
    version_sw = err_reg.read_sw_version()

