from enum import IntEnum
import struct

# ---- CANopen object indexes ----
IDX_THRUSTER_CMD   = 0x4000
IDX_COND_STATS     = 0x4001
IDX_SOFT_START     = 0x4002
IDX_SEQ_ENGINE     = 0x4200
IDX_HSI_BLOCK      = 0x3100
IDX_FAULT_STATUS   = 0x2831
IDX_TRACE_MSG      = 0x5001
IDX_SERIAL_NUMBER  = 0x5022
IDX_UPDATE         = 0x5500
NMT_BOOTUP_COB_ID  = 0x722

# ---- Thruster Command subindexes (IDX_THRUSTER_CMD) ----
SUB_READY_MODE     = 0x1
SUB_STEADY_STATE   = 0x2
SUB_SHUTDOWN       = 0x3
SUB_THRUST_POINT   = 0x4
SUB_THRUSTER_STATUS = 0x5
SUB_CONDITION      = 0x6
SUB_BIT            = 0x7
SUB_COND_CLEAR     = 0x8
SUB_AUTO_START     = 0x9

# ---- Soft-start / classic-start subindexes (IDX_SOFT_START) ----
SUB_SS_SETPOINT    = 0x2
SUB_SS_ANODE_PRES  = 0x4
SUB_SS_START_SELECT = 0x10

# ---- Sequence engine subindexes (IDX_SEQ_ENGINE) ----
SUB_SEQ_SELECT     = 0x4
SUB_SEQ_STEP       = 0x5
SUB_SEQ_CMD        = 0x6
SUB_SEQ_ARG        = 0x7

# ---- HSI block subindex (IDX_HSI_BLOCK) ----
SUB_HSI_BLOCK      = 0x1

# ---- Trace message subindex (IDX_TRACE_MSG) ----
SUB_TRACE_MSG      = 0x6

# ---- Fault status base subindex (IDX_FAULT_STATUS); entries start at SUB_FAULT_BASE ----
SUB_FAULT_BASE     = 0x2

# ---- Special write values ----
CMD_COND_CLEAR     = 0x63637772
CMD_SEQ_KEEPER_ON  = 0x01020706  # adjust keeper current in sequence engine
CMD_SEQ_KEEPER_OFF = 0x01040706  # turn keeper off in sequence engine

