#!/usr/bin/python

class BasicDisplayer:
	def __init__(self):
		pass
	def displaybegin(self, tag, attrs):
		""" Do nothing """
		print "begin"

	def displayend(self, tag):
		""" Do nothing """
		print "end"
	def displaydata(self, data, type):
		""" Do nothing """
		print "data"