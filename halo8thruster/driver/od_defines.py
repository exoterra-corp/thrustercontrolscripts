# ---- CANopen object indexes ----
IDX_THRUSTER_CMD   = 0x4000
IDX_COND_STATS     = 0x4001
IDX_SOFT_START     = 0x4002
IDX_SEQ_ENGINE     = 0x4200
IDX_HSI_BLOCK      = 0x3100
IDX_FAULT_STATUS   = 0x2831
IDX_TRACE_MSG      = 0x5001
IDX_SERIAL_NUMBER  = 0x5022
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