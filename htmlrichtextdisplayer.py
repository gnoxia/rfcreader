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
	"""
	This displayer works a little like render, the different is the render works while
	the html is parsing. So here only a little html and css will be recognized and utilized 
	in this displayer.
	"""
	def __init__(self, rc, css):
		if rc:
			self.rc = rc
			self.attrs = {}
			self.tag = False
		self.css = css
		self.urlContinure = 0
		# docEntryList record all headers in html.
		self.docEntryList = []
		self.docEntryElement = DocEntryElement()
		self.docEntryElement.data = ""
		self.docEntryElement.lastPosition = 0
		self.docEntryElement.begin = False
		self.docEntryElement.titleType = ""
		# dictContent record all self or outer links.
		self.dictContent = {}

	def displaybegin(self, tag, attrs):
		if tag == 'link' or tag == 'meta' or tag == 'style' or tag == 'script':
			self.tag = True
			self.attrs = {}
		else:
			self.tag = tag
			self.attrs[tag] = attrs
			

	def displayend(self, tag):
		if tag == 'a' and 'a' in self.attrs and 'href' in self.attrs['a']:
			# Add handler for an url
			self.rc.Bind(wx.EVT_TEXT_URL, self.OnURL)
			self.urlContinure = 0
	
		if tag == 'span' and self.docEntryElement.begin == True:
			# Record catalog and reset catalog flags.
			self.docEntryList.append({self.docEntryElement.titleType:[self.docEntryElement.lastPosition, self.docEntryElement.data]})
			self.docEntryElement.data = ""
			self.docEntryElement.lastPosition = 0
			self.docEntryElement.begin = False
			self.docEntryElement.titleType = ""
		del self.attrs[tag]
		self.tag = False

	def displaydata(self, data, type):
		selfLinkUrl = ""
		size = ""
		weight = ""
		family = ""
		style = rt.RichTextAttr()
		if self.tag == True or type != 0:
			# Do nothing for these tags.
			return
		if 'a' in self.attrs and 'href' in self.attrs['a'] and self.urlContinure == 0:								
			# Add to dict for content search.
			selfLinkUrl = self.attrs['a']['href']			
			self.urlContinure = 1
			if 'span' in self.attrs and 'class' in self.attrs['span'] and self.attrs['span']['class'][0] == 'h':
				# Select headers from html and record them.
				self.docEntryElement.lastPosition = self.rc.GetLastPosition()
				self.docEntryElement.begin = True
				self.docEntryElement.titleType = self.attrs['span']['class']
				self.rc.SetInsertionPoint(self.rc.GetLastPosition())

		if 'span' in self.attrs and 'class' in self.attrs['span']:			
			import re
			l = re.split(' ', self.attrs['span']['class'])
			for selector in l:
				if selector in self.css:					
					for decls in self.css[selector]:					
						if 'font-size' in decls:
							size = decls['font-size']
						if 'font-weight' in decls:
							weight = decls['font-weight']
						if 'font-family' in decls:
							family = decls['font-family']						
	
		if self.docEntryElement.begin:
			self.docEntryElement.data += data + " "
			self.dictContent[selfLinkUrl] = self.rc.GetLastPosition()
	
		if family != "":
			# TODO: parse family string.
			style.SetFontFaceName(family)
		if size != "":
			# TODO: parse font size.
			if size == '1em':
				pass#style.SetFontSize(wx.FONTSIZE_MEDIUM)
		if weight != "":
			# TODO: parse font weight.
			if weight == 'bold':
				style.SetFontWeight(wx.FONTWEIGHT_BOLD)
			elif weight == 'light':
				style.SetFontWeight(wx.FONTWEIGHT_LIGHT)
		else:
			# Reset font weight back to normal.
			style.SetFontWeight(wx.FONTWEIGHT_NORMAL)		
		
		if selfLinkUrl != "":
			# Set url style				
			style.SetFontUnderlined(True)
			style.SetTextColour(wx.BLUE)
		else:
			# Reset url style.
			style.SetFontUnderlined(False)
			style.SetTextColour(wx.BLACK)

		
		self.rc.BeginStyle(style)
		
		if selfLinkUrl != "":
			self.rc.BeginURL(selfLinkUrl)

		self.rc.WriteText(data)

		if selfLinkUrl != "":
			self.rc.EndURL()

		self.rc.EndStyle()

	def OnURL(self, event):
		""" 
		Seek the url if it is in current html.
		Parameter event contains the url name, which
		is needed by searching process.
		"""
		key = event.GetString()
		if key in self.dictContent:
			# In order to keep found header showing at top
			# here first seek to the end of file then seek
			# back to the header
			self.rc.ShowPosition(self.rc.GetLastPosition())
			self.rc.ShowPosition(self.dictContent.get(key))
	
	def SetPosition(self, pos):
		self.rc.ShowPosition(self.rc.GetLastPosition())
		self.rc.ShowPosition(pos)
		
		

