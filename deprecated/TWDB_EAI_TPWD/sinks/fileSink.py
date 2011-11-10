#=========================================================================
#
# Jython Source File
#
# NAME: fileSink.py
#
# AUTHOR: ADI
# DATE  : 30/07/2003
#
# COMMENT: 
#
#=========================================================================

import os, sys, string, StringIO, time, reticLog, traceback, random, reticUtils
import zipfile

class sink:


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
            self.msg = ''
            self.filePath = args['filePath']
            self.fileName = args['fileName']
            self.addTimestamp = args['addTimestamp']
            self.fileType = 'flat'
            self.writeMethod = 'overwrite'
            if args.has_key('zip'):
                self.zip = args['zip']
            else:
                self.zip = 'n'
                self.args['zip'] = 'n'
            self.maxBytes = 0
            self.metadata = {}
            if args.has_key('fileType'):
                self.fileType = args['fileType']
            if args.has_key('writeMethod'):
                self.writeMethod = args['writeMethod']                
            if self.fileType.lower() == 'xml' and self.writeMethod.lower() == 'append':
                try:
                    self.fp = open(os.path.join(self.filePath, self.fileName), 'r')
                    self.lastLine = self.fp.readlines()[-1]
                    print "Last line : " + self.lastLine
                    self.fp.close()
                    self.fp = open(os.path.join(self.filePath,self.fileName), 'a+')
                except:
                    self.lastLine = ''
                    print "Last line retrieval => error..."
                    self.fp = open(os.path.join(self.filePath,self.fileName), 'a+')
            elif self.fileType.lower() == 'flat' and self.writeMethod.lower() == 'append':
                self.fp = open(os.path.join(self.filePath,self.fileName), 'a')
                
        except KeyError:
            reticLog.logError(self.logList, "Error during FileSink initialization")
            reticLog.logError(self.logList, "Parameter " + str(sys.exc_info()[1]) + " is missing in sink definition" )
            sys.exit(1)
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Unknown error during initialization in sink")
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            sys.exit(1)
            

    def getMsg (self, message):
        try:
            reticLog.logInfo(self.logList, "( " + self.name + " ) Retrieving message for sink : " + self.name)
            # Re-initialize msg to get new message
            self.msg = ''
            self.msg = message
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Error during message retrieval in sink : " + self.name)                        
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            return 1
        
        
    def process (self):
        try:
            msg = StringIO.StringIO()
            msg.write(self.msg)    
            msg.seek(0)
            self.updateAttributesFromMetadata()
            reticLog.logInfo(self.logList, "( " + self.name + " ) Processing file in sink " + self.name)
            if self.addTimestamp == 'y':
                index = 0
                i = 0
                while index >= 0:
                    i = index
                    index = string.find(self.fileName,'.',index+1)
                now = time.time()
                timestamp = str(time.localtime()[0])+reticUtils.completeWithZero(str(time.localtime()[1]))+reticUtils.completeWithZero(str(time.localtime()[2]))+reticUtils.completeWithZero(str(time.localtime()[3]))+reticUtils.completeWithZero(str(time.localtime()[4]))+reticUtils.completeWithZero(str(time.localtime()[5]))+str(int(random.random()*10000))
                reticLog.logDebug(self.logList, "Timestamp added to filename : " + timestamp)
                new_filename = self.fileName[:i] + timestamp + self.fileName[i:]
            else:
                new_filename = self.fileName
            if self.writeMethod == 'overwrite':
                if self.zip == 'y':                    
                    reticLog.logDebug(self.logList, "Message is being zipped")
                    tmpFpName = '_tmp' + str(int(random.random()*100000000)) + '.dat'
                    tmpFpName2 = '_tmp' + str(int(random.random()*100000000)) + '.dat'
                    tmpFpMsg = open(tmpFpName2,'w+b')
                    tmpFpMsg.write(self.msg)
                    tmpFpMsg.close()
                    tmpZipFile = zipfile.ZipFile(os.path.join(os.getcwd(),tmpFpName),'w',zipfile.ZIP_DEFLATED)
                    tmpZipFile.write(tmpFpName2,self.fileName)
                    
                    tmpZipFile.close()
                    tmpZipFile = open(os.path.join(os.getcwd(),tmpFpName),'r+b')
        
                    self.msg = tmpZipFile.read()
                    tmpZipFile.close()                        
                    os.remove(tmpFpName)
                    os.remove(tmpFpName2)
                    new_filename = new_filename + '.zip'
                    self.fp = open(os.path.join(self.filePath,new_filename),'wb')
            
                elif reticUtils.istext(msg):
                    reticLog.logDebug(self.logList, "Message identified as being text")
                    self.fp = open(os.path.join(self.filePath,new_filename),'w')
                else:
                    reticLog.logDebug(self.logList, "Message identified as being binary data")
                    self.fp = open(os.path.join(self.filePath,new_filename),'wb')
                
                self.fp.truncate()
                self.fp.write(self.msg)
                self.fp.close()
                reticLog.logInfo(self.logList, "( " + self.name + " ) New file created by sink " + self.name + " : " + self.filePath + new_filename)
            else:
                if self.fileType == 'flat':
                    file_content = self.msg
                    self.fp.write(file_content)
                else:
                    msg.seek(0)
                    addLines = msg.readlines()
                    if len(self.lastLine) > 0:
                        self.fp.seek(-(len(self.lastLine)+1),2)
                        self.fp.truncate()
                        del addLines[0:2]
                    self.fp.writelines(addLines)
                    self.fp.flush()
                    self.lastLine = addLines[-1]
                reticLog.logInfo(self.logList, "( " + self.name + " ) Data appended to file in sink " + self.name + " - file : " + self.filePath + new_filename)                                
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Error during message processing in sink : " + self.name)                        
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            return 1


    def updateAttributesFromMetadata(self):
        self.filePath = self.args['filePath']
        self.fileName = self.args['fileName']
        self.addTimestamp = self.args['addTimestamp']
        self.zip = self.args['zip']
        
        for key in self.metadata.keys():
            if string.find(self.args['filePath'],'[[' + key + ']]') >=0:
                self.filePath = string.replace(self.filePath,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['fileName'],'[[' + key + ']]') >=0:
                self.fileName = string.replace(self.fileName,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['addTimestamp'],'[[' + key + ']]') >=0:
                self.addTimestamp = string.replace(self.addTimestamp,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['zip'],'[[' + key + ']]') >=0:
                self.zip = string.replace(self.zip,'[[' + key + ']]',self.metadata[key])
        


# ============================================================= #
#
#      Private methods (optional) 
#
# ============================================================= #


    def completeWithZero(self,number):
        if number >= 0 and number <=9:
            return '0' + str(number)
        else:
            return str(number)