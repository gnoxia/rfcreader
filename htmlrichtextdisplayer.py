#!/usr/bin/python

import wx
import wx.richtext as rt
from basicdisplayer import BasicDisplayer

class DocEntryElement:
	data = ""
	lastPosition = 0
	begin = False
	titleType = ""

class HTMLRichTextDisplayer(BasicDisplayer):
	def __init__(self, rc):
		if rc:
			self.rc = rc
			self.attrs = []
			self.tag = False
		self.urlContinure = 0
		self.docEntryList = []
		self.docEntryElement = DocEntryElement()
		self.docEntryElement.data = ""
		self.docEntryElement.lastPosition = 0
		self.docEntryElement.begin = False
		self.docEntryElement.titleType = ""
		self.dictContent = {}

	def displaybegin(self, tag, attrs):
		if tag == 'link' or tag == 'meta' or tag == 'style' or tag == 'script':
			self.tag = True
			self.attrs = []
		else:
			self.tag = tag
			self.attrs.append(attrs)
			

	def displayend(self, tag):
		for attr in self.attrs:
			if 'href' in attr:
				self.rc.EndURL()
				self.rc.EndStyle()
				self.rc.Bind(wx.EVT_TEXT_URL, self.OnURL)
				self.urlContinure = 0
				break
		if tag == 'span' and self.docEntryElement.begin == True:
			self.docEntryList.append({self.docEntryElement.titleType:[self.docEntryElement.lastPosition, self.docEntryElement.data]})
			self.docEntryElement.data = ""
			self.docEntryElement.lastPosition = 0
			self.docEntryElement.begin = False
			self.docEntryElement.titleType = ""
		self.attrs = []
		self.tag = False

	def displaydata(self, data, type):
		selfLinkUrl = ""
		if self.tag == True or type != 0:
			return
		for attr in self.attrs:
			if 'href' in attr and self.urlContinure == 0:
				style = rt.RichTextAttr()
				style.SetFontUnderlined(True)
				style.SetTextColour(wx.BLUE)
				self.rc.BeginStyle(style)
				self.rc.BeginURL(attr['href'])
				# Add to dict for content search.
				selfLinkUrl = attr['href']
				self.urlContinure = 1
			if 'class' in attr and attr['class'][0] == 'h':
				self.docEntryElement.lastPosition = self.rc.GetLastPosition()
				self.docEntryElement.begin = True
				self.docEntryElement.titleType = attr['class']
				self.rc.SetInsertionPoint(self.rc.GetLastPosition())
		
		if self.docEntryElement.begin:
			self.docEntryElement.data += data + " "
			self.dictContent[selfLinkUrl] = self.rc.GetLastPosition()
		self.rc.WriteText(data)
		
	def OnURL(self, event):
		key = event.GetString()
		print key
		if key in self.dictContent:
			self.rc.ShowPosition(self.rc.GetLastPosition())
			self.rc.ShowPosition(self.dictContent.get(key))
	def SetPosition(self, pos):
		self.rc.ShowPosition(self.rc.GetLastPosition())
		self.rc.ShowPosition(pos)
		
		

