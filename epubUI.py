#!/usr/bin/python2.7 -tt

try:
	import wx
except ImportError:
	print "You do not appear to have wxpython installed.\n"
	print "Without wxpython, this program cannot run.\n"
	print "You can download wxpython at: http://www.wxpython.org/download.php#stable \n"
	sys.exit()

import epubFrame

epubApp = wx.App(False)

options = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
frame = wx.Frame(None, style=options)
f = epubFrame.epubFrame(frame)

epubApp.MainLoop()