from sources import fileSource
from pipes import toXML
from sinks import SQLSink_forTPWD  
#from sinks import SQLSink
from xml.etree.ElementTree import *
import utility_EAI.twdbEaiLog as reticLog
from utility_EAI.twdbEaiUtil import get_conf_attr
import testTPWDmodel
from testTPWDmodel import major_area_str,minor_bay_str,station_str
import StringIO

#parsing xml file, get component key list
def get_attr(fileName,mode="log"):
    res = []
    root = ElementTree(file=fileName)
    #Create an iterator
    iter = root.getiterator()
    if mode == "log":
        for element in iter:
        #Next the attributes (available on the instance itself using
        #the Python dictionary protocol)
            if element.keys() and (element.tag == 'logger'):
                res.append(element.attrib)
    #extract source attributes
    elif mode == "source":
        for element in iter:
            if element.keys() and (element.tag == 'source'):
                res = element.attrib
    #extract pipe attributes
    elif mode == "pipe":
        for element in iter:
            if element.keys and (element.tag == 'pipe'):
                tempRes = element.attrib
                tempRes['fieldNames'] = {}
                tempRes['fieldLength'] = {}
                #pipe children tag, for fields
                if element.getchildren():
                    fieldIndex = 0
                    for child in element.getchildren():
                        if child.tag == 'field':
                            tempRes['fieldNames'][fieldIndex] = child.attrib['name']
                            fieldIndex += 1
                res = tempRes
    #extract sink attributes
    elif mode == 'sink':
        for element in iter:
            if element.keys() and (element.tag == 'sink'):
                res = element.attrib
                if element.getchildren():
                    for child in element.getchildren():
                        res['dbFactroyArg'] = child.attrib
    #extract source attributes
    else:
        import sys
        print "unkown component configuration mode..."
        sys.exit()
    return res

#build a complete adapter (including source,pipe(s) and sink (s))
#note: an adapter can have multiple log(s), pipe(s) and sink(s)
config = ["testAdaptor_config\logParam.xml","testAdaptor_config\srcParam.xml", \
          "testAdaptor_config\pipeParam.xml","testAdaptor_config\sinkParam.xml"]

def test(logConf = config[0],srcConf = config[1], pipeConf = config[2], sinkConf = config[3] ):
    #get log config parameter dictionary 
    log_args = get_attr(logConf)
    #logList parameter, parameter for source, pipe and sink
    logList = []
    #initialize log(s) according to parameters.
    for attDict in log_args:
         reticLog.addLogger(logList,attDict)
    #building up sources
    print "Initialize source..."
    src_args = get_attr(srcConf,'source')
    testSource = fileSource.source(src_args,logList)
    testSource.start()
    #print testSource.msg
    #building up pipes
    print "Initialize pipe(s)..."
    pipe_args = get_attr(pipeConf,'pipe')
    testPipe = toXML.pipe(pipe_args,logList)
    while testSource.next()==1:
        testPipe.getMsg(testSource.msg)
        testPipe.process()
        testSource.commit()
    #print testPipe.InMsg.read()
    #raw_input("here")
    #building up sinks
    testSource.commit()       
    print "Initialize sink(s)..."
    sink_args = get_attr(sinkConf,'sink')
    testSink = SQLSink_forTPWD.sink(sink_args,logList)
    for i in range(len(testPipe.msgList)):
        testSink.getMsg(testPipe.msgList[i])
        print "sinking start..."
        #print testSink.msg
        recordList = testSink.getRecordList()
        print raw_input(str(len(recordList))+" XML records"+' generated'+' for %s'%testSource.metadata['filename'][i])
        testSink.processSites(recordList)
        updateList = testSink.prepareUpdateObject(recordList,testTPWDmodel.tpwdProcessInfo)
        print raw_input(str(len(updateList))+" database records"+' to be inserted')
        testSink.updateDB(updateList)
    #print open(".\pipes\\test_SANT__wq_out.xml",'r').read()
    #print "here"
    
    
    



if __name__ == '__main__':
    test()
