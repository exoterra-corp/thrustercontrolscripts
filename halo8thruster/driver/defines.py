from enum import IntEnum
import struct

# =============================================================================
# CANopen object dictionary map
#
# One class per CANopen index. Each class carries the index value as
# `INDEX` and a nested `Sub(IntEnum)` enumerating its subindexes, so it is
# always visible which subindex belongs to which index.
#
# The flat IDX_*/SUB_* module-level aliases below some classes are kept
# because those exact names are imported elsewhere in this driver
# (state.py, conditoning.py, thruster_command.py, update.py, comms.py) via
# `from halo8thruster.driver.defines import *` -- so existing call sites
# don't need to change. Objects with no aliases are not referenced by any
# call site today.
# =============================================================================


class ThrusterCommand:
    """0x4000 -- thruster_command_object.c"""
    INDEX = 0x4000

    class Sub(IntEnum):
        READY_MODE      = 0x1  # "Keeper On"
        STEADY_STATE    = 0x2  # "Anode On"; upper 16 bits of the write value = steady-state timeout
        SHUTDOWN        = 0x3
        THRUST_POINT    = 0x4  # set throttle set point in throttle table
        THRUSTER_STATUS = 0x5
        CONDITION       = 0x6
        BIT             = 0x7
        COND_CLEAR      = 0x8  # clears conditioning stats unconditionally on ANY write -- not magic-gated here (see ConditionStatClear below for the real magic-gated clear at 0x5401)
        AUTO_START      = 0x9


IDX_THRUSTER_CMD    = ThrusterCommand.INDEX
SUB_READY_MODE      = ThrusterCommand.Sub.READY_MODE
SUB_STEADY_STATE    = ThrusterCommand.Sub.STEADY_STATE
SUB_SHUTDOWN        = ThrusterCommand.Sub.SHUTDOWN
SUB_THRUST_POINT    = ThrusterCommand.Sub.THRUST_POINT
SUB_THRUSTER_STATUS = ThrusterCommand.Sub.THRUSTER_STATUS
SUB_CONDITION       = ThrusterCommand.Sub.CONDITION
SUB_BIT             = ThrusterCommand.Sub.BIT
SUB_COND_CLEAR      = ThrusterCommand.Sub.COND_CLEAR
SUB_AUTO_START      = ThrusterCommand.Sub.AUTO_START


class ConditionStats:
    """0x4001 -- control_condition_object.c. Dynamically sized: sub 0x1 is
    the current step, then repeating triplets of (SEQ_STAT_COND,
    ELAPSED_MS, MONITOR_ERR) starting at sub 0x2, one triplet per
    conditioning step."""
    INDEX = 0x4001

    class Sub(IntEnum):
        CURRENT_STEP    = 0x1
        STEP_ENTRY_BASE = 0x2  # first step's SEQ_STAT_COND; each step occupies STEP_ENTRY_STRIDE subindexes (COND, ELAPSED_MS, MONITOR_ERR)

    STEP_ENTRY_STRIDE = 3


IDX_COND_STATS = ConditionStats.INDEX


class Throttle:
    """0x4002 -- throttle_object.c. Called IDX_SOFT_START in this driver
    historically, but firmware's own name for it is the throttle table."""
    INDEX = 0x4002

    class Sub(IntEnum):
        TABLE_SELECTOR      = 0x1
        ROW_SELECTOR        = 0x2   # selects the throttle-table row (1-based on the wire)
        CATHODE             = 0x3
        ANODE_FLOW          = 0x4   # anode flow setpoint (not pressure)
        VOLTAGE             = 0x5
        CURRENT             = 0x6
        INNER               = 0x7
        OUTER_I             = 0x8
        THRUST              = 0x9
        POWER               = 0xA
        KEEPER_ON           = 0xB
        TIMEOUT             = 0xC
        SETPOINT            = 0xD
        TABLE_LEN           = 0xE
        SETPOINT_PERSIST    = 0xF
        SOFTSTART_STEP_SIZE = 0x10


IDX_SOFT_START = Throttle.INDEX


