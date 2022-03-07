#!/usr/bin/python3
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
import time, traceback
from sys import exit
from canopen import Network
from enum import Enum

class NMT_STATE(Enum):
    GO_TO_OPERATIONAL = 0x1
    GO_TO_PRE_OPERATIONAL = 0x80
    GO_TO_INIT = 0x81

class THRUSTER_STATE(Enum):
    TCS_TRANISTION_STANDBY      = 0x7  #Transitioning to Standby (NMT_OPERATIONAL)
    TCS_STANDBY                 = 0x8  #In Standby               (NMT_OPERATIONAL) 
    TCS_TRANSITION_READY_MODE   = 0x9  #Thruster Startup         (NMT_OPERATIONAL)   
    TCS_READY_MODE              = 0xA  #Ready Mode (Keeper On)   (NMT_OPERATIONAL) 
    TCS_TRANSITION_STEADY_STATE = 0xB  #Starting Anode           (NMT_OPERATIONAL) 
    TCS_STEADY_STATE            = 0xC  #Steady State (Anode On)  (NMT_OPERATIONAL) 

THRUSTER_COMMAND_INDEX = 0x4000
THRUSTER_COMMAND_SUBINDEX_READY_MODE = 0x1
THRUSTER_COMMAND_SUBINDEX_STEADY_STATE = 0x2
THRUSTER_COMMAND_SUBINDEX_STATE = 0x5
SLEEP_TIME = 1

class Example:
    def __init__(self, serial_port, ppu_system_id):
        try:
            #initalize variables
            self.system_id = ppu_system_id
            self.port = serial_port
            self.thruster_state = 0
            self.boot_msg = False
            self.enable_val = bytearray(struct.pack("<I", 0x1))

            start = time.time()
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
            print(f"Added {hex(self.system_id)} to canopen Network.")

            #subscribe to bootup msg
            self.network.subscribe(0x722, self.notify_bootup)

            #send device Init, resets the PPU.
            print("Resetting PPU.")
            self.node.nmt.send_command(NMT_STATE.GO_TO_INIT.value)
            
            #waiting for the PPU to boot.
            print("waiting for boot msg...")
            while self.boot_msg == False:
                time.sleep(SLEEP_TIME)
            print("PPU Ready!")

            #change the nmt state of the PPU to OPERATIONAL and wait for Thruster_Standby.
            self.node.nmt.send_command(NMT_STATE.GO_TO_OPERATIONAL.value)
            while (self.thruster_state != THRUSTER_STATE.TCS_STANDBY.value):
                time.sleep(SLEEP_TIME)
                self.thruster_state = self.node.sdo.upload(THRUSTER_COMMAND_INDEX, THRUSTER_COMMAND_SUBINDEX_STATE)
                self.thruster_state = struct.unpack("<I",self.thruster_state)[0]
                print(f"Transitioning to Standby. Thruster State: {self.thruster_state}", end="\r")

            print(f"\nThruster State: {hex(self.thruster_state)}")

            if self.thruster_state != THRUSTER_STATE.TCS_STANDBY.value:
                    print("Device Failed to go to Standby.")
                    exit(1)
            else: 
                    print("Device is set to Standby.")

            #Set the PPU to run Ready Mode
            self.node.sdo.download(THRUSTER_COMMAND_INDEX, THRUSTER_COMMAND_SUBINDEX_READY_MODE, self.enable_val)
            self.thruster_state = 0
            while (self.thruster_state != THRUSTER_STATE.TCS_READY_MODE.value) and \
                    (self.thruster_state != THRUSTER_STATE.TCS_STANDBY.value):
                time.sleep(SLEEP_TIME)
                self.thruster_state = self.node.sdo.upload(THRUSTER_COMMAND_INDEX, THRUSTER_COMMAND_SUBINDEX_STATE)
                self.thruster_state = struct.unpack("<I", self.thruster_state)[0]
                print(f"Transitioning to Ready Mode. Thruster State: {hex(self.thruster_state)}", end="\r")

            print(f"\nThruster State: {hex(self.thruster_state)}")
            
            if self.thruster_state != THRUSTER_STATE.TCS_READY_MODE.value:
                print("Device Failed to set to Ready Mode.")
                self.thruster_state = self.node.sdo.upload(THRUSTER_COMMAND_INDEX, THRUSTER_COMMAND_SUBINDEX_STATE)
                self.thruster_state = struct.unpack("<I", self.thruster_state)[0]
                print(f"\nThruster State: {hex(self.thruster_state)}")
                self.node.nmt.send_command(NMT_STATE.GO_TO_PRE_OPERATIONAL.value)
                exit(1)
            else:
                print("Device is set to Ready Mode. ")

            #Set the PPU to run Steady State
            self.node.sdo.download(THRUSTER_COMMAND_INDEX, THRUSTER_COMMAND_SUBINDEX_STEADY_STATE, self.enable_val)
            self.thruster_state = 0
            while (self.thruster_state != THRUSTER_STATE.TCS_STEADY_STATE.value) and \
                    (self.thruster_state != THRUSTER_STATE.TCS_STANDBY.value):
                time.sleep(SLEEP_TIME)
                self.thruster_state = self.node.sdo.upload(THRUSTER_COMMAND_INDEX, THRUSTER_COMMAND_SUBINDEX_STATE)
                self.thruster_state = struct.unpack("<I", self.thruster_state)[0]
                print(f"Transitioning to Steady State. Thruster State: {hex(self.thruster_state)}", end="\r")
            
            print(f"\nThruster State: {hex(self.thruster_state)}")
            
            if self.thruster_state != THRUSTER_STATE.TCS_STEADY_STATE.value:
                print(f"Device Failed to go into Steady State. {self.thruster_state}")
            else:
                print(f"Device in Steady State. {hex(self.thruster_state)}")
            stop = time.time()

            print(f"PPU took {stop - start} seconds from reset to steady state.")

            while True:
                print("Thruster in Steady State. Cntrl-c to shutdown and exit.", end="\r")
                time.sleep(SLEEP_TIME)

            self.node.disconnect()

        except KeyboardInterrupt:
            print("\nDetected Cntrl-c Returning to Pre-Operational.")
            self.node.nmt.send_command(NMT_STATE.GO_TO_PRE_OPERATIONAL.value)
            print("Sent NMT change state Pre-Operational.")

        except Exception as e:
            print(traceback.format_exc())
            print(f"{e}")
    
    def notify_bootup(self, can_id, data, timestamp):
        self.boot_msg = True

if __name__ == "__main__":
    serial_port = "/dev/ttyUSB0"
    system_id = 0x22

    e = Example(serial_port, system_id)
