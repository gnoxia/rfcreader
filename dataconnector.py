#!/usr/bin/python
import urllib2
import os

class DataConnector:
    """ Maintains data source. """
    def __init__(self):
        self._defURLPrefix = "http://tools.ietf.org/html/rfc"
        self._defDir = "rfcs/"
    def Read(self, fileNameSuffix):
        """ Read data back to caller """
        """ First try the local path, then internet """
        try:
            with open(self._defDir + fileNameSuffix) as f:
                print "Read data from file: " + self._defDir + fileNameSuffix
                return f.read()
        except IOError as e:
            print e
            print "Retry by openning URL", "http://tools.ietf.org/html/rfc" + fileNameSuffix
            try:
                urlfile =  urllib2.urlopen("http://tools.ietf.org/html/rfc" + fileNameSuffix)
                return urlfile.read()
            except urllib2.URLError as e:
                print e.reason
            return 
    def SaveToFile(self, fileName, content):
        if not os.path.isdir(self._defDir):
            os.makedirs(self._defDir)
        try:
            with open(self._defDir + fileName, 'a') as f:
                f.write(content)
        except IOError as e:
            print e