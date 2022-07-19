#!/usr/bin/python3
import sys,canopen, argparse, os
from loguru import logger
import serial.tools.list_ports
import struct, datetime
from os.path import exists
sys.path.append("/opt/jmitchell/testscripts/libecp")
try:
    from libecp.interfaces.generic_script import GenericScript
    from libecp.tools.versions import Versions
    from libecp.tools.arg_parser import ScriptArguments
except ImportError as e:
    logger.info(f"Failed to import libecp: {e}")

class Versions(GenericScript):
    def __init__(self):
        """connects and then reads the software version
        """
        super().__init__()
        self.storage_path = "./logs/versions/"
        sc = ScriptArguments()
        sc.parse_args()
        self.ecp_conn = self.connect(sc.get_serial_port(), sc.get_system_id(), sc.get_eds_file(), {"error_parser_en": True, }) #"hsi_en": True, "trace_en": True})
        logger.info(self.versions.read_hw_version())

if __name__ == "__main__":
    versions = Versions()