class SequenceEngine:
    """0x4200 -- sequence_table_update_object.c (firmware symbols are
    SqncCtrl*; the file name is misleading)."""
    INDEX = 0x4200

    class Sub(IntEnum):
        STEP_COUNT       = 0x1
        EXECUTE          = 0x2
        CONDITION        = 0x3
        TABLE_SELECT     = 0x4  # value from SequenceTable below
        STEP_SELECT      = 0x5
        STEP_CMD_UPPER32 = 0x6  # upper 32 bits of the 64-bit step word (the "cmd")
        STEP_ARG_LOWER32 = 0x7  # lower 32 bits of the 64-bit step word (the "arg")

    class SequenceTable(IntEnum):
        """Values written to Sub.TABLE_SELECT. Mirrors firmware's
        sequence_t (client_control/control_sequence.h). Firmware itself
        warns these are position-dependent in its C enum
        (sequence_table_update_object.c) -- re-verify against
        control_sequence.h if firmware ever reorders it."""
        MODE_READY                 = 0
        MODE_STEADY_STATE          = 1
        MODE_EOL                   = 2
        THROTTLE_1                 = 3
        THROTTLE_2                 = 4
        THROTTLE_3                 = 5
        THROTTLE_4                 = 6
        THROTTLE_5                 = 7
        THROTTLE_6                 = 8
        EOL                        = 9
        COND_MAGS                  = 10
        COND_KEEPER_1              = 11
        COND_KEEPER_2              = 12
        COND_KEEPER_3              = 13
        COND_KEEPER_4              = 14
        COND_ANODE_1               = 15
        COND_EOL                   = 16
        BIT_USER_MOD               = 17
        BIT_LATCH_VALVE_OPEN       = 18
        BIT_LATCH_VALVE_CLOSE      = 19
        BIT_CATHODE_LOW_FLOW_CHECK = 20
        BIT_ANODE_VALVE_CHECK      = 21
        BIT_PCV_DRAIN              = 22
        BIT_INNER_COIL_TEST        = 23
        BIT_OUTER_COIL_TEST        = 24
        BIT_KEEPER_TEST            = 25
        BIT_ANODE_TEST             = 26
        CATH_LF_CHECK_AMBIENT      = 27
        ANODE_VALVE_CHECK_AMBIENT  = 28
        OPEN_ALL_VALVES            = 29
        BIT_EOL                    = 30


IDX_SEQ_ENGINE = SequenceEngine.INDEX
SUB_SEQ_SELECT = SequenceEngine.Sub.TABLE_SELECT
SUB_SEQ_STEP   = SequenceEngine.Sub.STEP_SELECT
SUB_SEQ_CMD    = SequenceEngine.Sub.STEP_CMD_UPPER32
SUB_SEQ_ARG    = SequenceEngine.Sub.STEP_ARG_LOWER32

# Literal step-command words taken from firmware's built-in sequence
# tables (control_thruster_start.c) -- not named macros in firmware, so
# these could go stale silently if those tables are ever edited.
CMD_SEQ_KEEPER_ON  = 0x01020706  # adjust keeper current in sequence engine
CMD_SEQ_KEEPER_OFF = 0x01040706  # turn keeper off in sequence engine


class HsiBlock:
    """0x3100 -- hk_hsi_object.c. A CO_DOMAIN object that is a raw memcpy
    of firmware's client_hsi_t struct (diag.h). Validated byte-for-byte
    against diag.h's client_hsi_t (field order, types, 52 fields, 122
    bytes total) -- see HSIDefines below, which decodes this blob.

    NOT the same object as HealthTick (0x5002) -- that's unrelated
    health-sample tick-rate config that firmware also informally calls
    "HSI"."""
    INDEX = 0x3100

    class Sub(IntEnum):
        DOMAIN_OBJ = 0x1


IDX_HSI_BLOCK = HsiBlock.INDEX
SUB_HSI_BLOCK = HsiBlock.Sub.DOMAIN_OBJ


