#=========================================================================
#
# Python Source File
#
# NAME: SOAPSource.py
#
# AUTHOR: ADI
# DATE  : 31/12/2003
#
# COMMENT: 
#
#=========================================================================

import shutil, os, sys, string, StringIO, reticLog
import urllib, traceback

class source:


# ============================================================= #
#
#      Public methods (must exist) 
#
# ============================================================= #

    def __init__ (self, args, logger):
        try:
            self.args = args
            self.logList = logger
            self.name = args['name']
            self.SOAPMessage = args['SOAPMessage']
            self.SOAPAction = args['SOAPAction']
            self.url = args['url']
            self.proxyUrl = args['proxyUrl']
            self.params = {}
            for key in self.args.keys():
                if key[0] == '_':
                    self.params[key] = self.args[key]
            self.exitOnError = args['exitOnError']
            self.nbMsg = 0
            self.msg = ''
            self.msgName = ''            
            self.metadata = {}
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Source " + self.name + " initialized.")
        except KeyError:
            try:
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error during init phase of source : " + self.name)
            except:
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error during init phase of source")
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Parameter " + str(sys.exc_info()[1]) + " is missing in component definition" )
            sys.exit(1)
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Unknown error during initialization in source : " + self.name)
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
            sys.exit(1)
                
    def start (self):
        'Start the source of the adaptor (begin work...)'
        reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Starting the source : " + self.name)
        self.getMsg()
        return 0


    def next(self):
        if self.nbMsg == 0:
            return 0
        else:
            try:
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Starting processing phase of source " + self.name)
                self.updateAttributesFromMetadata()
                print "updateMetTermine"
                SOAPMessage = self.SOAPMessage
                for key in self.params.keys():
                    print "key : " + key
                    SOAPMessage = string.replace(SOAPMessage,'**' + key[1:] + '**',self.params[key])
                print "SOAPMsg : "  + SOAPMessage
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Executing SOAP request")
                reticLog.logDebug(self.logList, '( ' + self.name + ' ) ' +  "SOAP Request : " + SOAPMessage)
                if self.proxyUrl <> '':
                    urlopener = urllib.FancyURLopener( {'http' : self.proxyUrl } )
                else:
                    urlopener = urllib.URLopener()
                urlopener.addheaders.append(('Content-Length', str(len(SOAPMessage))))
                urlopener.addheaders.append(('Content-type', 'text/xml; charset="utf-8"'))
                urlopener.addheaders.append(('SOAPAction', self.SOAPAction))
                
                resp = urlopener.open(self.url, SOAPMessage)
                response = resp.read()
                reticLog.logDebug(self.logList, '( ' + self.name + ' ) ' +  "SOAP Response : " + response)
                self.msg = response
    
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "source " + self.name + " executed ok")
                return 1
            except:
                errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error during process phase of source : " + self.name)
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
                return 0                    

    def commit(self):
        'Commit the current message treatment'
        self.nbMsg = self.nbMsg - 1
        return 1        


    def updateAttributesFromMetadata(self):
        self.url = self.args['url']
        self.proxyUrl = self.args['proxyUrl']
        self.params = {}
        for key in self.args.keys():
            if key[0] == '_':
                self.params[key] = self.args[key]
        
       
        for key in self.metadata.keys():
            if string.find(self.args['url'],'[[' + key + ']]') >=0:
                self.url = string.replace(self.url,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['proxyUrl'],'[[' + key + ']]') >=0:
                self.proxyUrl = string.replace(self.proxyUrl,'[[' + key + ']]',self.metadata[key])
            for pkey in self.params.keys():
                if string.find(self.params[pkey],'[[' + key + ']]') >=0:
                    self.params[pkey] = string.replace(self.params[pkey],'[[' + key + ']]',self.metadata[key])

                    
# ============================================================= #
#
#      Private methods (optional)
#
# ============================================================= #


    def getMsg (self):
        'Get msg names and how many there are to process in the poll'
        self.nbMsg = 1       
        return self.nbMsg

        
                
                
    
            