# Update Subindexes
UPDATE_SUB_DATA    = 1
UPDATE_SUB_VERIFY  = 2
UPDATE_SUB_INSTALL = 3




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
            # anode
            "a_vx":      {"index": self.anode_index, "subindex": "ADC0", "type": "<I", "row": 4, "col": 0x0, "hex": False},
            "a_vy":      {"index": self.anode_index, "subindex": "ADC1", "type": "<I", "row": 4, "col": 0x1, "hex": False},
            "a_vout":    {"index": self.anode_index, "subindex": "ADC2", "type": "<I", "row": 4, "col": 0x2, "hex": False},
            "a_iout":    {"index": self.anode_index, "subindex": "ADC3", "type": "<H", "row": 4, "col": 0x3, "hex": False},
            "a_dac":     {"index": self.anode_index, "subindex": "ADC4", "type": "<H", "row": 4, "col": 0x4, "hex": False},
            "a_hs_temp": {"index": self.anode_index, "subindex": "ADC7", "type": "<H", "row": 4, "col": 0x7, "hex": False},
            "a_last_err":{"index": self.anode_index, "subindex": "ADC5", "type": "<H", "row": 4, "col": 0x5, "hex": False},
            "a_cur_oft": {"index": self.anode_index, "subindex": "ADC6", "type": "<H", "row": 4, "col": 0x6, "hex": False},
            "a_msg_cnt": {"index": self.anode_index, "subindex": "ADC8", "type": "<H", "row": 4, "col": 0x8, "hex": False},
            "a_can_err": {"index": self.anode_index, "subindex": "ADC9", "type": "<H", "row": 4, "col": 0x9, "hex": False},

            # keeper
            "k_v_sepic": {"index": self.keeper_index, "subindex": "ADC0", "type": "<I", "row": 1, "col": 0x0, "hex": False},
            "k_v_in":    {"index": self.keeper_index, "subindex": "ADC1", "type": "<H", "row": 1, "col": 0x1, "hex": False},
            "k_i_out":   {"index": self.keeper_index, "subindex": "ADC2", "type": "<H", "row": 1, "col": 0x2, "hex": False},
            "k_dac_out": {"index": self.keeper_index, "subindex": "ADC3", "type": "<H", "row": 1, "col": 0x3, "hex": False},
            "k_last_err":{"index": self.keeper_index, "subindex": "ADC4", "type": "<H", "row": 1, "col": 0x4, "hex": False},
            "k_cur_oft": {"index": self.keeper_index, "subindex": "ADC5", "type": "<H", "row": 1, "col": 0x5, "hex": False},
            "k_msg_cnt": {"index": self.keeper_index, "subindex": "ADC6", "type": "<H", "row": 1, "col": 0x6, "hex": False},
            "k_can_err": {"index": self.keeper_index, "subindex": "ADC7", "type": "<H", "row": 1, "col": 0x7, "hex": False},

            # magnet outer
            "mo_v_out":   {"index": self.mag_inner_index, "subindex": "ADC0", "type": "<H", "row": 7, "col": 0, "hex": False},
            "mo_i_out":   {"index": self.mag_inner_index, "subindex": "ADC1", "type": "<H", "row": 7, "col": 1, "hex": False},
            "mo_dac_out": {"index": self.mag_inner_index, "subindex": "ADC2", "type": "<H", "row": 7, "col": 2, "hex": False},
            "mo_last_err":{"index": self.mag_inner_index, "subindex": "ADC3", "type": "<H", "row": 7, "col": 3, "hex": False},
            "mo_msg_cnt": {"index": self.mag_inner_index, "subindex": "ADC4", "type": "<H", "row": 7, "col": 4, "hex": False},
            "mo_can_err": {"index": self.mag_inner_index, "subindex": "ADC5", "type": "<H", "row": 7, "col": 5, "hex": False},

            # magnet inner
            "mi_v_out":   {"index": self.mag_outer_index, "subindex": "ADC0", "type": "<H", "row": 10, "col": 0, "hex": False},
            "mi_i_out":   {"index": self.mag_outer_index, "subindex": "ADC1", "type": "<H", "row": 10, "col": 1, "hex": False},
            "mi_dac_out": {"index": self.mag_outer_index, "subindex": "ADC2", "type": "<H", "row": 10, "col": 2, "hex": False},
            "mi_last_err":{"index": self.mag_outer_index, "subindex": "ADC3", "type": "<H", "row": 10, "col": 3, "hex": False},
            "mi_msg_cnt": {"index": self.mag_outer_index, "subindex": "ADC4", "type": "<H", "row": 10, "col": 4, "hex": False},
            "mi_can_err": {"index": self.mag_outer_index, "subindex": "ADC5", "type": "<H", "row": 10, "col": 5, "hex": False},

            # valves
            "va_anode_v":            {"index": self.valves_index, "subindex": "ADC0", "type": "<H", "row": 13, "col": 0, "hex": False},
            "va_cathode_hf_v":       {"index": self.valves_index, "subindex": "ADC1", "type": "<H", "row": 13, "col": 1, "hex": False},
            "va_cathode_lf_v":       {"index": self.valves_index, "subindex": "ADC2", "type": "<H", "row": 13, "col": 2, "hex": False},
            "va_temperature":        {"index": self.valves_index, "subindex": "ADC3", "type": "<i", "row": 13, "col": 3, "hex": False},  # signed 32bit
            "va_tank_pressure":      {"index": self.valves_index, "subindex": "ADC4", "type": "<I", "row": 13, "col": 4, "hex": False},  # 32bit
            "va_cathode_pressure":   {"index": self.valves_index, "subindex": "ADC5", "type": "<H", "row": 13, "col": 5, "hex": False},
            "va_anode_pressure":     {"index": self.valves_index, "subindex": "ADC6", "type": "<H", "row": 13, "col": 6, "hex": False},
            "va_regulator_pressure": {"index": self.valves_index, "subindex": "ADC7", "type": "<H", "row": 13, "col": 7, "hex": False},
            "va_msg_cnt":            {"index": self.valves_index, "subindex": "ADC8", "type": "<H", "row": 13, "col": 8, "hex": False},
            "va_can_err":            {"index": self.valves_index, "subindex": "ADC9", "type": "<H", "row": 13, "col": 9, "hex": False},

            # hk mem
            "hk_mA_28V": {"index": self.hk_index, "subindex": "ADC0", "type": "<H", "row": 16, "col": 0, "hex": False},
            "hk_mV_14V": {"index": self.hk_index, "subindex": "ADC1", "type": "<H", "row": 16, "col": 1, "hex": False},
            "hk_mA_14V": {"index": self.hk_index, "subindex": "ADC2", "type": "<H", "row": 16, "col": 2, "hex": False},
            "hk_mV_7VA": {"index": self.hk_index, "subindex": "ADC3", "type": "<H", "row": 16, "col": 3, "hex": False},
            "hk_mA_7VA": {"index": self.hk_index, "subindex": "ADC4", "type": "<H", "row": 16, "col": 4, "hex": False},

            # efc
            "count_meccemsb": {"index": self.hk_index, "subindex": "ADC0", "type": "<H", "row": 19, "col": 0, "hex": True},
            "count_ueccemsb": {"index": self.hk_index, "subindex": "ADC1", "type": "<H", "row": 19, "col": 1, "hex": True},
            "count_meccelsb": {"index": self.hk_index, "subindex": "ADC2", "type": "<H", "row": 19, "col": 2, "hex": True},
            "count_ueccelsb": {"index": self.hk_index, "subindex": "ADC3", "type": "<H", "row": 19, "col": 3, "hex": True},

            # sys-mem
            "region_stat":    {"index": self.hk_index, "subindex": "ADC0", "type": "<I", "row": 22, "col": 0, "hex": True},
            "failed_repairs": {"index": self.hk_index, "subindex": "ADC1", "type": "<I", "row": 22, "col": 1, "hex": True},
            "repair_stat":    {"index": self.hk_index, "subindex": "ADC2", "type": "<I", "row": 22, "col": 2, "hex": True},
        }

    def get_parse_str(self):
        """
        create a parse string like <IIII etc... from the table above.  Needs the type token to work.
        """
        return "<"+"".join(v["type"][1] for v in self.hsi.values())

    def parse_hsi_packet(self, data:bytes):
        if len(data) != 122:
            raise Exception("hsi data invalid length")
        parse_str = self.get_parse_str()
        unpacked_values = struct.unpack_from(parse_str, data)
        csv_row = {}
        for i, (name, value) in enumerate(self.hsi.items()):
            parsed_val = unpacked_values[i]
            if value.get("hex"):
                parsed_val = hex(parsed_val)
            if value.get("row") is not None and value.get("col") is not None:
                csv_row[name] = parsed_val
        return csv_row


class NMTD(IntEnum):
    INIT = 0
    STOPPED = 4
    OPERATIONAL = 5
    SLEEP = 80
    STANDBY = 96
    PRE_OPERATIONAL = 127

class TCS(IntEnum):
    """Thruster Control State — enums of the various states of the PPU."""
    INVALID                 = 0x0
    INIT                    = 0x1
    PREOP                   = 0x2
    OPERATIONAL             = 0x3
    STOP                    = 0x4
    MODE_NUM                = 0x5
    POWER_OFF               = 0x6
    TRANISTION_STANDBY      = 0x7
    STANDBY                 = 0x8
    TRANSITION_READY_MODE   = 0x9
    READY_MODE              = 0xA
    TRANSITION_STEADY_STATE = 0xB
    STEADY_STATE            = 0xC
    CONDITIONING            = 0xD
    BIT_TEST                = 0xE
    LOCKOUT                 = 0xF