class FaultStatus:
    """0x2831 -- fault_status_object.c."""
    INDEX = 0x2831

    class Sub(IntEnum):
        DUMP           = 0x1  # defined in firmware's enum but never actually ODAdd'ed -- reserved, not implemented
        DATA_WORD_BASE = 0x2  # 5 consecutive U32 words (DATA_WORD_BASE .. DATA_WORD_BASE+4), fr_stat.reg_start[0..4]


IDX_FAULT_STATUS = FaultStatus.INDEX
SUB_FAULT_BASE   = FaultStatus.Sub.DATA_WORD_BASE


class Trace:
    """0x5001 -- trace_object.c (_TRACE_ENABLE builds only)."""
    INDEX = 0x5001

    class Sub(IntEnum):
        FLAG             = 0x1
        HEAD             = 0x2
        TAIL             = 0x3
        SIZE             = 0x4
        MSG_HEAD         = 0x5
        MSG_TAIL         = 0x6
        PEEK_ADDR        = 0x7
        PEEK_VAL         = 0x8
        POKE_VAL         = 0x9
        LOCKOUT_OVERRIDE = 0xA  # write CMD_TRACE_LOCKOUT_OVERRIDE here to bypass a lockout timer (dev/debug)


IDX_TRACE_MSG = Trace.INDEX
SUB_TRACE_MSG = Trace.Sub.MSG_TAIL

CMD_TRACE_LOCKOUT_OVERRIDE = 0x6f6c6466  # 'fdlo'


class NodeId:
    """0x5022 -- node_id_object.c. This is the device's CANopen Node ID
    (persisted to flash), NOT a hardware serial number -- previously
    named IDX_SERIAL_NUMBER in this file, which was misleading. Writing
    here changes the device's own CAN node address."""
    INDEX = 0x5022

    class Sub(IntEnum):
        DATA = 0x1


IDX_NODE_ID = NodeId.INDEX


class SwUpdate:
    """0x5500 -- update_object.c."""
    INDEX = 0x5500

    class Sub(IntEnum):
        PROGRAM = 0x1
        VERIFY  = 0x2
        INSTALL = 0x3
        PENA    = 0x4  # "program enabled" flag, read-only


IDX_UPDATE        = SwUpdate.INDEX
UPDATE_SUB_DATA    = SwUpdate.Sub.PROGRAM
UPDATE_SUB_VERIFY  = SwUpdate.Sub.VERIFY
UPDATE_SUB_INSTALL = SwUpdate.Sub.INSTALL


NMT_BOOTUP_COB_ID = 0x722


# Value written to ThrusterCommand.Sub.COND_CLEAR (0x4000/0x8). Firmware
# ignores the value there (any write clears) -- this happens to be the
# same literal as CMD_CONDITION_STAT_CLEAR_MAGIC below, which IS actually
# checked, but at a different index/subindex (0x5401/0x1).
CMD_COND_CLEAR = 0x63637772


# -----------------------------------------------------------------------
# Objects registered by firmware but not currently used anywhere in this
# driver. Kept here for completeness/documentation; no flat aliases since
# nothing references them yet.
# -----------------------------------------------------------------------

class Keeper:
    """0x2100 -- keeper_object.c."""
    INDEX = 0x2100


class KeeperDiag:
    """0x3001 -- keeper_object.c. Individual-field view of the keeper
    portion of the 0x3100 HSI blob."""
    INDEX = 0x3001


class KeeperErrHistory:
    """0x3011 -- keeper_object.c. Dynamic-length error history."""
    INDEX = 0x3011


class Anode:
    """0x2200 -- anode_object.c."""
    INDEX = 0x2200


class AnodeDiag:
    """0x3002 -- anode_object.c."""
    INDEX = 0x3002


class AnodeErrHistory:
    """0x3012 -- anode_object.c."""
    INDEX = 0x3012


class Magnets:
    """0x2300 -- magnets_object.c."""
    INDEX = 0x2300


class MagnetsOuterDiag:
    """0x3003 -- magnets_object.c."""
    INDEX = 0x3003


class MagnetsOuterErrHistory:
    """0x3013 -- magnets_object.c."""
    INDEX = 0x3013


class MagnetsInnerDiag:
    """0x3004 -- magnets_object.c."""
    INDEX = 0x3004


