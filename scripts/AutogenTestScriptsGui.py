# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

###########################################################################
## Class HSIExcelFrame
###########################################################################

class HSIExcelFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1059,680 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer80 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_hsiExcelGrid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.m_hsiExcelGrid.CreateGrid( 28, 10 )
		self.m_hsiExcelGrid.EnableEditing( True )
		self.m_hsiExcelGrid.EnableGridLines( True )
		self.m_hsiExcelGrid.EnableDragGridSize( False )
		self.m_hsiExcelGrid.SetMargins( 0, 0 )

		# Columns
		self.m_hsiExcelGrid.EnableDragColMove( False )
		self.m_hsiExcelGrid.EnableDragColSize( False )
		self.m_hsiExcelGrid.SetColLabelSize( 30 )
		self.m_hsiExcelGrid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.m_hsiExcelGrid.AutoSizeRows()
		self.m_hsiExcelGrid.EnableDragRowSize( True )
		self.m_hsiExcelGrid.SetRowLabelSize( 100 )
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


