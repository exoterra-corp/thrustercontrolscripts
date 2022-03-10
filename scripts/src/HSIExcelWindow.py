from src.AutogenTestScriptsGui import *

"""
ExoTerra Resource HSIExcelWindow.
description:
This is a helper class for the gui portion of the listener script.

contact:
joshua.meyers@exoterracorp.com 
jeremy.mitchell@exoterracorp.com
"""


class HSIExcelWindow(HSIExcelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid = self.m_hsiExcelGrid
        self.setupView()
        self.Show(True)
        self.anode_row = 4
        self.keeper_row = 1
        self.magnets_outer_row = 7
        self.magnets_inner_row = 10
        self.valves_row = 13
        self.hkm_row = 15

    def setupView(self):
        """
        setupView, formats the grid into a specific format
        """
        self.grid.ClearGrid()
        # setup keeper labels
        row = 0
        self.grid.SetRowLabelValue(row, "Keeper")
        self.grid.SetRowLabelValue(row + 1, "K-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "VSEPIC (mV)")
        self.grid.SetCellValue(row, 1, "VIN (mV)")
        self.grid.SetCellValue(row, 2, "IOUT (mA)")
        self.grid.SetCellValue(row, 3, "DAC (counts)")
        self.grid.SetCellValue(row, 4, "LASTERR")
        self.grid.SetCellValue(row, 5, "CUR_OFT (counts)")
        self.grid.SetCellValue(row, 6, "MSG_CNT")
        self.grid.SetCellValue(row, 7, "CAN_ERR")

        # setup anode labels
        row += 3
        self.grid.SetRowLabelValue(row, "Anode")
        self.grid.SetRowLabelValue(row + 1, "A-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "VX (mV)")
        self.grid.SetCellValue(row, 1, "VY (mV)")
        self.grid.SetCellValue(row, 2, "VOUT (mV)")
        self.grid.SetCellValue(row, 3, "IOUT (mA)")
        self.grid.SetCellValue(row, 4, "DAC (counts)")
        self.grid.SetCellValue(row, 5, "LASTERR")
        self.grid.SetCellValue(row, 6, "CUR_OFT (counts)")
        self.grid.SetCellValue(row, 7, "HS_TEMP")
        self.grid.SetCellValue(row, 8, "MSG_CNT")
        self.grid.SetCellValue(row, 9, "CAN_ERR")

        # setup Magnet Outer labels
        row += 3
        self.grid.SetRowLabelValue(row, "Magnet Outer")
        self.grid.SetRowLabelValue(row + 1, "MO-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "VOUT (mV)")
        self.grid.SetCellValue(row, 1, "IOUT (mA)")
        self.grid.SetCellValue(row, 2, "DAC (counts)")
        self.grid.SetCellValue(row, 3, "LASTERR")
        self.grid.SetCellValue(row, 4, "MSG_CNT")
        self.grid.SetCellValue(row, 5, "CAN_ERR")

        # setup Magnet Inner labels
        row += 3
        self.grid.SetRowLabelValue(row, "Magnet Inner")
        self.grid.SetRowLabelValue(row + 1, "MI-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "VOUT (mV)")
        self.grid.SetCellValue(row, 1, "IOUT (mA)")
        self.grid.SetCellValue(row, 2, "DAC (counts)")
        self.grid.SetCellValue(row, 3, "LASTERR")
        self.grid.SetCellValue(row, 4, "MSG_CNT")
        self.grid.SetCellValue(row, 5, "CAN_ERR")

        # setup Valves labels
        row += 3
        self.grid.SetRowLabelValue(row, "Valves Outer")
        self.grid.SetRowLabelValue(row + 1, "V-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "ANODE_V (mV)")
        self.grid.SetCellValue(row, 1, "CAT_HF_V (mV)")
        self.grid.SetCellValue(row, 2, "CAT_LF_V (mV)")
        self.grid.SetCellValue(row, 3, "TEMP (C)")
        self.grid.SetCellValue(row, 4, "TANK_PRESSURE (mPSI)")
        self.grid.SetCellValue(row, 5, "CAT_PRESSURE (mPSI)")
        self.grid.SetCellValue(row, 6, "ANODE_PRESSURE (mPSI)")
        self.grid.SetCellValue(row, 7, "REG_PRESSURE m(PSI)")
        self.grid.SetCellValue(row, 8, "MSG_CNT")
        self.grid.SetCellValue(row, 9, "CAN_ERR")

        row += 3
        self.grid.SetRowLabelValue(row, "HK")
        self.grid.SetRowLabelValue(row+1, "HK-Data")
        self.grid.SetCellValue(row, 0, "CURRENT_28V (mA)")
        self.grid.SetCellValue(row, 1, "VOLTAGE_14V (mV)")
        self.grid.SetCellValue(row, 2, "CURRENT_14V (mA)")
        self.grid.SetCellValue(row, 3, "VOLTAGE_7A (mV)")
        self.grid.SetCellValue(row, 4, "CURRENT_7A (mA)")

        row += 3
        self.grid.SetRowLabelValue(row, "EFC")
        self.grid.SetRowLabelValue(row+1, "EFC-Data")
        self.grid.SetCellValue(row, 0, "CNT_MECCEMSB")
        self.grid.SetCellValue(row, 1, "CNT_UECCEMSB")
        self.grid.SetCellValue(row, 2, "CNT_MECCELSB")
        self.grid.SetCellValue(row, 3, "CNT_UECCELSB")

        row += 3
        self.grid.SetRowLabelValue(row, "SYS-MEM")
        self.grid.SetRowLabelValue(row+1, "SYS-MEM-Data")
        self.grid.SetCellValue(row, 0, "REGION_STAT")
        self.grid.SetCellValue(row, 1, "FAILED_REPAIRS")
        self.grid.SetCellValue(row, 2, "REPAIR_STAT")

    def write_display(self, row, col, val):
        try:
            self.grid.SetCellValue(row, col, str(val))
        except Exception as e:
            print(f"{e}")
            print(row,col, val)