class MagnetsInnerErrHistory:
    """0x3014 -- magnets_object.c."""
    INDEX = 0x3014


class Valves:
    """0x2500 -- valves_object.c."""
    INDEX = 0x2500


class ValvesDiag:
    """0x3005 -- valves_object.c."""
    INDEX = 0x3005


class ValvesErrHistory:
    """0x3015 -- valves_object.c."""
    INDEX = 0x3015


class HkmHsi:
    """0x3000 -- hk_hsi_object.c. Housekeeping ADCs + EFC counters +
    sys-mem stats exposed as INDIVIDUAL SDO fields (unlike the 0x3100
    domain blob).

    WARNING: its EFC/sys-mem field order is DIFFERENT from the 0x3100
    blob (count_meccelsb, count_meccemsb, count_ueccelsb, count_ueccemsb,
    failed_repairs, region_stat, repair_stat), and firmware exposes them
    as CO_UNSIGNED32, contradicting the ICD doc's stated UINT16 for these
    fields. Do NOT use this object as a reference for the 0x3100 layout --
    use HsiBlock / HSIDefines instead.
    """
    INDEX = 0x3000


class FaultReactionType:
    """0x2830 -- fault_status_object.c. Configures per-fault-code
    reaction type."""
    INDEX = 0x2830

    class Sub(IntEnum):
        FAULT_CODE_SELECT = 0x1
        REACTION_TYPE     = 0x2


class FirmwareVersions:
    """0x5000 -- firmware_versions_object.c. Write DEVICE_SELECT to choose
    which device's version row the rest of the subs expose."""
    INDEX = 0x5000

    class Sub(IntEnum):
        DEVICE_SELECT         = 0x1
        TC_VERSION            = 0x2
        TC_GIT_SHA            = 0x3
        EXEC_VERSION_COL_BASE = 0x4  # 6 consecutive columns, COL_BASE .. COL_BASE+5


class HealthTick:
    """0x5002 -- health_object.c. Health-sampling tick-rate config. NOT
    the HSI memory block -- that's HsiBlock at 0x3100. Firmware names
    this object "HSI" internally, which is a naming collision worth
    avoiding in Python."""
    INDEX = 0x5002

    class Sub(IntEnum):
        TICK_SET    = 0x1
        TICK_ENABLE = 0x2


class PowerControl:
    """0x5003 -- power_control_object.c. Each sub is a power-rail on/off
    switch (0 = off, nonzero = on)."""
    INDEX = 0x5003

    class Sub(IntEnum):
        MAGNET_PROCESSOR       = 0x1
        VALVE_14V              = 0x2
        VALVE_PROCESSOR        = 0x3
        THRUSTER_28V           = 0x4
        ANODE_KEEPER_PROCESSOR = 0x5
        POWER_DIAGNOSTIC_MODE  = 0x6


class MemCorrupter:
    """0x5005 -- mem_corrupter_object.c. Debug/self-test object for the
    IACM memory-repair subsystem."""
    INDEX = 0x5005

    class Sub(IntEnum):
        MEM_COMP_CORRUPT     = 0x1  # debug-build only
        STATUS               = 0x2  # IACM region status
        FAILED               = 0x3  # failed-repairs count, self-clearing on read
        UD_STAT              = 0x4  # "just updated" status, self-clearing
        IACM                 = 0x5  # raw domain dump of the IACM table
        FUNLOCK              = 0x6  # flash unlock/lock; 0 = unlock
        REPAIR_ENA           = 0x7
        LOCKBITS             = 0x8
        MS_VERIFY            = 0x9
        NVM_CORRUPT          = 0xA  # debug-build only
        IACM_REGION_ERASE    = 0xB  # debug-build only
        IACM_GET_CORRUPT_RR  = 0xC
        MEM_COMP_CORRUPT_ALL = 0xD  # debug-build only


