import sys
from threading import Thread
import wx, struct, time, traceback
from AutogenTestScriptsGui import *

class HSIExcelWindow(HSIExcelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.grid = self.m_hsiExcelGrid
        self.setupView()
        self.request_thread = None
        self.running = False
        self.hex_en = False

        self.Show(True)
        self.anode_row = 4
        self.keeper_row = 1
        self.magnets_outer_row = 7
        self.magnets_inner_row = 10
        self.valves_row = 13
        self.hkm_row = 15

    def handleHexEnable(self, ev):
        if ev.GetEventObject().GetValue():
            self.hex_en = True
        else:
            self.hex_en = False

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

        row+=3
        self.grid.SetRowLabelValue(row, "HKM")


    # def OnClose(self, event):
    #     sys.exit(0)

    def OnDestroy(self, event):
        self.running = False

    def postInit(self, loaded_classes=None):
        self.funcs = [
            #anode functions
            {"get_func": self.anode_diag.getVX, "data_row": self.anode_row, "data_col": 0,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getVY, "data_row": self.anode_row, "data_col": 1,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getVOUT, "data_row": self.anode_row, "data_col": 2,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getIOUT, "data_row": self.anode_row, "data_col": 3,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getDAC, "data_row": self.anode_row, "data_col": 4,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getLASTERR, "data_row": self.anode_row, "data_col": 5,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getHSTEMP, "data_row": self.anode_row, "data_col": 6,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getCURRENTOFT, "data_row": self.anode_row, "data_col": 7,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getCAN_CNT, "data_row": self.anode_row, "data_col": 8,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.anode_diag.getCAN_ERR_CNT, "data_row": self.anode_row, "data_col": 9,
             "on_failure": self.writeDisplayFailure},

            #keeper functions
            {"get_func": self.keeper_diag.getSEPICV, "data_row": self.keeper_row, "data_col": 0,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.keeper_diag.getHSIV, "data_row": self.keeper_row, "data_col": 1,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.keeper_diag.getIOUT, "data_row": self.keeper_row, "data_col": 2,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.keeper_diag.getDACOUT, "data_row": self.keeper_row, "data_col": 3,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.keeper_diag.getLASTERROR, "data_row": self.keeper_row, "data_col": 4,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.keeper_diag.getCURRENTOFT, "data_row": self.keeper_row, "data_col": 5,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.keeper_diag.getCAN_CNT, "data_row": self.keeper_row, "data_col": 6,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.keeper_diag.getCAN_ERR_CNT, "data_row": self.keeper_row, "data_col": 7,
             "on_failure": self.writeDisplayFailure},

            # magnet inner functions
            {"get_func": self.inner_magnet_diag.getVOUT, "data_row": self.magnets_inner_row, "data_col": 0,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.inner_magnet_diag.getIOUT, "data_row": self.magnets_inner_row, "data_col": 1,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.inner_magnet_diag.getDACOUT, "data_row": self.magnets_inner_row, "data_col": 2,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.inner_magnet_diag.getLASTERR, "data_row": self.magnets_inner_row, "data_col": 3,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.inner_magnet_diag.getCAN_CNT, "data_row": self.magnets_inner_row, "data_col": 4,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.inner_magnet_diag.getCAN_ERR_CNT, "data_row": self.magnets_inner_row, "data_col": 5,
             "on_failure": self.writeDisplayFailure},

            # magnet outer functions
            {"get_func": self.outer_magnet_diag.getVOUT, "data_row": self.magnets_outer_row, "data_col": 0,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.outer_magnet_diag.getIOUT, "data_row": self.magnets_outer_row, "data_col": 1,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.outer_magnet_diag.getDACOUT, "data_row": self.magnets_outer_row, "data_col": 2,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.outer_magnet_diag.getLASTERR, "data_row": self.magnets_outer_row, "data_col": 3,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.outer_magnet_diag.getCAN_CNT, "data_row": self.magnets_outer_row, "data_col": 4,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.outer_magnet_diag.getCAN_ERR_CNT, "data_row": self.magnets_outer_row, "data_col": 5,
             "on_failure": self.writeDisplayFailure},

            # valves functions
            {"get_func": self.valves_diag.get_cathode_low_flow, "data_row": self.valves_row, "data_col": 0,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_cathode_high_flow, "data_row": self.valves_row, "data_col": 1,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_anode_voltage, "data_row": self.valves_row, "data_col": 2,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_temperature, "data_row": self.valves_row, "data_col": 3,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_regulator_pressure, "data_row": self.valves_row, "data_col": 4,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_anode_pressure, "data_row": self.valves_row, "data_col": 5,
             "on_failure": self.writeDisplayFailure, "args":{"bold":True}},
            {"get_func": self.valves_diag.get_cathode_pressure, "data_row": self.valves_row, "data_col": 6,
             "on_failure": self.writeDisplayFailure, "args":{"bold":True}},
            {"get_func": self.valves_diag.get_tank_pressure, "data_row": self.valves_row, "data_col": 7,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_can_cnt, "data_row": self.valves_row, "data_col": 8,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.getCAN_ERR_CNT, "data_row": self.valves_row, "data_col": 9,
             "on_failure": self.writeDisplayFailure},

            # hkm functions
            {"get_func": self.valves_diag.get_cathode_low_flow, "data_row": self.hkm_row, "data_col": 0,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_cathode_high_flow, "data_row": self.hkm_row, "data_col": 1,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_anode_voltage, "data_row": self.hkm_row, "data_col": 2,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_temperature, "data_row": self.hkm_row, "data_col": 3,
             "on_failure": self.writeDisplayFailure},
            {"get_func": self.valves_diag.get_regulator_pressure, "data_row": self.hkm_row, "data_col": 4,
             "on_failure": self.writeDisplayFailure},
        ]
        self.m_hsiEnable.SetValue(False)
        # self.request_thread = Thread(target=self.readHsi)
        # self.running = True
        # self.request_thread.start()

    def handleThreadInit(self, event):
        if event.GetEventObject().GetValue():
            self.request_thread = Thread(target=self.readHsi)
            self.running = True
            self.request_thread.start()
        else:
            #kill the thread
            self.running = False

    def readHsi(self):
        """
        readHsi, rolls through the hsi, calling the callback on success
        """
        while self.running:
            for el in self.funcs:
                try:
                    self.try_read(el)
                    cb = el.get("on_success")
                    if cb != None:
                        cb(el)
                except Exception as e:
                    # print(traceback.format_exc())
                    invalid_callback = el.get("on_failure")
                    if invalid_callback != None:
                        invalid_callback(el, e)
                    # print(e)
            time.sleep(1)

    def try_read(self, func):
        """
        try_read, tries to get the value and then will write it to the this display.
        calls a callback if there.
        """
        val = func.get("get_func")()
        if self.hex_en:
            val = hex(val)
        data_row = func.get("data_row")
        data_col = func.get("data_col")
        callback = func.get("on_success")
        if data_row != None and data_col !=None:
            self.unpack_and_display(func, val)
        if callback != None:
            callback(val)

    def unpack_and_display(self, func, val):
        """
        """
        # print(f"val:{val}")
        # unpacked = struct.unpack("H", val)[0]  # ushort16
        data_row = func.get("data_row")
        data_col = func.get("data_col")
        args = func.get("args")

        if data_row != None and data_col !=None:
            if args != None:
                if args.get("bold"):
                    wx.CallAfter(self.grid.SetCellTextColour, data_row, data_col, wx.Colour( 255, 0, 0 ))
            wx.CallAfter(self.grid.SetCellValue, data_row, data_col, f"{val}")

    def writeDisplayFailure(self, element, e):
        data_row = element.get("data_row")
        data_col = element.get("data_col")
        if data_row != None and data_col !=None:
            wx.CallAfter(self.grid.SetCellValue,data_row, data_col, f"{e}")

    def write_display(self, row, col, val):
        self.grid.SetCellValue(row, col, val)