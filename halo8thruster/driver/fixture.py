from halo8thruster.driver.ppu import PPU 
from enum import IntEnum
"""
This class is similar to ppu but will run a list of operations for testing the ppu.
Straight up for testing.


dict or json file doesn't matter.



"""

class StepReaction(IntEnum):
    cont = 0,
    stop = 1,
    loop = 2

class TestFixture(PPU):
    """"""
    def __init__(self):
        super().__init__()
        self._steps = {}

    def add_step(self):
        pass

    def run_test(self):
        for s in self._steps:
            print(s)