class ClientControlUcv:
    """0x5100 -- client_control_ucv_object.c. Serial/lockout config plus a
    set of safety limits.

    NOTE: firmware also has limits_object.c (OD_INDEX_CONTROL_LIMITS),
    which duplicates these same limit fields (subindexes shifted by +3)
    -- but OD_INDEX_CONTROL_LIMITS is an undefined macro and its
    LimitsOD() is never called from user_object_config.c, so that file is
    dead/orphaned firmware code. Not represented here on purpose.
    """
    INDEX = 0x5100

    class Sub(IntEnum):
        SERIAL_BAUD               = 0x1
        LOCKOUT_TIME               = 0x2
        HSI_MISSES                 = 0x3
        KEEPER_OV_LIMIT             = 0x4
        KEEPER_SS_SHUTDOWN_LIMIT    = 0x5
        KEEPER_SS_HIGHWARN_LIMIT    = 0x6
        KEEPER_SS_HIGHCLEAR_LIMIT   = 0x7
        KEEPER_SS_LOW_WARN_LIMIT    = 0x8
        KEEPER_SS_LOW_CLEAR_LIMIT   = 0x9
        MAGNET_CURRENT_ERROR        = 0xA
        INPUT_POWER_LOW             = 0xB
        INPUT_POWER_HIGH            = 0xC


class ConditionLimit:
    """0x5101 -- control_condition_object.c. Per-sequence conditioning
    limits table."""
    INDEX = 0x5101

    class Sub(IntEnum):
        MONITOR_MS         = 0x1
        ADJUST_LIMIT_LOWER = 0x2
        ADJUST_LIMIT_UPPER = 0x3
        CURRENT_LIMIT      = 0x4
        MAX_LIMIT          = 0x5
        POWER_LIMIT        = 0x6
        VOLTAGE_LIMIT      = 0x7


class UserConfigVar:
    """0x5102 -- user_config_var_object.c.

    NOTE: firmware also defines OD_INDEX_CALIB_VALS = 0x5102, which
    collides with this index and is never referenced anywhere -- a
    dead/leftover define, not represented here.
    """
    INDEX = 0x5102

    class Sub(IntEnum):
        STORE = 0x1
        ERASE = 0x2


class ConditionStatClear:
    """0x5401 -- control_condition_object.c. The REAL magic-gated
    conditioning-stats clear (unlike ThrusterCommand.Sub.COND_CLEAR at
    0x4000/0x8, which clears unconditionally on any write). Write
    CMD_CONDITION_STAT_CLEAR_MAGIC to Sub.CLEAR to trigger it."""
    INDEX = 0x5401

    class Sub(IntEnum):
        CLEAR = 0x1


CMD_CONDITION_STAT_CLEAR_MAGIC = 0x63637772  # 'ccwr'


class Calib:
    """0x5501 -- calib_object.c. Subindex enum (CALIB_SUBIDX_*) is defined
    in an external valve_mcu.h not present in this repo -- exact numeric
    subindex values are unconfirmed, do not guess. Known field order from
    firmware usage: SELECT (choose transducer), SLOPE, OFFSET,
    PRESSURE_RATIO, KEEPER_BOLSTERING_CURRENT."""
    INDEX = 0x5501


# Update Subindexes (legacy aliases, see SwUpdate.Sub above)
UPDATE_SUB_DATA    = SwUpdate.Sub.PROGRAM
UPDATE_SUB_VERIFY  = SwUpdate.Sub.VERIFY
UPDATE_SUB_INSTALL = SwUpdate.Sub.INSTALL


