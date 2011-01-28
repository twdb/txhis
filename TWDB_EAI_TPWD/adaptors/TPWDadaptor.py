import sys
sys.path.append("..")
from sources import fileSource
from pipes import toXML
from sinks import SQLSink_forTPWD
#from sinks import SQLSink
from xml.etree.ElementTree import *
import utility_EAI.twdbEaiLog as reticLog
from utility_EAI.twdbEaiUtil import get_conf_attr
import testTPWDmodel
from testTPWDmodel import major_area_str,minor_bay_str,station_str
from preprocessors.preprocess_TPWD import preprocess_batch,direcotryPath
import StringIO,threading,thread

config = ["testAdaptor_config\TPWD_config\logParam.xml","testAdaptor_config\srcParam.xml", \
          "testAdaptor_config\pipeParam.xml","testAdaptor_config\sinkParam.xml"]            

class adaptor(object):
    def __init__(self, adtName,
                       srcConfName,pipeConfName,sinkConfName,
                       logConfName = config[0]):
        self.adtName = adtName
        #assert not logConfName
        #get log config parameter dictionary         
        self.logList = []
        #initialize log(s) according to parameters.
        log_args = get_conf_attr(logConfName)
        for attDict in log_args:
            reticLog.addLogger(self.logList,attDict)
        #source object
        
        self.adaptorSource = fileSource.source(get_conf_attr(srcConfName,'source'),self.logList)
        self.interval = self.adaptorSource.interval
        #pipe object
        self.adaptorPipe = toXML.pipe(get_conf_attr(pipeConfName,'pipe'),self.logList)
        #sink obj
        self.adaptorSink = SQLSink_forTPWD.sink(get_conf_attr(sinkConfName,'sink'),self.logList)      
    #adaptor run
    def adpator_run(self):
        #preprocessing, so that all intermediate files for file source are generated        
        try:
            preprocess_batch(direcotryPath,self.logList)
        except:
            import sys,traceback
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.adtName + " ) Unknown error during initialization in sink")
            reticLog.logError(self.logList, "( " + self.adtName + " ) " + errorMessage)
        self.adaptorSource.start()
        while self.adaptorSource.next()==1:
            self.adaptorPipe.getMsg(self.adaptorSource.msg)
            self.adaptorPipe.process()
            self.adaptorSource.commit()
        self.adaptorSource.commit()
        for i in range(len(self.adaptorPipe.msgList)):
            self.adaptorSink.getMsg(self.adaptorPipe.msgList[i])
            #print self.adaptorSink.msg
            recordList = self.adaptorSink.getRecordList()
            print str(len(recordList))+" XML records"+' generated'+' for %s'%self.adaptorSource.metadata['filename'][i]
            self.adaptorSink.processSites(recordList,self.adaptorSource.metadata['filename'][i])
            updateList = self.adaptorSink.prepareUpdateObject(recordList,testTPWDmodel.tpwdProcessInfo)
            print str(len(updateList))+" database records"+' to be inserted'
            self.adaptorSink.updateDB(updateList)

#redefine runCommand 
#def 