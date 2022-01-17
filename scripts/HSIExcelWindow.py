from AutogenTestScriptsGui import *

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
        self.grid.SetCellValue(row, 0, "VSEPIC")
        self.grid.SetCellValue(row, 1, "VIN")
        self.grid.SetCellValue(row, 2, "IOUT")
        self.grid.SetCellValue(row, 3, "DACOUT")
        self.grid.SetCellValue(row, 4, "LASTERR")
        self.grid.SetCellValue(row, 5, "CUR_OFT")
        self.grid.SetCellValue(row, 6, "MSG_CNT")
        self.grid.SetCellValue(row, 7, "CAN_ERR")

        # setup anode labels
        row += 3
        self.grid.SetRowLabelValue(row, "Anode")
        self.grid.SetRowLabelValue(row + 1, "A-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "VX")
        self.grid.SetCellValue(row, 1, "VY")
        self.grid.SetCellValue(row, 2, "VOUT")
        self.grid.SetCellValue(row, 3, "IOUT")
        self.grid.SetCellValue(row, 4, "DAC")
        self.grid.SetCellValue(row, 5, "LASTERR")
        self.grid.SetCellValue(row, 6, "CUR_OFT")
        self.grid.SetCellValue(row, 7, "HS_TEMP")
        self.grid.SetCellValue(row, 8, "MSG_CNT")
        self.grid.SetCellValue(row, 9, "CAN_ERR")

        # setup Magnet Outer labels
        row += 3
        self.grid.SetRowLabelValue(row, "Magnet Outer")
        self.grid.SetRowLabelValue(row + 1, "MO-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "VOUT")
        self.grid.SetCellValue(row, 1, "IOUT")
        self.grid.SetCellValue(row, 2, "DAC OUT")
        self.grid.SetCellValue(row, 3, "LASTERR")
        self.grid.SetCellValue(row, 4, "MSG_CNT")
        self.grid.SetCellValue(row, 5, "CAN_ERR")

        # setup Magnet Inner labels
        row += 3
        self.grid.SetRowLabelValue(row, "Magnet Inner")
        self.grid.SetRowLabelValue(row + 1, "MI-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "VOUT")
        self.grid.SetCellValue(row, 1, "IOUT")
        self.grid.SetCellValue(row, 2, "DAC OUT")
        self.grid.SetCellValue(row, 3, "LASTERR")
        self.grid.SetCellValue(row, 4, "MSG_CNT")
        self.grid.SetCellValue(row, 5, "CAN_ERR")

        # setup Valves labels
        row += 3
        self.grid.SetRowLabelValue(row, "Valves Outer")
        self.grid.SetRowLabelValue(row + 1, "V-Data")
        self.grid.SetRowLabelValue(row + 2, "")
        self.grid.SetCellValue(row, 0, "anode_v")
        self.grid.SetCellValue(row, 1, "cath_hf_v")
        self.grid.SetCellValue(row, 2, "cath_lf_v")
        self.grid.SetCellValue(row, 3, "temp")
        self.grid.SetCellValue(row, 4, "tank_pressure")
        self.grid.SetCellValue(row, 5, "cathode_pressure")
        self.grid.SetCellValue(row, 6, "anode_pressure")
        self.grid.SetCellValue(row, 7, "reg_pressure")
        self.grid.SetCellValue(row, 8, "MSG_CNT")
        self.grid.SetCellValue(row, 9, "CAN_ERR")

        row += 3
        self.grid.SetRowLabelValue(row, "HK")
        self.grid.SetRowLabelValue(row+1, "HK-Data")
        self.grid.SetCellValue(row, 0, "current_28v")
        self.grid.SetCellValue(row, 1, "sense_14v")
        self.grid.SetCellValue(row, 2, "current_14v")
        self.grid.SetCellValue(row, 3, "sense_7a")
        self.grid.SetCellValue(row, 4, "current_7a")

        row += 3
        self.grid.SetRowLabelValue(row, "EFC")
        self.grid.SetRowLabelValue(row+1, "EFC-Data")
        self.grid.SetCellValue(row, 0, "cnt_meccemsb")
        self.grid.SetCellValue(row, 1, "cnt_ueccemsb")
        self.grid.SetCellValue(row, 2, "cnt_meccelsb")
        self.grid.SetCellValue(row, 3, "cnt_ueccelsb")

        row += 3
        self.grid.SetRowLabelValue(row, "SYS-MEM")
        self.grid.SetRowLabelValue(row+1, "SYS-MEM-Data")
        self.grid.SetCellValue(row, 0, "region_stat")
        self.grid.SetCellValue(row, 1, "failed_repairs")
        self.grid.SetCellValue(row, 2, "repair_stat")

    def write_display(self, row, col, val):
        self.grid.SetCellValue(row, col, val)