class HSIDefines:
    """
    HSIDefines is a way to define the structure for the hsi gathering and decoding.

    Decodes the CANopen 0x3100/sub-1 domain blob (HsiBlock above). Field
    order/types/sizes here were validated byte-for-byte against firmware's
    client_hsi_t struct in
    halo-thruster-control/thruster-control/firmware/src/.../diag.h
    (#pragma pack(1), 52 fields, 122 bytes total) -- including the
    a_hs_temp field, which really does sit out of ADC-number order between
    a_dac and a_last_err. The "index"/"subindex" string labels below are
    internal/logical labels only (not real CANopen index/subindex values)
    and aren't consumed anywhere outside this file.
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
            "mo_v_out":   {"index": self.mag_outer_index, "subindex": "ADC0", "type": "<H", "row": 7, "col": 0, "hex": False},
            "mo_i_out":   {"index": self.mag_outer_index, "subindex": "ADC1", "type": "<H", "row": 7, "col": 1, "hex": False},
            "mo_dac_out": {"index": self.mag_outer_index, "subindex": "ADC2", "type": "<H", "row": 7, "col": 2, "hex": False},
            "mo_last_err":{"index": self.mag_outer_index, "subindex": "ADC3", "type": "<H", "row": 7, "col": 3, "hex": False},
            "mo_msg_cnt": {"index": self.mag_outer_index, "subindex": "ADC4", "type": "<H", "row": 7, "col": 4, "hex": False},
            "mo_can_err": {"index": self.mag_outer_index, "subindex": "ADC5", "type": "<H", "row": 7, "col": 5, "hex": False},

            # magnet inner
            "mi_v_out":   {"index": self.mag_inner_index, "subindex": "ADC0", "type": "<H", "row": 10, "col": 0, "hex": False},
            "mi_i_out":   {"index": self.mag_inner_index, "subindex": "ADC1", "type": "<H", "row": 10, "col": 1, "hex": False},
            "mi_dac_out": {"index": self.mag_inner_index, "subindex": "ADC2", "type": "<H", "row": 10, "col": 2, "hex": False},
            "mi_last_err":{"index": self.mag_inner_index, "subindex": "ADC3", "type": "<H", "row": 10, "col": 3, "hex": False},
            "mi_msg_cnt": {"index": self.mag_inner_index, "subindex": "ADC4", "type": "<H", "row": 10, "col": 4, "hex": False},
            "mi_can_err": {"index": self.mag_inner_index, "subindex": "ADC5", "type": "<H", "row": 10, "col": 5, "hex": False},

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

    @staticmethod
    def make_fake_hsi_packet() -> bytes:
        """
        Build a 122-byte HSI packet with unique values per field.
        Each value encodes its section (thousands digit) and field index within the section,
        so a misaligned display is immediately obvious.
        Values are packed in the exact order parse_hsi_packet() expects.

        Section prefixes:
        1xxx = Anode     2xxx = Keeper    3xxx = Mag Outer  4xxx = Mag Inner
        5xxx = Valves    6xxx = HK        7xxx = EFC         8xxx = SYS-MEM
        """
        return struct.pack(
            "<"
            "IIIHHHHHHH"    # anode:    1001-1010 (I I I H H H H H H H) = 3I+7H
            "IHHHHHHH"      # keeper:   2001-2008 (I H H H H H H H)     = 1I+7H
            "HHHHHH"        # mag out:  3001-3006
            "HHHHHH"        # mag in:   4001-4006
            "HHHiIHHHHH"   # valves:   5001-5010 (H H H i I H H H H H)
            "HHHHH"         # hk:       6001-6005
            "HHHH"          # efc:      7001-7004
            "III",          # sys-mem:  8001-8003
            # anode (10)
            1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
            # keeper (8)
            2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008,
            # mag outer (6)
            3001, 3002, 3003, 3004, 3005, 3006,
            # mag inner (6)
            4001, 4002, 4003, 4004, 4005, 4006,
            # valves (10) — va_temperature is signed i, va_tank_pressure is unsigned I
            5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010,
            # hk (5)
            6001, 6002, 6003, 6004, 6005,
            # efc (4) — displayed as hex, so 7001=0x1b59 etc.
            7001, 7002, 7003, 7004,
            # sys-mem (3) — displayed as hex, so 8001=0x1f41 etc.
            8001, 8002, 8003,
        )

class NMTD(IntEnum):
    INIT = 0
    STOPPED = 4
    OPERATIONAL = 5
    SLEEP = 80
    STANDBY = 96
    PRE_OPERATIONAL = 127

class NMTCommand(IntEnum):
    """NMT command bytes sent to the device (distinct from NMTD, which are resulting states)."""
    OPERATIONAL     = 0x1
    STOP            = 0x2
    PRE_OPERATIONAL = 0x80
    RESET_NODE      = 0x81

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
