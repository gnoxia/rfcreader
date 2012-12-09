#!/usr/bin/python

from HTMLParser import HTMLParser as HP
from basicdisplayer import BasicDisplayer

class HTMLParser(HP):
	def __init__(self, displayer):
		HP.__init__(self)
		""" Init Parser  """
		if displayer:
			self.displayer = displayer
		else:
			print "displayer is none."
			self.displayer = BasicDisplayer()

	def handle_starttag(self, tag, attrs):
		self.displayer.displaybegin(tag, attrs)
		#print "Start tag:", tag
		#for attr in attrs:
		#	print "     attr:", attr

	def handle_endtag(self, tag):
		self.displayer.displayend(tag)
		#print "End tag  :", tag
	def handle_data(self, data):
		self.displayer.displaydata(data, 0)
		#print "Data     :", data
	def handle_comment(self, data):
		self.displayer.displaydata(data, 1)
		#print "Comment  :", data
	def handle_entityref(self, name):
		self.displayer.displaydata(name, 2)
		#c = unichr(name2codepoint[name])
		#print "Named ent:", c
	def handle_charref(self, name):
		self.displayer.displaydata(name,3)
		if name.startswith('x'):
			c = unichr(int(name[1:], 16))
		else:
			c = unichr(int(name))
		#print "Num ent  :", c
	def handle_decl(self, data):
		self.displayer.displaydata(data, 4)
		#print "Decl     :", data

if __name__ == '__main__':
	parser = HTMLParser()
	parser.feed()