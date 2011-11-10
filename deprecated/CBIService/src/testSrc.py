'''
Created on Jan 31, 2011

@author: CTtan
'''
import cStringIO
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time,urllib2
from StringIO import StringIO
from urllib import urlencode

def getTCOONParamList(siteCode,variableCode,startDate,endDate):
    var_code_maping = {"wtp":"water_temperature",
                         "atp":"air_temperature",
                         "bpr":"air_pressure",
                         # water level is not working
                         #"pwl":"water_level",
                         "wsd":"wind_speed",
                         #"do":"dissolved_oxygen",
                         "sal":"salinity",
                         ## more to be continued
                         }
    data = {}
    data["offering"] = siteCode
    data['request']= "GetObservation"
    data["observedproperty"] = var_code_maping[variableCode]
    data["eventtime"] = "/".join([time.strftime("%Y-%m-%dT%H:%M:%SZ",time.strptime(startDate,"%Y-%m-%d %H:%M:%S")),
                             time.strftime("%Y-%m-%dT%H:%M:%SZ",time.strptime(endDate,"%Y-%m-%d %H:%M:%S"))])
    return urlencode(data)

def getTCOONValues(urlendata):
    fullurl = "?".join(["http://lighthouse.tamucc.edu/sos",urlendata])
    req = urllib2.Request(fullurl)
    response = urllib2.urlopen(req)
    output = StringIO(response.read())
    return output

class SOSHandler(ContentHandler):
    """
    A handler to deal with SOS RPC return call in XML
    """
    inValueCount = 0
    inValues = 0
    findValueCount = 0
    #findValuesString = 0
    recordsCount = ""
    valuesString = ""
    def startElement(self, name, attrs):
        if name == "swe:Count":
            self.inValueCount = 1
        elif name == "swe:values":
            self.inValues = 1
            #findValuesString = 1
    
    def characters(self, characters):
        if self.inValueCount:
            self.recordsCount += characters.strip()
        elif self.inValues:
            self.valuesString += characters.strip()
        
    def endElement(self, name):
        if name == "swe:Count":
            self.inValueCount = 0
        if name == "swe:values":
            self.inValues = 0          

def parseSOS(stream):
    saxparser = make_parser()
    ctHandler = SOSHandler()
    saxparser.setContentHandler(ctHandler)
    saxparser.parse(stream)
    return (ctHandler.recordsCount, ctHandler.valuesString)


if __name__ == "__main__":
    respons_rtr = getTCOONValues(getTCOONParamList('005','wtp','2011-1-20 00:00:00','2011-1-28 00:00:00'))
    #print respons_rtr.getvalue()
    parseResult = parseSOS(respons_rtr)
    print "hello..."
    print "1==>",parseResult[0]
    for row in parseResult[1].split():
        print row.split(',')[5]
    #print "2==>",parseResult[1]