from enum import Enum

class TCS(Enum): #Thruster Control State
    """
        Thruster Control State, enums of the various states of the PPU.
    """
    TCS_CO_INVALID              = 0x0
    TCS_CO_INIT                 = 0x1
    TCS_CO_PREOP                = 0x2
    TCS_CO_OPERATIONAL          = 0x3
    TCS_CO_STOP                 = 0x4
    TCS_CO_MODE_NUM             = 0x5
    TCS_POWER_OFF               = 0x6
    TCS_TRANISTION_STANDBY      = 0x7
    TCS_STANDBY                 = 0x8
    TCS_TRANSITION_READY_MODE   = 0x9
    TCS_READY_MODE              = 0xA
    TCS_TRANSITION_STEADY_STATE = 0xB
    TCS_STEADY_STATE            = 0xC
    TCS_CONDITIONING            = 0xD
    TCS_BIT_TEST                = 0xE
    TCS_LOCKOUT                 = 0xF

class HSIDefines:
    """
    HSIDefines is a way to define the structure for the hsi gathering and decoding.
    """
    def __init__(self):
        self.keeper_index = "KeeperDiag"
        self.anode_index = "AnodeDiag"
        self.mag_outer_index = "MagnetOuterDiag"
        self.mag_inner_index = "MagnetInnerDiag"
        self.valves_index = "ValveDiag"
        self.hk_index = "HKDiag"
        self.hsi = {
            "a_vx": {"index": self.anode_index, "subindex": "ADC0", "type": "<H", "row": 4, "col": 0x0},  # 32bit
            "a_vy": {"index": self.anode_index, "subindex": "ADC1", "type": "<H", "row": 4, "col": 0x1},  # 32bit
            "a_vout": {"index": self.anode_index, "subindex": "ADC2", "type": "<H", "row": 4, "col": 0x2},  # 32bit
            "a_iout": {"index": self.anode_index, "subindex": "ADC3", "type": "<H", "row": 4, "col": 0x3},
            "a_dac": {"index": self.anode_index, "subindex": "ADC4", "type": "<H", "row": 4, "col": 0x4},
            "a_hs_temp": {"index": self.anode_index, "subindex": "ADC7", "type": "<H", "row": 4, "col": 0x7},
            "a_last_err": {"index": self.anode_index, "subindex": "ADC5", "type": "<H", "row": 4, "col": 0x5},
            "a_cur_oft": {"index": self.anode_index, "subindex": "ADC6", "type": "<H", "row": 4, "col": 0x6},
            "a_msg_cnt": {"index": self.anode_index, "subindex": "ADC8", "type": "<H", "row": 4, "col": 0x8},
            "a_can_err": {"index": self.anode_index, "subindex": "ADC9", "type": "<H", "row": 4, "col": 0x9},

            "k_v_sepic": {"index": self.keeper_index, "subindex": "ADC0", "type": "<H", "row": 1, "col": 0x0},  # 32bit
            "k_v_in": {"index": self.keeper_index, "subindex": "ADC1", "type": "<H", "row": 1, "col": 0x1},  # 32bit
            "k_i_out": {"index": self.keeper_index, "subindex": "ADC2", "type": "<H", "row": 1, "col": 0x2},
            "k_dac_out": {"index": self.keeper_index, "subindex": "ADC3", "type": "<H", "row": 1, "col": 0x3},
            "k_last_err": {"index": self.keeper_index, "subindex": "ADC4", "type": "<H", "row": 1, "col": 0x4},
            "k_cur_oft": {"index": self.keeper_index, "subindex": "ADC5", "type": "<H", "row": 1, "col": 0x5},
            "k_msg_cnt": {"index": self.keeper_index, "subindex": "ADC6", "type": "<H", "row": 1, "col": 0x6},
            "k_can_err": {"index": self.keeper_index, "subindex": "ADC7", "type": "<H", "row": 1, "col": 0x7},

            "mo_v_out": {"index": self.mag_inner_index, "subindex": "ADC0", "type": "<H", "row": 7, "col": 0},
            "mo_i_out": {"index": self.mag_inner_index, "subindex": "ADC1", "type": "<H", "row": 7, "col": 1},
            "mo_dac_out": {"index": self.mag_inner_index, "subindex": "ADC2", "type": "<H", "row": 7, "col": 2},
            "mo_last_err": {"index": self.mag_inner_index, "subindex": "ADC3", "type": "<H", "row": 7, "col": 3},
            "mo_msg_cnt": {"index": self.mag_inner_index, "subindex": "ADC4", "type": "<H", "row": 7, "col": 4},
            "mo_can_err": {"index": self.mag_inner_index, "subindex": "ADC5", "type": "<H", "row": 7, "col": 5},

            "mi_v_out": {"index": self.mag_outer_index, "subindex": "ADC0", "type": "<H", "row": 10, "col": 0},
            "mi_i_out": {"index": self.mag_outer_index, "subindex": "ADC1", "type": "<H", "row": 10, "col": 1},
            "mi_dac_out": {"index": self.mag_outer_index, "subindex": "ADC2", "type": "<H", "row": 10, "col": 2},
            "mi_last_err": {"index": self.mag_outer_index, "subindex": "ADC3", "type": "<H", "row": 10, "col": 3},
            "mi_msg_cnt": {"index": self.mag_outer_index, "subindex": "ADC4", "type": "<H", "row": 10, "col": 4},
            "mi_can_err": {"index": self.mag_outer_index, "subindex": "ADC5", "type": "<H", "row": 10, "col": 5},

            "va_anode_v": {"index": self.valves_index, "subindex": "ADC0", "type": "<H", "row": 13, "col": 0},
            "va_cathode_hf_v": {"index": self.valves_index, "subindex": "ADC1", "type": "<H", "row": 13, "col": 1},
            "va_cathode_lf_v": {"index": self.valves_index, "subindex": "ADC2", "type": "<H", "row": 13, "col": 2},
            "va_temperature": {"index": self.valves_index, "subindex": "ADC3", "type": "<H", "row": 13, "col": 3},
            # signed 32bit
            "va_tank_pressure": {"index": self.valves_index, "subindex": "ADC4", "type": "<H", "row": 13, "col": 4},
            # 32bit
            "va_cathode_pressure": {"index": self.valves_index, "subindex": "ADC5", "type": "<H", "row": 13,
                                    "col": 5},
            "va_anode_pressure": {"index": self.valves_index, "subindex": "ADC6", "type": "<H", "row": 13, "col": 6},
            "va_regulator_pressure": {"index": self.valves_index, "subindex": "ADC7", "type": "<H", "row": 13, "col": 7},
            "va_msg_cnt": {"index": self.valves_index, "subindex": "ADC8", "type": "<H", "row": 13, "col": 8},
            "va_can_err": {"index": self.valves_index, "subindex": "ADC9", "type": "<H", "row": 13, "col": 9},

            "hk_mA_28V": {"index": self.hk_index, "subindex": "ADC0", "type": "<H", "row": 16, "col": 0},
            "hk_mV_14V": {"index": self.hk_index, "subindex": "ADC1", "type": "<H", "row": 16, "col": 1},
            "hk_mA_14V": {"index": self.hk_index, "subindex": "ADC2", "type": "<H", "row": 16, "col": 2},
            "hk_mV_7VA": {"index": self.hk_index, "subindex": "ADC3", "type": "<H", "row": 16, "col": 3},
            "hk_mA_7VA": {"index": self.hk_index, "subindex": "ADC4", "type": "<H", "row": 16, "col": 4},

            "count_meccemsb": {"index": self.hk_index, "subindex": "ADC0", "type": "<H", "row": 19, "col": 0},
            "count_ueccemsb": {"index": self.hk_index, "subindex": "ADC1", "type": "<H", "row": 19, "col": 1},
            "count_meccelsb": {"index": self.hk_index, "subindex": "ADC2", "type": "<H", "row": 19, "col": 2},
            "count_ueccelsb": {"index": self.hk_index, "subindex": "ADC3", "type": "<H", "row": 19, "col": 3},

            "region_stat": {"index": self.hk_index, "subindex": "ADC0", "type": "<I", "row": 22, "col": 0},
            "failed_repairs": {"index": self.hk_index, "subindex": "ADC1", "type": "<I", "row": 22, "col": 1},
            "repair_stat": {"index": self.hk_index, "subindex": "ADC2", "type": "<I", "row": 22, "col": 2},
        }
        self.block_hsi = [
            # anode
            {"name": "a_vx", "type": "<I", "hex": False},
            {"name": "a_vy", "type": "<I", "hex": False},
            {"name": "a_vout", "type": "<I", "hex": False},
            {"name": "a_iout", "type": "<H", "hex": False},
            {"name": "a_dac", "type": "<H", "hex": False},
            {"name": "a_hs_temp", "type": "<H", "hex": False},
            {"name": "a_last_err", "type": "<H", "hex": False},
            {"name": "a_cur_oft", "type": "<H", "hex": False},
            {"name": "a_msg_cnt", "type": "<H", "hex": False},
            {"name": "a_can_err", "type": "<H", "hex": False},

            # keeper
            {"name": "k_v_sepic", "type": "<I", "hex": False},
            {"name": "k_v_in", "type": "<H", "hex": False},
            {"name": "k_i_out", "type": "<H", "hex": False},
            {"name": "k_dac_out", "type": "<H", "hex": False},
            {"name": "k_last_err", "type": "<H", "hex": False},
            {"name": "k_cur_oft", "type": "<H", "hex": False},
            {"name": "k_msg_cnt", "type": "<H", "hex": False},
            {"name": "k_can_err", "type": "<H", "hex": False},

            # magnet
            {"name": "mo_v_out", "type": "<H", "hex": False},
            {"name": "mo_i_out", "type": "<H", "hex": False},
            {"name": "mo_dac_out", "type": "<H", "hex": False},
            {"name": "mo_last_err", "type": "<H", "hex": False},
            {"name": "mo_msg_cnt", "type": "<H", "hex": False},
            {"name": "mo_can_err", "type": "<H", "hex": False},

            #magnet inner
            {"name": "mi_v_out", "type": "<H", "hex": False},
            {"name": "mi_i_out", "type": "<H", "hex": False},
            {"name": "mi_dac_out", "type": "<H", "hex": False},
            {"name": "mi_last_err", "type": "<H", "hex": False},
            {"name": "mi_msg_cnt", "type": "<H", "hex": False},
            {"name": "mi_can_err", "type": "<H", "hex": False},

            # valves
            {"name": "va_anode_v", "type": "<H", "hex": False},
            {"name": "va_cathode_hf_v", "type": "<H", "hex": False},
            {"name": "va_cathode_lf_v", "type": "<H", "hex": False},
            {"name": "va_temperature", "type": "<i", "hex": False},
            {"name": "va_tank_pressure", "type": "<I", "hex": False},
            {"name": "va_cathode_pressure", "type": "<H", "hex": False},
            {"name": "va_anode_pressure", "type": "<H", "hex": False},
            {"name": "va_regulator_pressure", "type": "<H", "hex": False},
            {"name": "va_msg_cnt", "type": "<H", "hex": False},
            {"name": "va_can_err", "type": "<H", "hex": False},

            # hk mem
            {"name": "hk_mA_28V", "type": "<H", "hex": False},
            {"name": "hk_mV_14V", "type": "<H", "hex": False},
            {"name": "hk_mA_14V", "type": "<H", "hex": False},
            {"name": "hk_mV_7VA", "type": "<H", "hex": False},
            {"name": "hk_mA_7VA", "type": "<H", "hex": False},

            # efc
            {"name": "count_meccemsb", "type": "<H", "hex": True},
            {"name": "count_ueccemsb", "type": "<H", "hex": True},
            {"name": "count_meccelsb", "type": "<H", "hex": True},
            {"name": "count_ueccelsb", "type": "<H", "hex": True},

            # sys-mem
            {"name": "region_stat", "type": "<I", "hex": True},
            {"name": "failed_repairs", "type": "<I", "hex": True},
            {"name": "repair_stat", "type": "<I", "hex": True},
        ]
