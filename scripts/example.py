"""
ExoTerra Resource Example Script
description:
A simple example script that with the minimum number of lines fire the thruster.
There is no error handling, no telemetry.

contact:
joshua.meyers@exoterracorp.com
jeremy.mitchell@exoterracorp.com
"""
import struct
import time
from sys import exit
from canopen import Network
from enum import Enum

class SEQ_STATUS(Enum):
    SEQ_STAT_IDLE       = 0
    SEQ_STAT_QUEUED     = 1
    SEQ_STAT_RUNNING    = 2
    SEQ_STAT_ERROR      = 3
    SEQ_STAT_ABORTED    = 4
    SEQ_STAT_SUCCESS    = 5

class NMT_STATE(Enum):
    OPERATIONAL = 0x1
    PRE_OPERATIONAL = 0x80
    INIT = 0x81

class THRUSTER_STATE(Enum):
    STANDBY = 8

#go back to init
##wait for bootup msg
#operational
#ready mode
#steady state

class Example:
    def __init__(self):
        try:
            #initalize variables
            self.system_id = 0x22 #PPU ID
            self.port = "/dev/ttyUSB0"
            # self.port = "COM3"
            self.thruster_state = 0
            self.wait_attempts = 15

            #create a network
            self.network = Network()
            print("Created can Network.")

            #connect to the device, /dev/tty for linux, COM# for windows
            self.network.connect(bustype="exoserial", channel=self.port, baudrate=115200)
            print("Created Exoserial device.")

            #create a node on the can network
            self.node = self.network.add_node(self.system_id)
            print("Created CANOpen Node.")

            #add this node to the network object
            self.network.add_node(self.node)
            print(f"Added {self.system_id} to canopen Network.")

            #change the nmt state of the PPU to OPERATIONAL
            self.node.nmt.send_command(0x1)
            print("Sent NMT change state OPERATIONAL.")

            #read nmt state of the PPU
            #Index: Thruster Command - Subindex: Status in the eds file.
            attempts = 0
            while (self.thruster_state != 8) and (attempts < self.wait_attempts):
                print(f"Checking Thruster State attempt thruster_state {self.thruster_state} - {attempts} <  attempt Max:{self.wait_attempts}.")
                self.thruster_state = self.node.sdo.upload(0x4000, 0x5)
                self.thruster_state = struct.unpack("<I",self.thruster_state)[0]
                attempts += 1
                time.sleep(1)

            if self.thruster_state != 8:
                    print("Device Failed to set to OPERATIONAL")
                    exit(1)

            #Set the PPU to run Ready Mode
            self.ready_mode = 0
            attempts = 0
            while (self.ready_mode > 3) and (attempts < self.wait_attempts):
                self.ready_mode = self.node.sdo.upload(0x4000, 0x1)
                self.ready_mode = struct.unpack("<I", self.ready_mode)[0][-1:]  # unpack and get last byte
            print(self.ready_mode)
            if self.ready_mode != 0xA:
                print("Device Failed to set to READY MODE")

            #check to see if the keeper sparks and the state is updated
            mode = 0
            while mode > 3: #wait while qeued or running
                mode = self.node.sdo.upload(0x4000, 0x1)
                mode = struct.unpack("<I", mode) #check to see if 3,4,5

            #Set the PPU to run Steady State
            self.steady_state = self.node.sdo.upload(0x4000, 0x2)
            print(f"Device in Steady State {self.steady_state}")

        except KeyboardInterrupt:
            print("Detected Cntrl-c going back to pre operational")
            # self.node.nmt.send_command(0x80)
            print("Sent NMT change state PRE-OPERATIONAL.")

        except Exception as e:
            print(f"{e}")

if __name__ == "__main__":
    e = Example()