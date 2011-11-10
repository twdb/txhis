#=========================================================================
#
# Python Source File
#
# NAME: HTTPSource.py
#
# AUTHOR: Tony Tan
# DATE  : 22/07/2010
#
# COMMENT: 
#
#=========================================================================

import shutil, os, sys, string, cStringIO
sys.path.append("..")
import urllib2, traceback
from urllib import urlencode
import utility_EAI.twdbEaiLog as reticLog
import utility_EAI.twdbEaiUtil as reticUtils

EVENT = "1"
RESULT = "2"

class source:
# ============================================================= #
#
#      Public methods (must exist) 
#
# ============================================================= #

    def __init__ (self, args, logger):
        try:
            self.logList = logger
            self.name = args['name']
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Intitializing HTTPSource : " + self.name)
            self.URL = args['URL']
            self.exitOnError = 'n'
            self.msgList = []
            self.nbMsg = 0
            self.msg = []
            self.msgName = ''
            self.params = []
            self.metadata = {}
            #this is used for wait(interval) function, so use float
            if args.has_key('pollPeriod'):
                self.interval = float(args['pollPeriod'])
            if args.has_key('params'):
                self.params = args['params']
            if args.has_key('exitOnError'):
                self.exitOnError = args['exitOnError']
        except KeyError:
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on HTTPSource initialization")
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Parameter " + str(sys.exc_info()[1]) + " is missing on source definition" )
            sys.exit(1)
        except:
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Unknown error on HTTPSource initialization")
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1]))
            raise
            sys.exit(1)
                
    def setHTTPParams(self,params):
        self.params = params
    
    
    def start (self):
        """Start the source of the adaptor (begin work...)"""
        reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Starting the http source adaptor")
        self.getMsg()
        return 0


    def next(self):
        'Get the next message to be processed or return that sources are dry'
        if self.nbMsg == 0:
            return 0
        else:
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Messages Left on queue of adaptor : " + str(self.nbMsg))
             # No params are provided, processing raw URL. (without GET/POST request)
            if len(self.params) == 0:    
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Retrieving message from : " + self.URL)
                try:
                    request = urllib2.Request(self.URL)
                    connection = urllib2.urlopen(request)
                    self.msg.append(connection.read())
                    reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Message retrieved on adaptor: " + self.name)
                except:
                    errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                    reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on message retrieval on source : " + self.name)                        
                    reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
                    if self.exitOnError.lower() == 'y':
                        sys.exit(1)
            else:
                self.msg = []
                for param in self.params:
                    # Params are provided, processing URL passing them through GET method
                    # There are as many calls as there are param lists             
                    paramLine = '?'
                    for key in param.keys():
                        self.metadata[key] = param[key]
                    paramLine = urlencode(self.metadata)

                    reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Retrieving message from : " + self.URL+"?" + paramLine)
                    successful = False
                    while not successful:
                        try:
                            request = urllib2.Request("?".join([self.URL,paramLine]))
                            connection = urllib2.urlopen(request)
                            self.msg.append(connection.read())
                            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Message retrieved on adaptor: " + self.name)
                        except:
                            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on message retrieval on source : " + self.name)                        
                            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
                            if self.exitOnError.lower() == 'y':
                                sys.exit(1)
                        else:
                            successful = True                            
            return 1

    def commit(self):
        'Commit the current message treatment'
        self.nbMsg = self.nbMsg - 1
        return 1        
                    
# ============================================================= #
#
#      Private methods (optional)
#
# ============================================================= #


    def getMsg (self):
        """Get msg names and how many there are to process in the poll"""
        self.nbMsg = 1       
        return self.nbMsg
    
#self testing code
if __name__ == "__main__":
    logAttDic = {#get self name
                 'name': 'httpsource testing',
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'ConsoleAppender',}
    logList = []
    reticLog.addLogger(logList,logAttDic)
    src_args = {}
    src_args['name'] = "testing httpsource"
    src_args['URL'] = "http://www.tceq.state.tx.us/cgi-bin/compliance/monops/crp/sampquery.pl"
    src_args['params'] = [{"filetype":EVENT, "basinid":"0510","year":"2005"}]
    testSource = source(src_args,logList)
    testSource.start()
    while(testSource.next()==1):
        raw_input("Content of this URL:  %s" % testSource.URL)
        print testSource.msg
        testSource.commit()
    testSource.commit()
    
        
                
                
    
            
