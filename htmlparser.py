#!/usr/bin/python
from basicdisplayer import BasicDisplayer

class HTMLParser():
	def __init__(self, displayer):
		""" Init Parser  """
		if displayer:
			self.displayer = displayer
		else:
			print "displayer is none."
			self.displayer = BasicDisplayer()

	def start(self, tag, attrs):
		try:
			self.displayer.displaybegin(tag, attrs)
		except Exception as e:
			print e		

	def end(self, tag):
		try:
			self.displayer.displayend(tag)
		except Exception as e:
			print e
		
	def data(self, data):
		try:
			self.displayer.displaydata(data, 0)
		except Exception as e:
			print e
		
	def comment(self, data):
		try:
			self.displayer.displaydata(data, 1)
		except Exception as e:
			print e
			
	def close(self):
		pass

if __name__ == '__main__':
	parser = HTMLParser()
	parser.feed()