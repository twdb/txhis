from xml.etree import cElementTree
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from cStringIO import StringIO
from urllib import urlencode
import urllib2
import time



centralRegUrl = 'http://lighthouse.tamucc.edu/ioosobsreg.xml'
#normalize the xml space part
def normalize(name):
    """
    small utility, just for normalize the XML name space formed as: {space}tag name
    input: an string of XML tag
    output: tuple formed as (uri,tag) (both uri,tag are string) 
    """
    if name[0] == "{":
        uri, tag = name[1:].split("}")
        return (uri,tag)
    else:
        return name


#this function gets the Registry XML file from the hardcoded URL
def getIterator(urlStr):
    """
    gets the Registry XML file as a string from and url with urlStr
    input value: an urlStr
    output value: an ElementTree iterator for output XML Tree
    assumption(weak): the output is in XML format
    """
    req = urllib2.Request(urlStr)
    response = urllib2.urlopen(req)
    registryXMLString = response.read()   
    root = cElementTree.parse(StringIO(registryXMLString))
    return root.getiterator()

#this function build a SitesInfo dictionary.
#Here SiteInfo dictionary structure:
#This is a python dictionary, in the form of:
#    { siteCode(numeric): (siteName, [a feature member list]}
def buildSiteInfo_siteDictionary(treeIter,siteInfo_site_dict):
    """
    input: an XML tree rootiterator, an result siteInfo_site_dictionary
    output: none
    """
    noFeaturedMember = 0
    for element in treeIter:
        if normalize(element.tag)[1] == "boundedBy":
            #get srs info by reading the attribute srsName from Envelope tag
            siteInfo_site_dict['srs'] = element[0].attrib['srsName']
        if normalize(element.tag)[1] == "featureMember":
            #element[0] is InstituteObPoints Node
            for child in element[0]:
                if normalize(child.tag)[1] == "platformName" and \
                          not siteInfo_site_dict.has_key(child.text.split(':')[0]):
                    #here put the value as a tuple, in the form of (elment node, site name)
                    #note: element node here is the "InstituteObPoints Node"
                    #reference xml file: http://lighthouse.tamucc.edu/ioosobsreg.xml
                    siteInfo_site_dict[child.text.split(':')[0]] = (child.text.split(':')[1],[element[0]])
                    break
                elif siteInfo_site_dict.has_key(child.text.split(':')[0]):
                    siteInfo_site_dict[child.text.split(':')[0]][1].append(element[0])
                    break
    #print siteInfo_site_dict
    #handle multiple series case
    for key in siteInfo_site_dict.keys():
        if key == "__modTime" or key == "srs":continue
        #a dictionary to keep timeSeries info
        paramSerieInfo = {}
        #print siteInfo_site_dict[key][1]
        for xmlNode in siteInfo_site_dict[key][1]:
            from datetime import datetime
            #this node have not been processed
            if xmlNode[2].text not in paramSerieInfo.keys():
                #format of key-value pair:
                #   key(the parameter name)  
                #   value( [(startDate,endDate),xmlNode])
                timeTuple = tuple(map(lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')if x else "", \
                                            (xmlNode[10].text,xmlNode[11].text)))
                paramSerieInfo[xmlNode[2].text]=[timeTuple,xmlNode]
            #this node have been processed, comparing its time
            #get the earliest startDate and the latest endDate
            else:
                OldTimeTuple = paramSerieInfo[xmlNode[2].text][0]
                NewTimeTuple = map(lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ')if x else "", \
                                     (xmlNode[10].text,xmlNode[11].text))
                #ajusted time info
                newTimeList = list(paramSerieInfo[xmlNode[2].text][0])
                #processing startDate
                if OldTimeTuple[0] == "" :
                    newTimeList[0] = NewTimeTuple[0]
                    paramSerieInfo[xmlNode[2].text][1][10].text = xmlNode[10].text
                elif NewTimeTuple[0] == "":
                    pass
                else:
                    if OldTimeTuple[0] > NewTimeTuple[0]:
                        newTimeList[0] =  NewTimeTuple[0]
                        paramSerieInfo[xmlNode[2].text][1][10].text = xmlNode[10].text
                #processing endDate
                if OldTimeTuple[1] == "" :
                    newTimeList[1] = NewTimeTuple[1]
                    paramSerieInfo[xmlNode[2].text][1][11].text = xmlNode[11].text
                elif NewTimeTuple[1] == "":
                    pass
                else:
                    if OldTimeTuple[1] < NewTimeTuple[1]:
                        newTimeList[1] =  NewTimeTuple[1]
                        paramSerieInfo[xmlNode[2].text][1][11].text = xmlNode[11].text
                paramSerieInfo[xmlNode[2].text][0]=tuple(newTimeList)
        #new XMLNode list
        newNodeList = [paramSerieInfo[i][1] for i in paramSerieInfo.keys()]
        siteInfo_site_dict[key] = (siteInfo_site_dict[key][0],newNodeList)
                                          
    #this is only for testing
    if __name__ == "__main__":
        print len(siteInfo_site_dict.keys())                        
        print siteInfo_site_dict["005"][1]
        for xmlNode in siteInfo_site_dict["005"][1]:
            print xmlNode[2].text
            
# get input parameters for CBI GetValues information
# Input: siteCode, variableCode, startingDate, endingDate
# output: an encoded URL string for constructing a GET HTTP request
def getCBIParamList(siteCode,variableCode,startDate,endDate):
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

# get the value response for a certain HTTP request
# input: an encoded URL string (for GET HTTP request
# output: a StringIO containing all the data.
def getCBIValues(urlendata):
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

# return the URL query string for a CBI site
# input: siteCode, variableCode, startingDate, endingDate
# output: the query URL string
def getCBIURLqueryString(siteCode,variableCode,startDate,endDate):
    query = getCBIParamList(siteCode,variableCode,startDate,endDate)
    return "?".join(["http://lighthouse.tamucc.edu/cgi-bin/pd.cgi",query])
  
#self_testing code
if __name__ == "__main__":
    treeIter = getIterator(centralRegUrl)
    buildSiteInfo_siteDictionary(treeIter,{})
    query = getCBIParamList("006","pwl","2004-05-28 00:00:00","2006-06-24 00:00:00")
    print getCBIValues(query).getvalue()

