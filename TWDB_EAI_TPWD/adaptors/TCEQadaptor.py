import sys
sys.path.append("..")
sys.path.append('../pipes')
sys.path.append('../sources')
sys.path.append('../sinks')
from sources import HTTPSource
from sinks import SQLSink_forTCEQ
#from sinks import SQLSink
from xml.etree.ElementTree import *
from formatter import AbstractFormatter , NullFormatter
from htmllib import HTMLParser
import utility_EAI.twdbEaiLog as reticLog
from utility_EAI.twdbEaiUtil import get_conf_attr
import StringIO,urllib2


EVENT = "1"
RESULT = "2"
#This are classes for recoverying from failure spot (year, basinID)
class yearString(str):
    def __init__(self,stringIns):
        self.stringIns = stringIns
    def __lt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        if self.stringIns[0] == '/':
            LString = self.stringIns[1:]
        if other.stringIns[0] == '/':
            RString = other.stringIns[1:]
        return int(LString) < int(RString)
    def __gt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        if self.stringIns[0] == '/':
            LString = self.stringIns[1:]
        if other.stringIns[0] == '/':
            RString = other.stringIns[1:]
        return int(LString) > int(RString)
    def __cmp__(self,other):
        LString,RString = self.stringIns,other.stringIns
        return int(LString) == int(RString)


class basinIDString(str):
    def __init__(self,stringIns):
        if stringIns[-1].isalpha():
            self.stringIns = stringIns[:-1]
            self.letter = stringIns[-1]
        else:
            self.stringIns = stringIns
            self.letter = chr(ord('A')-1)
    def __lt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        LLetter,RLetter = self.letter, other.letter
        if int(LString) != int(RString):
            return int(LString) < int(RString)
        else:
            return LLetter < RLetter
    def __gt__(self,other):
        LString,RString = self.stringIns,other.stringIns
        LLetter,RLetter = self.letter, other.letter
        if int(LString) != int(RString):
            return int(LString) > int(RString)
        else:
            return LLetter > RLetter
    def __cmp__(self,other):
        LString,RString = self.stringIns,other.stringIns
        LLetter,RLetter = self.letter, other.letter
        return (int(LString) == int(RString)) and (LLetter == RLetter)

class selectTCEQExtractor(HTMLParser): # derive new HTML parser
    def __init__(self, formatter) :        # class constructor
      HTMLParser.__init__(self, formatter)  # base class constructor
      self.selectBasins = []        # create an empty list for BasinID
      self.selectYears = []         # creat an empty list for Years recorded
      self.insideBasinIdSelect = False
      self.insideYearSelect = False
    def start_select(self, attrs) :  # override handler of <select ...>...</select> tags
      # process the attributes
      if len(attrs) > 0 :
         for name,value in attrs :
            if name == "name":
                if value == "basinid":
                    self.insideBasinIdSelect = True
                if value == "year":
                    self.insideYearSelect = True
            #elif attr[0] == ""
    def end_select(self):
        "Record the end of a hyperlink."
        if self.insideBasinIdSelect:
            self.insideBasinIdSelect = False
        if self.insideYearSelect:
            self.insideYearSelect = False
    def start_option(self,attrs):
        if self.insideBasinIdSelect:
            if len(attrs) > 0 :
                for name,value in attrs :
                    if name == "value":
                        self.selectBasins.append(value)
        if self.insideYearSelect:
            if len(attrs) > 0 :
                for name,value in attrs :
                    if name == "value":
                        self.selectYears.append(value)
    def get_selectBasins(self) :     # return the list of basinID
        return self.selectBasins
    def get_selectYears(self) :     # return the list of years
        return self.selectYears


config = ["testAdaptor_config\TCEQ_config\logParam.xml","..\\testAdaptor_config\TCEQ_config\srcParam.xml", \
          "..\\testAdaptor_config\TCEQ_config\pipeParam.xml","..\\testAdaptor_config\TCEQ_config\sinkParam.xml"]


class adaptor(object):

    # here,default TCEQ does not have a pipe
    def __init__(self, adtName, srcConfName, pipeConfName, sinkConfName,
                 logConfName=config[0], firstTimeRun=True):
        self.adtName = adtName
        self.firstTimeRun = firstTimeRun
        #assert not logConfName
        #get log config parameter dictionary
        self.logList = []
        #initialize log(s) according to parameters.
        log_args = get_conf_attr(logConfName)
        for attDict in log_args:
            reticLog.addLogger(self.logList,attDict)
        #source object
        self.adaptorSource = HTTPSource.source(get_conf_attr(srcConfName,'source'),self.logList)
        self.interval = self.adaptorSource.interval
        #no pipe object for TCEQ
        #sink obj
        self.adaptorSink = SQLSink_forTCEQ.sink(get_conf_attr(sinkConfName,'sink'),self.logList)
    #adaptor run
    def adpator_run(self):
        #new logic goes in here
        fullurl = "http://www.tceq.state.tx.us/compliance/monitoring/crp/data/samplequery.html#structure"
        req = urllib2.Request(fullurl)
        response = urllib2.urlopen(req)
        format = NullFormatter()           # create default formatter
        htmlparser = selectTCEQExtractor(format)        # create new parser object

        htmlparser.feed(response.read())      # parse the file saving the info about links
        htmlparser.close()
        basinIDsList = htmlparser.get_selectBasins()   # get the hyperlinks list
        yearsList = htmlparser.get_selectYears()
        if not self.firstTimeRun:
            yearsList = yearsList[-1:]
        #print basinIDsList;print yearsList
        for basinID in basinIDsList:
            if (basinIDString(basinID) < basinIDString("1006")):
                continue
            for year in yearsList:
                ##########
                #here loop each basinID for each year
                ########
                if ((basinIDString(basinID) == basinIDString("1006")) and (yearString(year) < yearString("1989"))):
                    continue
                self.adaptorSource.setHTTPParams([{"filetype":EVENT, "basinid":basinID,"year":year},{"filetype":RESULT, "basinid":basinID,"year":year}])
                self.adaptorSource.start()
                ###########This is get message from HttpSource, and send it to sink
                StringIOList = []
                while(self.adaptorSource.next()==1):
                    print "Content of this URL:  %s" % self.adaptorSource.URL
                    self.adaptorSource.commit()
                self.adaptorSource.commit()
                #last iteration has one more message left?
                for msg in self.adaptorSource.msg:
                    msg = msg.replace(chr(0),"")
                    StringIOList.append(StringIO.StringIO(msg))
                self.adaptorSink.getMsg(StringIOList)
                self.adaptorSink.updateDB(methodLookUpfile="additionalInfo/varMethod.vmdb")






if __name__ == "__main__":
    tceqTestAdaptor = adaptor(adtName="TCEQTest",srcConfName=config[1],sinkConfName=config[3] )
    print "Adaptor initialization complete..."
    tceqTestAdaptor.adpator_run()
    print "Testing TCEQ Adatpor complete..."
