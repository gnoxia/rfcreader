#!/usr/bin/python
import urllib2

class DataConnector:
    """ Maintains data source. """
    def __init__(self):
        self._defURLPrefix = "http://tools.ietf.org/html/rfc"

    def Read(self, fileNameSuffix):
        """ Read data back to caller """
        """ First try the local path, then internet """
        try:
            with open(fileNameSuffix) as f:
                print "Read from file"
                return f.read()
        except IOError:
            print "Open URL", "http://tools.ietf.org/html/rfc" + fileNameSuffix
            try:
                urlfile =  urllib2.urlopen("http://tools.ietf.org/html/rfc" + fileNameSuffix)
                return urlfile.read()
            except urllib2.URLError as e:
                print e.reason
            return 
    def SaveToFile(self, fileName, content):
        try:
            with open(fileName, 'a') as f:
                f.write(content)
        except IOError as e:
            print e