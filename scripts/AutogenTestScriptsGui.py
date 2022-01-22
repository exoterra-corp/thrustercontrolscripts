# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui
import wx.richtext
import wx.grid

###########################################################################
## Class ThrusterControlFrame
###########################################################################

class ThrusterControlFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Thruster Control", pos = wx.DefaultPosition, size = wx.Size( 1024,768 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 800,750 ), wx.DefaultSize )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWFRAME ) )

		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_fileMenu = wx.Menu()
		self.m_menuUpdateSam = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Update System Controller", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_fileMenu.Append( self.m_menuUpdateSam )

		self.m_fileMenu.AppendSeparator()

		self.m_menu_version = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Version: Develop", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_fileMenu.Append( self.m_menu_version )

		self.m_fileMenu.AppendSeparator()

		self.m_show_hsi_window = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Show HSI Window", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_fileMenu.Append( self.m_show_hsi_window )

		self.m_fileMenu.AppendSeparator()

		self.m_show_ver_info = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Query Ver Info", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_fileMenu.Append( self.m_show_ver_info )

		self.m_fileMenu.AppendSeparator()

		self.m_get_eds_file = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Download Eds File", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_fileMenu.Append( self.m_get_eds_file )

		self.m_fileMenu.AppendSeparator()

		self.m_menuExit = wx.MenuItem( self.m_fileMenu, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_fileMenu.Append( self.m_menuExit )

		self.m_menubar1.Append( self.m_fileMenu, u"File" )

		self.SetMenuBar( self.m_menubar1 )

		bSerialSizer = wx.BoxSizer( wx.VERTICAL )

		sbSerialSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Connection" ), wx.VERTICAL )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText2 = wx.StaticText( sbSerialSizer.GetStaticBox(), wx.ID_ANY, u"Connection Interface", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )

		bSizer4.Add( self.m_staticText2, 0, wx.ALL, 5 )

		m_serialchoiceChoices = []
		self.m_serialchoice = wx.Choice( sbSerialSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_serialchoiceChoices, 0 )
		self.m_serialchoice.SetSelection( 0 )
		bSizer4.Add( self.m_serialchoice, 1, wx.ALL, 5 )

		self.m_staticText21 = wx.StaticText( sbSerialSizer.GetStaticBox(), wx.ID_ANY, u"Baud Rate", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText21.Wrap( -1 )

		bSizer4.Add( self.m_staticText21, 0, wx.ALL, 5 )

		m_baudRateDropdownChoices = []
		self.m_baudRateDropdown = wx.Choice( sbSerialSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_baudRateDropdownChoices, 0 )
		self.m_baudRateDropdown.SetSelection( 0 )
		bSizer4.Add( self.m_baudRateDropdown, 0, wx.ALL, 5 )

		self.m_connectButton = wx.Button( sbSerialSizer.GetStaticBox(), wx.ID_ANY, u"Connect", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_connectButton, 1, wx.ALL, 5 )

		self.m_download_eds_btn = wx.Button( sbSerialSizer.GetStaticBox(), wx.ID_ANY, u"Download EDS", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4.Add( self.m_download_eds_btn, 0, wx.ALL, 5 )

		self.m_enable_error_popup = wx.CheckBox( sbSerialSizer.GetStaticBox(), wx.ID_ANY, u"EnableErrorPopup", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_enable_error_popup.SetValue(True)
		bSizer4.Add( self.m_enable_error_popup, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_staticText20 = wx.StaticText( sbSerialSizer.GetStaticBox(), wx.ID_ANY, u"NODE-ID 0x", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText20.Wrap( -1 )

		bSizer4.Add( self.m_staticText20, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_nodeIdspinCtrl = wx.SpinCtrl( sbSerialSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 22 )
		self.m_nodeIdspinCtrl.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNTEXT ) )

		bSizer4.Add( self.m_nodeIdspinCtrl, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		sbSerialSizer.Add( bSizer4, 0, wx.EXPAND, 5 )

		sbSizer34 = wx.StaticBoxSizer( wx.StaticBox( sbSerialSizer.GetStaticBox(), wx.ID_ANY, u"NMT State" ), wx.HORIZONTAL )

		self.m_staticText38 = wx.StaticText( sbSizer34.GetStaticBox(), wx.ID_ANY, u"Current NMT State:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38.Wrap( -1 )

		sbSizer34.Add( self.m_staticText38, 0, wx.ALL, 5 )

		self.m_nmtstate_display = wx.StaticText( sbSizer34.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_nmtstate_display.Wrap( -1 )

		sbSizer34.Add( self.m_nmtstate_display, 0, wx.ALL, 5 )

		self.m_init_button = wx.Button( sbSizer34.GetStaticBox(), wx.ID_ANY, u"INIT", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer34.Add( self.m_init_button, 0, wx.ALL, 5 )

		self.m_preop_button = wx.Button( sbSizer34.GetStaticBox(), wx.ID_ANY, u"PREOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer34.Add( self.m_preop_button, 0, wx.ALL, 5 )

		self.m_operational_button = wx.Button( sbSizer34.GetStaticBox(), wx.ID_ANY, u"OPERATIONAL", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer34.Add( self.m_operational_button, 0, wx.ALL, 5 )

		self.m_stop_button = wx.Button( sbSizer34.GetStaticBox(), wx.ID_ANY, u"STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer34.Add( self.m_stop_button, 0, wx.ALL, 5 )


		sbSerialSizer.Add( sbSizer34, 1, wx.EXPAND, 5 )


		bSerialSizer.Add( sbSerialSizer, 0, wx.EXPAND, 10 )

		sb = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Main Control" ), wx.VERTICAL )

		self.m_auinotebook1 = wx.aui.AuiNotebook( sb.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_TAB_EXTERNAL_MOVE|wx.aui.AUI_NB_TAB_MOVE )
		self.m_od_controltab = wx.Panel( self.m_auinotebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_odTree = wx.TreeCtrl( self.m_od_controltab, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE )
		bSizer8.Add( self.m_odTree, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer91 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer71 = wx.StaticBoxSizer( wx.StaticBox( self.m_od_controltab, wx.ID_ANY, u"Inspect" ), wx.VERTICAL )

		sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( sbSizer71.GetStaticBox(), wx.ID_ANY, u"EDS File Information" ), wx.VERTICAL )

		bSizer38 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText26 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"File Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )

		bSizer38.Add( self.m_staticText26, 0, wx.ALL, 5 )

		self.m_info_filename = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_info_filename.Wrap( -1 )

		bSizer38.Add( self.m_info_filename, 0, wx.ALL, 5 )


		sbSizer12.Add( bSizer38, 1, wx.EXPAND, 5 )

		bSizer381 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText261 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"File Version:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText261.Wrap( -1 )

		bSizer381.Add( self.m_staticText261, 0, wx.ALL, 5 )

		self.m_info_fileversion = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_info_fileversion.Wrap( -1 )

		bSizer381.Add( self.m_info_fileversion, 0, wx.ALL, 5 )


		sbSizer12.Add( bSizer381, 1, wx.EXPAND, 5 )

		bSizer3811 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText2611 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"File Revision:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2611.Wrap( -1 )

		bSizer3811.Add( self.m_staticText2611, 0, wx.ALL, 5 )

		self.m_info_filerevision = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_info_filerevision.Wrap( -1 )

		bSizer3811.Add( self.m_info_filerevision, 0, wx.ALL, 5 )


		sbSizer12.Add( bSizer3811, 1, wx.EXPAND, 5 )

		bSizer38111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText26111 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"Last Modified:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26111.Wrap( -1 )

		bSizer38111.Add( self.m_staticText26111, 0, wx.ALL, 5 )

		self.m_info_lastmodified = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_info_lastmodified.Wrap( -1 )

		bSizer38111.Add( self.m_info_lastmodified, 0, wx.ALL, 5 )


		sbSizer12.Add( bSizer38111, 1, wx.EXPAND, 5 )


		sbSizer71.Add( sbSizer12, 0, wx.EXPAND, 5 )

		sbSizer17 = wx.StaticBoxSizer( wx.StaticBox( sbSizer71.GetStaticBox(), wx.ID_ANY, u"Read / Write" ), wx.VERTICAL )

		sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Index / Subindex Selected" ), wx.HORIZONTAL )

		self.m_staticText22 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Index", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText22.Wrap( -1 )

		sbSizer11.Add( self.m_staticText22, 0, wx.ALL, 5 )

		self.m_indexset = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_indexset.Wrap( -1 )

		sbSizer11.Add( self.m_indexset, 1, wx.ALL, 5 )

		self.m_staticText24 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"SubIndex", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText24.Wrap( -1 )

		sbSizer11.Add( self.m_staticText24, 0, wx.ALL, 5 )

		self.m_subindexset = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_subindexset.Wrap( -1 )

		sbSizer11.Add( self.m_subindexset, 1, wx.ALL, 5 )


		sbSizer17.Add( sbSizer11, 1, wx.EXPAND, 5 )

		bSizer351 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_selectedStaticText = wx.StaticText( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Object Selected", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_selectedStaticText.Wrap( -1 )

		bSizer351.Add( self.m_selectedStaticText, 0, wx.ALL, 5 )


		sbSizer17.Add( bSizer351, 1, wx.EXPAND, 5 )

		bSizer35 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText511 = wx.StaticText( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Read And Write", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText511.Wrap( -1 )

		bSizer35.Add( self.m_staticText511, 0, wx.ALL, 5 )

		self.m_dataToReadWriteTextCntrl = wx.TextCtrl( sbSizer17.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer35.Add( self.m_dataToReadWriteTextCntrl, 0, wx.ALL, 5 )

		self.m_readButton = wx.Button( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Read", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer35.Add( self.m_readButton, 0, wx.ALL, 5 )

		self.m_writeButton = wx.Button( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Write", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer35.Add( self.m_writeButton, 0, wx.ALL, 5 )


		sbSizer17.Add( bSizer35, 10, wx.EXPAND, 5 )


		sbSizer71.Add( sbSizer17, 1, wx.EXPAND, 5 )


		bSizer91.Add( sbSizer71, 1, wx.EXPAND, 5 )


		bSizer8.Add( bSizer91, 1, wx.EXPAND, 5 )


		self.m_od_controltab.SetSizer( bSizer8 )
		self.m_od_controltab.Layout()
		bSizer8.Fit( self.m_od_controltab )
		self.m_auinotebook1.AddPage( self.m_od_controltab, u"OD R/W", False, wx.NullBitmap )
		self.m_ATMegaControl = wx.Panel( self.m_auinotebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		AtmegaTabSizer = wx.BoxSizer( wx.VERTICAL )

		Row1Sizer = wx.BoxSizer( wx.HORIZONTAL )

		KeeperSizer = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer82 = wx.StaticBoxSizer( wx.StaticBox( self.m_ATMegaControl, wx.ID_ANY, u"Keeper" ), wx.VERTICAL )

		bSizer222 = wx.BoxSizer( wx.VERTICAL )

		bSizer232 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer21 = wx.StaticBoxSizer( wx.StaticBox( sbSizer82.GetStaticBox(), wx.ID_ANY, u"Keeper Power Control" ), wx.HORIZONTAL )

		self.m_keeperOffButton = wx.Button( sbSizer21.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer21.Add( self.m_keeperOffButton, 1, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_keeperOnButton = wx.Button( sbSizer21.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer21.Add( self.m_keeperOnButton, 1, wx.ALIGN_CENTER|wx.ALL, 10 )


		bSizer232.Add( sbSizer21, 1, wx.EXPAND, 5 )


		bSizer222.Add( bSizer232, 0, wx.EXPAND, 5 )

		bSizer244 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText154 = wx.StaticText( sbSizer82.GetStaticBox(), wx.ID_ANY, u"Set SEPIC Voltage", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText154.Wrap( -1 )

		bSizer244.Add( self.m_staticText154, 0, wx.ALL, 5 )

		self.m_keeperSetVoltageTextCntrl = wx.TextCtrl( sbSizer82.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer244.Add( self.m_keeperSetVoltageTextCntrl, 0, wx.ALL, 5 )

		self.m_keeperWriteVoltageButton = wx.Button( sbSizer82.GetStaticBox(), wx.ID_ANY, u"Write Voltage", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer244.Add( self.m_keeperWriteVoltageButton, 0, wx.ALL, 5 )


		bSizer222.Add( bSizer244, 1, wx.EXPAND, 5 )

		bSizer252 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText162 = wx.StaticText( sbSizer82.GetStaticBox(), wx.ID_ANY, u"Voltage Applied  ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText162.Wrap( -1 )

		bSizer252.Add( self.m_staticText162, 0, wx.ALL, 5 )

		self.m_keeperVoltageAppliedTextCntrl = wx.TextCtrl( sbSizer82.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer252.Add( self.m_keeperVoltageAppliedTextCntrl, 0, wx.ALL, 5 )


		bSizer222.Add( bSizer252, 1, wx.EXPAND, 5 )

		bSizer2412 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1512 = wx.StaticText( sbSizer82.GetStaticBox(), wx.ID_ANY, u"        Set Current", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1512.Wrap( -1 )

		bSizer2412.Add( self.m_staticText1512, 0, wx.ALL, 5 )

		self.m_keeperSetCurrentTextCntrl = wx.TextCtrl( sbSizer82.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2412.Add( self.m_keeperSetCurrentTextCntrl, 0, wx.ALL, 5 )

		self.m_keeperWriteCurrent = wx.Button( sbSizer82.GetStaticBox(), wx.ID_ANY, u"Write Current", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2412.Add( self.m_keeperWriteCurrent, 0, wx.ALL, 5 )


		bSizer222.Add( bSizer2412, 1, wx.EXPAND, 5 )

		bSizer2422 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1522 = wx.StaticText( sbSizer82.GetStaticBox(), wx.ID_ANY, u"Current Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1522.Wrap( -1 )

		bSizer2422.Add( self.m_staticText1522, 0, wx.ALL, 5 )

		self.m_keeperGetCurrentAppliedTextCntrl = wx.TextCtrl( sbSizer82.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2422.Add( self.m_keeperGetCurrentAppliedTextCntrl, 0, wx.ALL, 5 )


		bSizer222.Add( bSizer2422, 1, wx.EXPAND, 5 )


		sbSizer82.Add( bSizer222, 0, wx.EXPAND, 5 )


		KeeperSizer.Add( sbSizer82, 0, wx.EXPAND, 5 )


		Row1Sizer.Add( KeeperSizer, 0, wx.EXPAND, 5 )

		AnodeSizer = wx.BoxSizer( wx.HORIZONTAL )

		AnodePowerControlSizer = wx.StaticBoxSizer( wx.StaticBox( self.m_ATMegaControl, wx.ID_ANY, u"Anode" ), wx.VERTICAL )

		bSizer221 = wx.BoxSizer( wx.VERTICAL )

		bSizer34 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer22 = wx.StaticBoxSizer( wx.StaticBox( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Anode Power Control" ), wx.HORIZONTAL )

		self.m_anodeOffButton = wx.Button( sbSizer22.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer22.Add( self.m_anodeOffButton, 1, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_anodeOnButton = wx.Button( sbSizer22.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer22.Add( self.m_anodeOnButton, 1, wx.ALIGN_CENTER|wx.ALL, 10 )


		bSizer34.Add( sbSizer22, 1, wx.EXPAND, 5 )


		bSizer221.Add( bSizer34, 0, wx.EXPAND, 5 )

		bSizer243 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText153 = wx.StaticText( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, u"        Set Voltage", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText153.Wrap( -1 )

		bSizer243.Add( self.m_staticText153, 0, wx.ALL, 5 )

		self.m_anodeSetVoltageTextCtrl = wx.TextCtrl( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer243.Add( self.m_anodeSetVoltageTextCtrl, 0, wx.ALL, 5 )

		self.m_anodeWriteVoltageButton = wx.Button( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Write Voltage", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer243.Add( self.m_anodeWriteVoltageButton, 0, wx.ALL, 5 )


		bSizer221.Add( bSizer243, 1, wx.EXPAND, 5 )

		bSizer251 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText161 = wx.StaticText( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Voltage Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText161.Wrap( -1 )

		bSizer251.Add( self.m_staticText161, 0, wx.ALL, 5 )

		self.m_anodeVoltageAppliedTextCntrl = wx.TextCtrl( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer251.Add( self.m_anodeVoltageAppliedTextCntrl, 0, wx.ALL, 5 )


		bSizer221.Add( bSizer251, 1, wx.EXPAND, 5 )

		bSizer2411 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1511 = wx.StaticText( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, u"        Set Current", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1511.Wrap( -1 )

		bSizer2411.Add( self.m_staticText1511, 0, wx.ALL, 5 )

		self.m_anodeSetCurrentTextCntrl = wx.TextCtrl( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2411.Add( self.m_anodeSetCurrentTextCntrl, 0, wx.ALL, 5 )

		self.m_anodeWriteCurrent = wx.Button( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Write Current", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2411.Add( self.m_anodeWriteCurrent, 0, wx.ALL, 5 )


		bSizer221.Add( bSizer2411, 1, wx.EXPAND, 5 )

		bSizer2421 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1521 = wx.StaticText( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Current Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1521.Wrap( -1 )

		bSizer2421.Add( self.m_staticText1521, 0, wx.ALL, 5 )

		self.m_anodeGetCurrentAppliedTextCntrl = wx.TextCtrl( AnodePowerControlSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2421.Add( self.m_anodeGetCurrentAppliedTextCntrl, 0, wx.ALL, 5 )


		bSizer221.Add( bSizer2421, 1, wx.EXPAND, 5 )


		AnodePowerControlSizer.Add( bSizer221, 0, wx.EXPAND, 5 )


		AnodeSizer.Add( AnodePowerControlSizer, 1, wx.EXPAND, 5 )


		Row1Sizer.Add( AnodeSizer, 2, wx.EXPAND, 5 )

		StatusSizer = wx.BoxSizer( wx.VERTICAL )

		self.m_refreshATMegaTabButton = wx.Button( self.m_ATMegaControl, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.DefaultSize, 0 )
		StatusSizer.Add( self.m_refreshATMegaTabButton, 0, wx.ALL, 5 )

		hsiSizer = wx.StaticBoxSizer( wx.StaticBox( self.m_ATMegaControl, wx.ID_ANY, u"HSI" ), wx.VERTICAL )

		self.m_HSIEnable = wx.Button( hsiSizer.GetStaticBox(), wx.ID_ANY, u"HSI Enable", wx.DefaultPosition, wx.DefaultSize, 0 )
		hsiSizer.Add( self.m_HSIEnable, 0, wx.ALL, 5 )

		self.m_HSIDisable = wx.Button( hsiSizer.GetStaticBox(), wx.ID_ANY, u"HSI Disable", wx.DefaultPosition, wx.DefaultSize, 0 )
		hsiSizer.Add( self.m_HSIDisable, 0, wx.ALL, 5 )

		bSizer461 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText37 = wx.StaticText( hsiSizer.GetStaticBox(), wx.ID_ANY, u"Ticker(MS)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText37.Wrap( -1 )

		bSizer461.Add( self.m_staticText37, 0, wx.ALL, 5 )

		self.m_HSITickTextCntrl = wx.TextCtrl( hsiSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer461.Add( self.m_HSITickTextCntrl, 0, wx.ALL, 5 )


		hsiSizer.Add( bSizer461, 0, wx.EXPAND, 5 )

		self.m_HSITickButton = wx.Button( hsiSizer.GetStaticBox(), wx.ID_ANY, u"Set HSI Tick", wx.DefaultPosition, wx.DefaultSize, 0 )
		hsiSizer.Add( self.m_HSITickButton, 0, wx.ALL, 5 )


		StatusSizer.Add( hsiSizer, 0, wx.EXPAND, 5 )

		sequencesSizer = wx.StaticBoxSizer( wx.StaticBox( self.m_ATMegaControl, wx.ID_ANY, u"Sequences" ), wx.VERTICAL )

		self.m_anodeStartupButton = wx.Button( sequencesSizer.GetStaticBox(), wx.ID_ANY, u"Anode Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		sequencesSizer.Add( self.m_anodeStartupButton, 0, wx.ALL, 5 )

		self.m_keeperStartupButton = wx.Button( sequencesSizer.GetStaticBox(), wx.ID_ANY, u"Keeper Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		sequencesSizer.Add( self.m_keeperStartupButton, 0, wx.ALL, 5 )


		StatusSizer.Add( sequencesSizer, 0, wx.EXPAND, 5 )


		Row1Sizer.Add( StatusSizer, 1, wx.EXPAND, 5 )

		PowerControlSizer = wx.StaticBoxSizer( wx.StaticBox( self.m_ATMegaControl, wx.ID_ANY, u"Power Control" ), wx.VERTICAL )

		bSizer472 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer161 = wx.StaticBoxSizer( wx.StaticBox( PowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Magnet Processor" ), wx.HORIZONTAL )

		self.m_magnetProcessorOffButton = wx.Button( sbSizer161.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer161.Add( self.m_magnetProcessorOffButton, 1, wx.ALL, 5 )

		self.m_magnetProcessorOnButton = wx.Button( sbSizer161.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer161.Add( self.m_magnetProcessorOnButton, 1, wx.ALL, 5 )


		bSizer472.Add( sbSizer161, 1, wx.EXPAND, 5 )


		PowerControlSizer.Add( bSizer472, 1, wx.EXPAND, 5 )

		bSizer4721 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer171 = wx.StaticBoxSizer( wx.StaticBox( PowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Valve 14V" ), wx.HORIZONTAL )

		self.m_valve14vOffButton = wx.Button( sbSizer171.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer171.Add( self.m_valve14vOffButton, 1, wx.ALL, 5 )

		self.m_valve14vOnButton = wx.Button( sbSizer171.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer171.Add( self.m_valve14vOnButton, 1, wx.ALL, 5 )


		bSizer4721.Add( sbSizer171, 1, wx.EXPAND, 5 )


		PowerControlSizer.Add( bSizer4721, 1, wx.EXPAND, 5 )

		bSizer4722 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer18 = wx.StaticBoxSizer( wx.StaticBox( PowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Valve Processor" ), wx.HORIZONTAL )

		self.m_valveProcessorOffButton = wx.Button( sbSizer18.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer18.Add( self.m_valveProcessorOffButton, 1, wx.ALL, 5 )

		self.m_valveProcessorOnButton = wx.Button( sbSizer18.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer18.Add( self.m_valveProcessorOnButton, 1, wx.ALL, 5 )


		bSizer4722.Add( sbSizer18, 1, wx.EXPAND, 5 )


		PowerControlSizer.Add( bSizer4722, 1, wx.EXPAND, 5 )

		bSizer4723 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer19 = wx.StaticBoxSizer( wx.StaticBox( PowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Thruster 28V" ), wx.HORIZONTAL )

		self.m_thruster28vOffButton = wx.Button( sbSizer19.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer19.Add( self.m_thruster28vOffButton, 1, wx.ALL, 5 )

		self.m_thruster28vOnButton = wx.Button( sbSizer19.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer19.Add( self.m_thruster28vOnButton, 1, wx.ALL, 5 )


		bSizer4723.Add( sbSizer19, 1, wx.EXPAND, 5 )


		PowerControlSizer.Add( bSizer4723, 1, wx.EXPAND, 5 )

		bSizer4724 = wx.BoxSizer( wx.VERTICAL )

		sbSizer20 = wx.StaticBoxSizer( wx.StaticBox( PowerControlSizer.GetStaticBox(), wx.ID_ANY, u"Anode and Keeper Processor" ), wx.HORIZONTAL )

		self.m_AnodeKeeperProcessorOffButton = wx.Button( sbSizer20.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer20.Add( self.m_AnodeKeeperProcessorOffButton, 1, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_AnodeKeeperProcessorOnButton = wx.Button( sbSizer20.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer20.Add( self.m_AnodeKeeperProcessorOnButton, 1, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer4724.Add( sbSizer20, 1, wx.EXPAND, 5 )


		PowerControlSizer.Add( bSizer4724, 1, wx.EXPAND, 5 )


		Row1Sizer.Add( PowerControlSizer, 0, wx.EXPAND, 5 )


		AtmegaTabSizer.Add( Row1Sizer, 0, wx.EXPAND, 5 )

		Row2 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer1021 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer821 = wx.StaticBoxSizer( wx.StaticBox( self.m_ATMegaControl, wx.ID_ANY, u"Magnet" ), wx.VERTICAL )

		bSizer471 = wx.BoxSizer( wx.VERTICAL )

		bSizer561 = wx.BoxSizer( wx.VERTICAL )

		sbSizer37 = wx.StaticBoxSizer( wx.StaticBox( sbSizer821.GetStaticBox(), wx.ID_ANY, u"Magnet Power Control" ), wx.HORIZONTAL )

		self.m_turnOnMagnetButton = wx.Button( sbSizer37.GetStaticBox(), wx.ID_ANY, u"ON", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer37.Add( self.m_turnOnMagnetButton, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_turnOffMagnetButton = wx.Button( sbSizer37.GetStaticBox(), wx.ID_ANY, u"OFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer37.Add( self.m_turnOffMagnetButton, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_magnetSyncButton = wx.Button( sbSizer37.GetStaticBox(), wx.ID_ANY, u"SYNC", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer37.Add( self.m_magnetSyncButton, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer561.Add( sbSizer37, 0, wx.EXPAND, 5 )


		bSizer471.Add( bSizer561, 1, wx.EXPAND, 5 )

		bSizer40 = wx.BoxSizer( wx.VERTICAL )

		bSizer483 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText2811 = wx.StaticText( sbSizer821.GetStaticBox(), wx.ID_ANY, u"Inner Current (Amps)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2811.Wrap( -1 )

		bSizer483.Add( self.m_staticText2811, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_magnetAmpsTextCntrl = wx.TextCtrl( sbSizer821.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer483.Add( self.m_magnetAmpsTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText281 = wx.StaticText( sbSizer821.GetStaticBox(), wx.ID_ANY, u"Outer to Inner Ratio", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText281.Wrap( -1 )

		bSizer483.Add( self.m_staticText281, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_magnetRatioTextCntrl = wx.TextCtrl( sbSizer821.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer483.Add( self.m_magnetRatioTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer40.Add( bSizer483, 0, wx.EXPAND, 5 )

		bSizer4811 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText28211 = wx.StaticText( sbSizer821.GetStaticBox(), wx.ID_ANY, u"Inner Current Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28211.Wrap( -1 )

		bSizer4811.Add( self.m_staticText28211, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_magnetInnerCurrentTextCntrl = wx.TextCtrl( sbSizer821.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4811.Add( self.m_magnetInnerCurrentTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText2821 = wx.StaticText( sbSizer821.GetStaticBox(), wx.ID_ANY, u"Outer Current Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2821.Wrap( -1 )

		bSizer4811.Add( self.m_staticText2821, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_magnetOuterCurrentTextCntrl = wx.TextCtrl( sbSizer821.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer4811.Add( self.m_magnetOuterCurrentTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer40.Add( bSizer4811, 0, wx.EXPAND, 5 )

		self.m_setAmpsAndRatioButton = wx.Button( sbSizer821.GetStaticBox(), wx.ID_ANY, u"Set Amps / Set Ratio", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer40.Add( self.m_setAmpsAndRatioButton, 0, wx.ALL|wx.EXPAND, 0 )


		bSizer471.Add( bSizer40, 2, wx.EXPAND, 5 )


		sbSizer821.Add( bSizer471, 1, wx.EXPAND, 5 )


		bSizer1021.Add( sbSizer821, 1, wx.EXPAND, 5 )


		Row2.Add( bSizer1021, 1, wx.EXPAND, 5 )

		bSizer1022 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer822 = wx.StaticBoxSizer( wx.StaticBox( self.m_ATMegaControl, wx.ID_ANY, u"Valves" ), wx.VERTICAL )

		bSizer47 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer56 = wx.BoxSizer( wx.VERTICAL )

		self.m_openLatchValve = wx.Button( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Open Latch Valve", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer56.Add( self.m_openLatchValve, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_closeLatchValve = wx.Button( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Close Latch Valve", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer56.Add( self.m_closeLatchValve, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer47.Add( bSizer56, 1, wx.EXPAND, 5 )

		bSizer48 = wx.BoxSizer( wx.VERTICAL )

		self.m_setCathodeHFButton = wx.Button( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Cathode HF", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer48.Add( self.m_setCathodeHFButton, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_cathodeHFTextCntrl = wx.TextCtrl( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer48.Add( self.m_cathodeHFTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline4 = wx.StaticLine( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer48.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticText28 = wx.StaticText( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Cathode HF Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )

		bSizer48.Add( self.m_staticText28, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_cathodeAppliedHFTextCntrl = wx.TextCtrl( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer48.Add( self.m_cathodeAppliedHFTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer47.Add( bSizer48, 1, wx.EXPAND, 5 )

		bSizer481 = wx.BoxSizer( wx.VERTICAL )

		self.m_setCathodeLFButton = wx.Button( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Cathode LF", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer481.Add( self.m_setCathodeLFButton, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_cathodeLFTextCntrl = wx.TextCtrl( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer481.Add( self.m_cathodeLFTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline5 = wx.StaticLine( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer481.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticText282 = wx.StaticText( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Cathode LF Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText282.Wrap( -1 )

		bSizer481.Add( self.m_staticText282, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_cathodeAppliedLFTextCntrl = wx.TextCtrl( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer481.Add( self.m_cathodeAppliedLFTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer47.Add( bSizer481, 1, wx.EXPAND, 5 )

		bSizer482 = wx.BoxSizer( wx.VERTICAL )

		self.m_setAnodeFlowButton = wx.Button( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Anode Flow", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer482.Add( self.m_setAnodeFlowButton, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_anodeFlowTextCntrl = wx.TextCtrl( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer482.Add( self.m_anodeFlowTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline6 = wx.StaticLine( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer482.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticText283 = wx.StaticText( sbSizer822.GetStaticBox(), wx.ID_ANY, u"Anode Flow Applied", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText283.Wrap( -1 )

		bSizer482.Add( self.m_staticText283, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_anodeFlowAppliedTextCntrl = wx.TextCtrl( sbSizer822.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer482.Add( self.m_anodeFlowAppliedTextCntrl, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer47.Add( bSizer482, 1, wx.EXPAND, 5 )


		sbSizer822.Add( bSizer47, 1, wx.EXPAND, 5 )


		bSizer1022.Add( sbSizer822, 1, wx.EXPAND, 5 )


		Row2.Add( bSizer1022, 1, wx.EXPAND, 5 )


		AtmegaTabSizer.Add( Row2, 1, wx.EXPAND, 5 )


		self.m_ATMegaControl.SetSizer( AtmegaTabSizer )
		self.m_ATMegaControl.Layout()
		AtmegaTabSizer.Fit( self.m_ATMegaControl )
		self.m_auinotebook1.AddPage( self.m_ATMegaControl, u"ATMega Control", False, wx.NullBitmap )
		self.m_throttle_control_tab = wx.Panel( self.m_auinotebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer462 = wx.BoxSizer( wx.VERTICAL )

		sbSizer162 = wx.StaticBoxSizer( wx.StaticBox( self.m_throttle_control_tab, wx.ID_ANY, u"Control" ), wx.VERTICAL )

		sbSizer41 = wx.StaticBoxSizer( wx.StaticBox( sbSizer162.GetStaticBox(), wx.ID_ANY, u"Anode Voltage" ), wx.HORIZONTAL )

		bSizer71 = wx.BoxSizer( wx.VERTICAL )

		bSizer60 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText3811 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Start Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3811.Wrap( -1 )

		bSizer60.Add( self.m_staticText3811, 0, wx.ALL, 8 )

		self.m_staticText381 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Stop Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText381.Wrap( -1 )

		bSizer60.Add( self.m_staticText381, 0, wx.ALL, 8 )

		self.m_staticText3812 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Step Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3812.Wrap( -1 )

		bSizer60.Add( self.m_staticText3812, 0, wx.ALL, 8 )

		self.m_staticText38121 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Slew Time (s)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38121.Wrap( -1 )

		bSizer60.Add( self.m_staticText38121, 0, wx.ALL, 8 )


		bSizer71.Add( bSizer60, 0, wx.EXPAND, 5 )

		bSizer601 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_anode_startvalue_text = wx.TextCtrl( sbSizer41.GetStaticBox(), wx.ID_ANY, u"100", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_startvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601.Add( self.m_slew_anode_startvalue_text, 0, wx.ALL, 5 )

		self.m_slew_anode_stopvalue_text = wx.TextCtrl( sbSizer41.GetStaticBox(), wx.ID_ANY, u"150", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_stopvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601.Add( self.m_slew_anode_stopvalue_text, 0, wx.ALL, 5 )

		self.m_slew_anode_inc_value_text = wx.TextCtrl( sbSizer41.GetStaticBox(), wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_inc_value_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601.Add( self.m_slew_anode_inc_value_text, 0, wx.ALL, 5 )

		self.m_slew_anode_sweep_time_text = wx.TextCtrl( sbSizer41.GetStaticBox(), wx.ID_ANY, u"60", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_sweep_time_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601.Add( self.m_slew_anode_sweep_time_text, 0, wx.ALL, 5 )


		bSizer71.Add( bSizer601, 0, wx.EXPAND, 5 )


		sbSizer41.Add( bSizer71, 1, wx.EXPAND, 5 )

		bSizer72 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer73 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer73.SetMinSize( wx.Size( 100,-1 ) )
		self.m_staticText46 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Step Num:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText46.Wrap( -1 )

		bSizer73.Add( self.m_staticText46, 0, wx.ALL, 5 )

		self.m_slew_anode_step_num_text = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_step_num_text.Wrap( -1 )

		self.m_slew_anode_step_num_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer73.Add( self.m_slew_anode_step_num_text, 0, wx.ALL, 5 )


		bSizer72.Add( bSizer73, 0, wx.EXPAND, 5 )

		bSizer77 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText44 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Delay Steps:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText44.Wrap( -1 )

		bSizer77.Add( self.m_staticText44, 0, wx.ALL, 5 )

		self.m_slew_anode_delay_steps_text = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_delay_steps_text.Wrap( -1 )

		self.m_slew_anode_delay_steps_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer77.Add( self.m_slew_anode_delay_steps_text, 1, wx.ALL, 5 )


		bSizer72.Add( bSizer77, 0, wx.EXPAND, 5 )

		bSizer771 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText441 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Current Step:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText441.Wrap( -1 )

		bSizer771.Add( self.m_staticText441, 0, wx.ALL, 5 )

		self.m_slew_anode_current_step = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_current_step.Wrap( -1 )

		self.m_slew_anode_current_step.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_anode_current_step.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer771.Add( self.m_slew_anode_current_step, 0, wx.ALL, 5 )


		bSizer72.Add( bSizer771, 0, wx.EXPAND, 5 )

		bSizer7711 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText4411 = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Current Value:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4411.Wrap( -1 )

		bSizer7711.Add( self.m_staticText4411, 0, wx.ALL, 5 )

		self.m_slew_anode_current_value = wx.StaticText( sbSizer41.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_current_value.Wrap( -1 )

		self.m_slew_anode_current_value.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_anode_current_value.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer7711.Add( self.m_slew_anode_current_value, 0, wx.ALL, 5 )


		bSizer72.Add( bSizer7711, 0, wx.EXPAND, 5 )


		sbSizer41.Add( bSizer72, 0, wx.EXPAND, 5 )

		bSizer602 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_anode_start_sweep_btn = wx.Button( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Start Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer602.Add( self.m_slew_anode_start_sweep_btn, 0, wx.ALL, 5 )

		self.m_slew_anode_stop_sweep_btn = wx.Button( sbSizer41.GetStaticBox(), wx.ID_ANY, u"Stop Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer602.Add( self.m_slew_anode_stop_sweep_btn, 0, wx.ALL, 5 )


		sbSizer41.Add( bSizer602, 0, wx.EXPAND, 5 )


		sbSizer162.Add( sbSizer41, 0, wx.EXPAND, 5 )

		sbSizer411 = wx.StaticBoxSizer( wx.StaticBox( sbSizer162.GetStaticBox(), wx.ID_ANY, u"Anode Current" ), wx.HORIZONTAL )

		bSizer711 = wx.BoxSizer( wx.VERTICAL )

		bSizer603 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText38111 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Start Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38111.Wrap( -1 )

		bSizer603.Add( self.m_staticText38111, 0, wx.ALL, 8 )

		self.m_staticText3813 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Stop Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3813.Wrap( -1 )

		bSizer603.Add( self.m_staticText3813, 0, wx.ALL, 8 )

		self.m_staticText38122 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Step Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38122.Wrap( -1 )

		bSizer603.Add( self.m_staticText38122, 0, wx.ALL, 8 )

		self.m_staticText381211 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Slew Time (s)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText381211.Wrap( -1 )

		bSizer603.Add( self.m_staticText381211, 0, wx.ALL, 8 )


		bSizer711.Add( bSizer603, 0, wx.EXPAND, 5 )

		bSizer6011 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_anode_cu_startvalue_text = wx.TextCtrl( sbSizer411.GetStaticBox(), wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_startvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011.Add( self.m_slew_anode_cu_startvalue_text, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_stopvalue_text = wx.TextCtrl( sbSizer411.GetStaticBox(), wx.ID_ANY, u"2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_stopvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011.Add( self.m_slew_anode_cu_stopvalue_text, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_inc_value_text = wx.TextCtrl( sbSizer411.GetStaticBox(), wx.ID_ANY, u".1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_inc_value_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011.Add( self.m_slew_anode_cu_inc_value_text, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_sweep_time_text = wx.TextCtrl( sbSizer411.GetStaticBox(), wx.ID_ANY, u"60", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_sweep_time_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011.Add( self.m_slew_anode_cu_sweep_time_text, 0, wx.ALL, 5 )


		bSizer711.Add( bSizer6011, 0, wx.EXPAND, 5 )


		sbSizer411.Add( bSizer711, 1, wx.EXPAND, 5 )

		bSizer721 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer731 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer731.SetMinSize( wx.Size( 100,-1 ) )
		self.m_staticText461 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Step Num:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText461.Wrap( -1 )

		bSizer731.Add( self.m_staticText461, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_step_num_text = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_step_num_text.Wrap( -1 )

		self.m_slew_anode_cu_step_num_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer731.Add( self.m_slew_anode_cu_step_num_text, 0, wx.ALL, 5 )


		bSizer721.Add( bSizer731, 0, wx.EXPAND, 5 )

		bSizer772 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText442 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Delay Steps:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText442.Wrap( -1 )

		bSizer772.Add( self.m_staticText442, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_delay_steps_text = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_delay_steps_text.Wrap( -1 )

		self.m_slew_anode_cu_delay_steps_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer772.Add( self.m_slew_anode_cu_delay_steps_text, 0, wx.ALL, 5 )


		bSizer721.Add( bSizer772, 0, wx.EXPAND, 5 )

		bSizer7712 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText4412 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Current Step:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4412.Wrap( -1 )

		bSizer7712.Add( self.m_staticText4412, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_current_step = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_current_step.Wrap( -1 )

		self.m_slew_anode_cu_current_step.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_anode_cu_current_step.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer7712.Add( self.m_slew_anode_cu_current_step, 0, wx.ALL, 5 )


		bSizer721.Add( bSizer7712, 0, wx.EXPAND, 5 )

		bSizer77111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText44111 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Current Value:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText44111.Wrap( -1 )

		bSizer77111.Add( self.m_staticText44111, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_current_value = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_cu_current_value.Wrap( -1 )

		self.m_slew_anode_cu_current_value.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_anode_cu_current_value.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer77111.Add( self.m_slew_anode_cu_current_value, 0, wx.ALL, 5 )


		bSizer721.Add( bSizer77111, 0, wx.EXPAND, 5 )


		sbSizer411.Add( bSizer721, 0, wx.EXPAND, 5 )

		bSizer6021 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_anode_cu_start_sweep_btn = wx.Button( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Start Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6021.Add( self.m_slew_anode_cu_start_sweep_btn, 0, wx.ALL, 5 )

		self.m_slew_anode_cu_stop_sweep_btn = wx.Button( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Stop Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6021.Add( self.m_slew_anode_cu_stop_sweep_btn, 0, wx.ALL, 5 )


		sbSizer411.Add( bSizer6021, 0, wx.EXPAND, 5 )


		sbSizer162.Add( sbSizer411, 0, wx.EXPAND, 5 )

		sbSizer4111 = wx.StaticBoxSizer( wx.StaticBox( sbSizer162.GetStaticBox(), wx.ID_ANY, u"Anode Flow" ), wx.HORIZONTAL )

		bSizer7111 = wx.BoxSizer( wx.VERTICAL )

		bSizer6031 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText381111 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Start Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText381111.Wrap( -1 )

		bSizer6031.Add( self.m_staticText381111, 0, wx.ALL, 8 )

		self.m_staticText38131 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Stop Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38131.Wrap( -1 )

		bSizer6031.Add( self.m_staticText38131, 0, wx.ALL, 8 )

		self.m_staticText381221 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Step Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText381221.Wrap( -1 )

		bSizer6031.Add( self.m_staticText381221, 0, wx.ALL, 8 )

		self.m_staticText3812111 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Slew Time (s)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3812111.Wrap( -1 )

		bSizer6031.Add( self.m_staticText3812111, 0, wx.ALL, 8 )


		bSizer7111.Add( bSizer6031, 0, wx.EXPAND, 5 )

		bSizer60111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_anode_gas_startvalue_text = wx.TextCtrl( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"7", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_startvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer60111.Add( self.m_slew_anode_gas_startvalue_text, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_stopvalue_text = wx.TextCtrl( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_stopvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer60111.Add( self.m_slew_anode_gas_stopvalue_text, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_value_text = wx.TextCtrl( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_value_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer60111.Add( self.m_slew_anode_gas_value_text, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_sweep_time_text = wx.TextCtrl( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_sweep_time_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer60111.Add( self.m_slew_anode_gas_sweep_time_text, 0, wx.ALL, 5 )


		bSizer7111.Add( bSizer60111, 0, wx.EXPAND, 5 )


		sbSizer4111.Add( bSizer7111, 1, wx.EXPAND, 5 )

		bSizer7211 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer7311 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer7311.SetMinSize( wx.Size( 100,-1 ) )
		self.m_staticText4611 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Step Num:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4611.Wrap( -1 )

		bSizer7311.Add( self.m_staticText4611, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_step_num_text = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_step_num_text.Wrap( -1 )

		self.m_slew_anode_gas_step_num_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer7311.Add( self.m_slew_anode_gas_step_num_text, 0, wx.ALL, 5 )


		bSizer7211.Add( bSizer7311, 0, wx.EXPAND, 5 )

		bSizer7721 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText4421 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Delay Steps:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4421.Wrap( -1 )

		bSizer7721.Add( self.m_staticText4421, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_delay_steps_text = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_delay_steps_text.Wrap( -1 )

		self.m_slew_anode_gas_delay_steps_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer7721.Add( self.m_slew_anode_gas_delay_steps_text, 0, wx.ALL, 5 )


		bSizer7211.Add( bSizer7721, 0, wx.EXPAND, 5 )

		bSizer77121 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText44121 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Current Step:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText44121.Wrap( -1 )

		bSizer77121.Add( self.m_staticText44121, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_current_step = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_current_step.Wrap( -1 )

		self.m_slew_anode_gas_current_step.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_anode_gas_current_step.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer77121.Add( self.m_slew_anode_gas_current_step, 0, wx.ALL, 5 )


		bSizer7211.Add( bSizer77121, 0, wx.EXPAND, 5 )

		bSizer771111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText441111 = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Current Value:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText441111.Wrap( -1 )

		bSizer771111.Add( self.m_staticText441111, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_current_value = wx.StaticText( sbSizer4111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_anode_gas_current_value.Wrap( -1 )

		self.m_slew_anode_gas_current_value.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_anode_gas_current_value.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer771111.Add( self.m_slew_anode_gas_current_value, 0, wx.ALL, 5 )


		bSizer7211.Add( bSizer771111, 0, wx.EXPAND, 5 )


		sbSizer4111.Add( bSizer7211, 0, wx.EXPAND, 5 )

		bSizer60211 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_anode_gas_start_sweep_btn = wx.Button( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Start Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer60211.Add( self.m_slew_anode_gas_start_sweep_btn, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_stop_sweep_btn = wx.Button( sbSizer4111.GetStaticBox(), wx.ID_ANY, u"Stop Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer60211.Add( self.m_slew_anode_gas_stop_sweep_btn, 0, wx.ALL, 5 )


		sbSizer4111.Add( bSizer60211, 0, wx.EXPAND, 5 )


		sbSizer162.Add( sbSizer4111, 0, wx.EXPAND, 5 )

		sbSizer411111 = wx.StaticBoxSizer( wx.StaticBox( sbSizer162.GetStaticBox(), wx.ID_ANY, u"Magnet Current" ), wx.HORIZONTAL )

		bSizer711111 = wx.BoxSizer( wx.VERTICAL )

		bSizer603111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText38111111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Start Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38111111.Wrap( -1 )

		bSizer603111.Add( self.m_staticText38111111, 0, wx.ALL, 8 )

		self.m_staticText3813111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Stop Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3813111.Wrap( -1 )

		bSizer603111.Add( self.m_staticText3813111, 0, wx.ALL, 8 )

		self.m_staticText38122111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Step Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38122111.Wrap( -1 )

		bSizer603111.Add( self.m_staticText38122111, 0, wx.ALL, 8 )

		self.m_staticText381211111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Slew Time (s)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText381211111.Wrap( -1 )

		bSizer603111.Add( self.m_staticText381211111, 0, wx.ALL, 8 )


		bSizer711111.Add( bSizer603111, 0, wx.EXPAND, 5 )

		bSizer6011111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_magnet_current_startvalue_text = wx.TextCtrl( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"3", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_startvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011111.Add( self.m_slew_magnet_current_startvalue_text, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_stopvalue_text = wx.TextCtrl( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"4", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_stopvalue_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011111.Add( self.m_slew_magnet_current_stopvalue_text, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_value_text = wx.TextCtrl( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_value_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011111.Add( self.m_slew_magnet_current_value_text, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_sweep_time_text = wx.TextCtrl( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_sweep_time_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer6011111.Add( self.m_slew_magnet_current_sweep_time_text, 0, wx.ALL, 5 )


		bSizer711111.Add( bSizer6011111, 0, wx.EXPAND, 5 )


		sbSizer411111.Add( bSizer711111, 1, wx.EXPAND, 5 )

		bSizer721111 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer731111 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer731111.SetMinSize( wx.Size( 100,-1 ) )
		self.m_staticText461111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Step Num:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText461111.Wrap( -1 )

		bSizer731111.Add( self.m_staticText461111, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_step_num_text = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_step_num_text.Wrap( -1 )

		self.m_slew_magnet_current_step_num_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer731111.Add( self.m_slew_magnet_current_step_num_text, 0, wx.ALL, 5 )


		bSizer721111.Add( bSizer731111, 0, wx.EXPAND, 5 )

		bSizer772111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText442111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Delay Steps:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText442111.Wrap( -1 )

		bSizer772111.Add( self.m_staticText442111, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_delay_steps_text = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_delay_steps_text.Wrap( -1 )

		self.m_slew_magnet_current_delay_steps_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer772111.Add( self.m_slew_magnet_current_delay_steps_text, 0, wx.ALL, 5 )


		bSizer721111.Add( bSizer772111, 0, wx.EXPAND, 5 )

		bSizer7712111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText4412111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Current Step:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4412111.Wrap( -1 )

		bSizer7712111.Add( self.m_staticText4412111, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_current_step = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_current_step.Wrap( -1 )

		self.m_slew_magnet_current_current_step.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_magnet_current_current_step.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer7712111.Add( self.m_slew_magnet_current_current_step, 0, wx.ALL, 5 )


		bSizer721111.Add( bSizer7712111, 0, wx.EXPAND, 5 )

		bSizer77111111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText44111111 = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Current Value:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText44111111.Wrap( -1 )

		bSizer77111111.Add( self.m_staticText44111111, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_current_value = wx.StaticText( sbSizer411111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_magnet_current_current_value.Wrap( -1 )

		self.m_slew_magnet_current_current_value.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_magnet_current_current_value.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer77111111.Add( self.m_slew_magnet_current_current_value, 0, wx.ALL, 5 )


		bSizer721111.Add( bSizer77111111, 0, wx.EXPAND, 5 )


		sbSizer411111.Add( bSizer721111, 0, wx.EXPAND, 5 )

		bSizer6021111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_magnet_current_start_sweep_btn = wx.Button( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Start Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6021111.Add( self.m_slew_magnet_current_start_sweep_btn, 0, wx.ALL, 5 )

		self.m_slew_magnet_current_stop_sweep_btn = wx.Button( sbSizer411111.GetStaticBox(), wx.ID_ANY, u"Stop Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer6021111.Add( self.m_slew_magnet_current_stop_sweep_btn, 0, wx.ALL, 5 )


		sbSizer411111.Add( bSizer6021111, 0, wx.EXPAND, 5 )


		sbSizer162.Add( sbSizer411111, 0, wx.EXPAND, 5 )

		sbSizer41111 = wx.StaticBoxSizer( wx.StaticBox( sbSizer162.GetStaticBox(), wx.ID_ANY, u"Cathode Low Flow" ), wx.HORIZONTAL )

		bSizer71111 = wx.BoxSizer( wx.VERTICAL )

		bSizer60311 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText3811111 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Start Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3811111.Wrap( -1 )

		bSizer60311.Add( self.m_staticText3811111, 0, wx.ALL, 8 )

		self.m_staticText381311 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Stop Value", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText381311.Wrap( -1 )

		bSizer60311.Add( self.m_staticText381311, 0, wx.ALL, 8 )

		self.m_staticText3812211 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Step Size", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3812211.Wrap( -1 )

		bSizer60311.Add( self.m_staticText3812211, 0, wx.ALL, 8 )

		self.m_staticText38121111 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Slew Time (s)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38121111.Wrap( -1 )

		bSizer60311.Add( self.m_staticText38121111, 0, wx.ALL, 8 )


		bSizer71111.Add( bSizer60311, 0, wx.EXPAND, 5 )

		bSizer601111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_cathode_low_flow_start_text = wx.TextCtrl( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"7", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_start_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601111.Add( self.m_slew_cathode_low_flow_start_text, 0, wx.ALL, 5 )

		self.m_slew_cathode_low_flow_stop_text = wx.TextCtrl( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_stop_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601111.Add( self.m_slew_cathode_low_flow_stop_text, 0, wx.ALL, 5 )

		self.m_slew_cathode_low_flow_step_size_text = wx.TextCtrl( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_step_size_text.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601111.Add( self.m_slew_cathode_low_flow_step_size_text, 0, wx.ALL, 5 )

		self.m_slew_cathode_low_flow_slew_time = wx.TextCtrl( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"10", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_slew_time.SetMinSize( wx.Size( 60,-1 ) )

		bSizer601111.Add( self.m_slew_cathode_low_flow_slew_time, 0, wx.ALL, 5 )


		bSizer71111.Add( bSizer601111, 0, wx.EXPAND, 5 )


		sbSizer41111.Add( bSizer71111, 1, wx.EXPAND, 5 )

		bSizer72111 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer73111 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer73111.SetMinSize( wx.Size( 100,-1 ) )
		self.m_staticText46111 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Step Num:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText46111.Wrap( -1 )

		bSizer73111.Add( self.m_staticText46111, 0, wx.ALL, 5 )

		self.m_slew_cathode_low_flow_step_num_text = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_step_num_text.Wrap( -1 )

		self.m_slew_cathode_low_flow_step_num_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer73111.Add( self.m_slew_cathode_low_flow_step_num_text, 0, wx.ALL, 5 )


		bSizer72111.Add( bSizer73111, 0, wx.EXPAND, 5 )

		bSizer77211 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText44211 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Delay Steps:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText44211.Wrap( -1 )

		bSizer77211.Add( self.m_staticText44211, 0, wx.ALL, 5 )

		self.m_slew_cathode_low_flow_delay_step_text = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_delay_step_text.Wrap( -1 )

		self.m_slew_cathode_low_flow_delay_step_text.SetMinSize( wx.Size( 25,-1 ) )

		bSizer77211.Add( self.m_slew_cathode_low_flow_delay_step_text, 0, wx.ALL, 5 )


		bSizer72111.Add( bSizer77211, 0, wx.EXPAND, 5 )

		bSizer771211 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText441211 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Current Step:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText441211.Wrap( -1 )

		bSizer771211.Add( self.m_staticText441211, 0, wx.ALL, 5 )

		self.m_slew_cathode_low_flow_current_step_text = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_current_step_text.Wrap( -1 )

		self.m_slew_cathode_low_flow_current_step_text.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_cathode_low_flow_current_step_text.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer771211.Add( self.m_slew_cathode_low_flow_current_step_text, 0, wx.ALL, 5 )


		bSizer72111.Add( bSizer771211, 0, wx.EXPAND, 5 )

		bSizer7711111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText4411111 = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Current Value:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4411111.Wrap( -1 )

		bSizer7711111.Add( self.m_staticText4411111, 0, wx.ALL, 5 )

		self.m_slew_cathode_low_flow_current_value = wx.StaticText( sbSizer41111.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_slew_cathode_low_flow_current_value.Wrap( -1 )

		self.m_slew_cathode_low_flow_current_value.SetMinSize( wx.Size( 50,-1 ) )
		self.m_slew_cathode_low_flow_current_value.SetMaxSize( wx.Size( 100,-1 ) )

		bSizer7711111.Add( self.m_slew_cathode_low_flow_current_value, 0, wx.ALL, 5 )


		bSizer72111.Add( bSizer7711111, 0, wx.EXPAND, 5 )


		sbSizer41111.Add( bSizer72111, 0, wx.EXPAND, 5 )

		bSizer602111 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_slew_cathode_low_flow_start_btn = wx.Button( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Start Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer602111.Add( self.m_slew_cathode_low_flow_start_btn, 0, wx.ALL, 5 )

		self.m_slew_anode_gas_stop_sweep_btn = wx.Button( sbSizer41111.GetStaticBox(), wx.ID_ANY, u"Stop Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer602111.Add( self.m_slew_anode_gas_stop_sweep_btn, 0, wx.ALL, 5 )


		sbSizer41111.Add( bSizer602111, 0, wx.EXPAND, 5 )


		sbSizer162.Add( sbSizer41111, 1, wx.EXPAND, 5 )

		self.m_slew_anode_gas_both_sweep_btn = wx.Button( sbSizer162.GetStaticBox(), wx.ID_ANY, u"AF/LF Start Slew", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer162.Add( self.m_slew_anode_gas_both_sweep_btn, 0, wx.ALL, 5 )


		bSizer462.Add( sbSizer162, 1, wx.EXPAND, 5 )


		self.m_throttle_control_tab.SetSizer( bSizer462 )
		self.m_throttle_control_tab.Layout()
		bSizer462.Fit( self.m_throttle_control_tab )
		self.m_auinotebook1.AddPage( self.m_throttle_control_tab, u"Throttle Control", False, wx.NullBitmap )
		self.m_logpanel = wx.Panel( self.m_auinotebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer46 = wx.BoxSizer( wx.VERTICAL )

		self.m_logAutoScroll = wx.CheckBox( self.m_logpanel, wx.ID_ANY, u"Scroll To Bottom", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_logAutoScroll.SetValue(True)
		bSizer46.Add( self.m_logAutoScroll, 0, wx.ALIGN_LEFT|wx.ALL, 5 )

		sbSizer16 = wx.StaticBoxSizer( wx.StaticBox( self.m_logpanel, wx.ID_ANY, u"Log" ), wx.VERTICAL )

		self.m_logText = wx.richtext.RichTextCtrl( sbSizer16.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		sbSizer16.Add( self.m_logText, 1, wx.EXPAND |wx.ALL, 0 )

		self.m_showLogFiles = wx.ToggleButton( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Log Files", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer16.Add( self.m_showLogFiles, 0, wx.ALL, 5 )


		bSizer46.Add( sbSizer16, 1, wx.EXPAND, 5 )


		self.m_logpanel.SetSizer( bSizer46 )
		self.m_logpanel.Layout()
		bSizer46.Fit( self.m_logpanel )
		self.m_auinotebook1.AddPage( self.m_logpanel, u"Log", False, wx.NullBitmap )
		self.m_tracemessage_tab = wx.Panel( self.m_auinotebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer43 = wx.BoxSizer( wx.VERTICAL )

		bSizer44 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText33 = wx.StaticText( self.m_tracemessage_tab, wx.ID_ANY, u"Trace Flag", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText33.Wrap( -1 )

		bSizer44.Add( self.m_staticText33, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_textTraceFlag = wx.TextCtrl( self.m_tracemessage_tab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer44.Add( self.m_textTraceFlag, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_setTraceFlagButton = wx.Button( self.m_tracemessage_tab, wx.ID_ANY, u"Set Trace Flag", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer44.Add( self.m_setTraceFlagButton, 0, wx.ALL, 5 )

		self.m_traceAutoScroll = wx.CheckBox( self.m_tracemessage_tab, wx.ID_ANY, u"Scroll To Bottom", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_traceAutoScroll.SetValue(True)
		bSizer44.Add( self.m_traceAutoScroll, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_enableTraceCheckbox = wx.CheckBox( self.m_tracemessage_tab, wx.ID_ANY, u"Enable", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer44.Add( self.m_enableTraceCheckbox, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_staticText331 = wx.StaticText( self.m_tracemessage_tab, wx.ID_ANY, u"Trace Delay Time (MS)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText331.Wrap( -1 )

		bSizer44.Add( self.m_staticText331, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_traceDelaySpinCntrl = wx.SpinCtrl( self.m_tracemessage_tab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 5000, 10 )
		bSizer44.Add( self.m_traceDelaySpinCntrl, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_clearTextButton = wx.Button( self.m_tracemessage_tab, wx.ID_ANY, u"Clear Msgs", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer44.Add( self.m_clearTextButton, 0, wx.ALL, 5 )


		bSizer43.Add( bSizer44, 0, wx.EXPAND, 5 )

		self.m_traceMsgLogText = wx.richtext.RichTextCtrl( self.m_tracemessage_tab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		bSizer43.Add( self.m_traceMsgLogText, 1, wx.EXPAND |wx.ALL, 5 )


		self.m_tracemessage_tab.SetSizer( bSizer43 )
		self.m_tracemessage_tab.Layout()
		bSizer43.Fit( self.m_tracemessage_tab )
		self.m_auinotebook1.AddPage( self.m_tracemessage_tab, u"Trace Messages", True, wx.NullBitmap )

		sb.Add( self.m_auinotebook1, 10, wx.EXPAND |wx.ALL, 5 )


		bSerialSizer.Add( sb, 1, wx.EXPAND, 5 )

		self.m_emergencystop_button = wx.Button( self, wx.ID_ANY, u"EMERGENCY STOP", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_emergencystop_button.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.m_emergencystop_button.SetBackgroundColour( wx.Colour( 255, 0, 0 ) )
		self.m_emergencystop_button.SetMinSize( wx.Size( 400,-1 ) )

		bSerialSizer.Add( self.m_emergencystop_button, 0, wx.ALIGN_CENTER|wx.ALL|wx.RIGHT, 0 )


		self.SetSizer( bSerialSizer )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class HSIExcelFrame
###########################################################################

class HSIExcelFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1200,768 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 1200,768 ), wx.DefaultSize )

		bSizer80 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_hsiExcelGrid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.m_hsiExcelGrid.CreateGrid( 28, 10 )
		self.m_hsiExcelGrid.EnableEditing( True )
		self.m_hsiExcelGrid.EnableGridLines( True )
		self.m_hsiExcelGrid.EnableDragGridSize( False )
		self.m_hsiExcelGrid.SetMargins( 0, 0 )

		# Columns
		self.m_hsiExcelGrid.SetColSize( 0, 100 )
		self.m_hsiExcelGrid.SetColSize( 1, 100 )
		self.m_hsiExcelGrid.SetColSize( 2, 100 )
		self.m_hsiExcelGrid.SetColSize( 3, 100 )
		self.m_hsiExcelGrid.SetColSize( 4, 100 )
		self.m_hsiExcelGrid.SetColSize( 5, 100 )
		self.m_hsiExcelGrid.SetColSize( 6, 100 )
		self.m_hsiExcelGrid.SetColSize( 7, 100 )
		self.m_hsiExcelGrid.SetColSize( 8, 100 )
		self.m_hsiExcelGrid.SetColSize( 9, 100 )
		self.m_hsiExcelGrid.EnableDragColMove( False )
		self.m_hsiExcelGrid.EnableDragColSize( True )
		self.m_hsiExcelGrid.SetColLabelSize( 30 )
		self.m_hsiExcelGrid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.m_hsiExcelGrid.AutoSizeRows()
		self.m_hsiExcelGrid.EnableDragRowSize( True )
		self.m_hsiExcelGrid.SetRowLabelSize( 150 )
		self.m_hsiExcelGrid.SetRowLabelAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTER )

		# Label Appearance

		# Cell Defaults
		self.m_hsiExcelGrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer80.Add( self.m_hsiExcelGrid, 0, wx.ALL, 5 )


		self.SetSizer( bSizer80 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class VerisonInfoFrame
###########################################################################

class VerisonInfoFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1106,236 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		sbSizer30 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Version Info" ), wx.HORIZONTAL )

		self.m_ver_grid = wx.grid.Grid( sbSizer30.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.m_ver_grid.CreateGrid( 7, 9 )
		self.m_ver_grid.EnableEditing( True )
		self.m_ver_grid.EnableGridLines( True )
		self.m_ver_grid.EnableDragGridSize( False )
		self.m_ver_grid.SetMargins( 0, 0 )

		# Columns
		self.m_ver_grid.SetColSize( 0, 206 )
		self.m_ver_grid.SetColSize( 1, 80 )
		self.m_ver_grid.SetColSize( 2, 80 )
		self.m_ver_grid.SetColSize( 3, 80 )
		self.m_ver_grid.SetColSize( 4, 80 )
		self.m_ver_grid.SetColSize( 5, 80 )
		self.m_ver_grid.SetColSize( 6, 80 )
		self.m_ver_grid.SetColSize( 7, 80 )
		self.m_ver_grid.SetColSize( 8, 80 )
		self.m_ver_grid.EnableDragColMove( False )
		self.m_ver_grid.EnableDragColSize( True )
		self.m_ver_grid.SetColLabelSize( 30 )
		self.m_ver_grid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.m_ver_grid.EnableDragRowSize( True )
		self.m_ver_grid.SetRowLabelSize( 90 )
		self.m_ver_grid.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Label Appearance

		# Cell Defaults
		self.m_ver_grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		sbSizer30.Add( self.m_ver_grid, 1, wx.ALL, 5 )

		self.m_ver_info_query_btn = wx.Button( sbSizer30.GetStaticBox(), wx.ID_ANY, u"Query", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer30.Add( self.m_ver_info_query_btn, 0, wx.ALL, 5 )


		self.SetSizer( sbSizer30 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


