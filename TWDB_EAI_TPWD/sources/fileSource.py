#=========================================================================
#
# Python Source File
#
# NAME: FileSource.py
#
# AUTHOR: Tony
# DATE  : 03/01/2010
#
# COMMENT: 
#
#=========================================================================

import shutil, os, sys, string, StringIO, traceback 
sys.path.append("..")
import utility_EAI.twdbEaiLog as reticLog
import utility_EAI.twdbEaiUtil as reticUtils

from fnmatch import *

class source:


# ============================================================= #
#
#      Public methods (must exist) 
#
# ============================================================= #

    def __init__ (self, args, logList):
        try:
            self.logList = []
            self.logList = logList
            self.name = args['name']
            self.exitOnError = 'y'
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Intitializing fileSource")
            self.fileFilter = args['fileFilter']
            self.newExtension = args['newExtension']
            self.msgList = []
            self.metadata = {}
            self.nbMsg = 0
            self.msg = ''
            self.msgName = ''
            self.filePath = args['filePath']
            #this is used for wait(interval) function, so use float
            self.interval = float(args['pollPeriod'])
            #here,determine the os path seperator, '\\' for nt, '/' for linux
            import os
            self.filePath = self.filePath + os.sep
            if args.has_key('exitOnError'):
                self.exitOnError = args['exitOnError']
        except KeyError:
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on fileSource initialization")
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Parameter " + str(sys.exc_info()[1]) + " is missing on source definition" )
            sys.exit(1)
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Unknown error on initialization on source")                        
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
            sys.exit(1)
            
            
             
    def start (self):
        'Start the source of the adaptor (begin work...)'
        try:
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Starting the source adaptor")
            self.getMsg()        
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Unknown error on start of source")                        
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
            sys.exit(1)

    def next(self):
        'Get the next message to be processed or return that sources are dry'
        if self.nbMsg == 0:
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Sources dry on source ")
            return 0
        else:
            try:
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Messages Left on queue of adaptor : " + str(self.nbMsg))
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Retrieving file : " + self.msgList[0])
                self.msgName = self.msgList[0]
                dotIndex = string.find(self.msgName,'.')
                if dotIndex > 0:
                    if(not self.metadata.has_key('filename')):
                        self.metadata['filename'] = []
                    self.metadata['filename'].append(string.split(self.msgName,'.')[0])
                    self.metadata['extension'] = string.split(self.msgName,'.')[1]
                else:
                    if(not self.metadata.has_key('filename')):
                        self.metadata['filename'] = []
                    self.metadata['filename'] = self.msgName
                    self.metadata['extension'] = ''
                #file reading happend here
                fp = open(os.path.join(self.filePath,self.msgList[0]))
                if reticUtils.istext(fp):
                    fp.close()
                    fp = open(os.path.join(self.filePath,self.msgList[0]),'r')
                else:
                    fp.close()
                    fp = open(os.path.join(self.filePath,self.msgList[0]),'rb')                    
                self.msg = fp.read()
                fp.close()
                return 1
            except:
                errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on message retrieval on source : " + self.name)                        
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
                if self.exitOnError.lower() == 'y':
                    return 0
                else:
                    return 1


    def commit(self):
        'Commit the current message treatment'
        if self.nbMsg > 0 : 
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Commiting msg " + self.msgList[0] + " on source : " + self.name)
            msgName = self.msgList[0]
            try:    
                #if self.newExtension != '' and self.newExtension != ' ':
                    #shutil.copyfile(self.filePath+self.msgName,self.filePath+self.msgName+self.newExtension)
                shutil.os.remove(self.filePath+self.msgName)
                self.nbMsg = self.nbMsg - 1 
                self.msgList = self.msgList[1:]
                self.msg = ''
                return 0
            except:
                errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on commit phase on source - File : " + msgName) 
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
                return 1
                
        else:
                return 1
                    
# ============================================================= #
#
#      Private methods (optional)
#
# ============================================================= #

        
    def getMsg (self):
        'Get msg names and how many there are to process in the poll'
        fileList = os.listdir(self.filePath)
       
        for i in range(len(fileList)):
            try:
                if fnmatch(fileList[i], self.fileFilter):
                    #raw_input("find matched file %s" % fileList[i] )
                    self.addMsg(fileList[i])
            except: 
                pass
        #the return just for debugging
        return self.nbMsg
                
    def matchesPattern (self, fileName, pattern):
        pattern_split = string.split(pattern,'*')
        toRemoveList = []
        for i in range(len(pattern_split)):
            if pattern_split[i] == '':
                toRemoveList.Append(i)
        for index in toRemoveList:
            del pattern_split[index]
        index = -1
        if string.find(pattern,'*')>=0 :
            for i in range(len(pattern_split)):
                if i == len(pattern_split)-1:
                    if pattern_split[i] == fileName[-len(pattern_split[i]):]:
                        return 1
                    else:
                        return 0
                index = string.find(fileName,pattern_split[i],index+1)
                if index < 0:
                    return 0
        elif pattern != fileName :
            return 0
             
        return 1
     
    def addMsg(self, name):
        self.nbMsg = self.nbMsg + 1
        self.msgList.append(name)

#self test, assuming data file are in place
if __name__ == '__main__':
    logAttDic = {#get self name
                 'name':sys.argv[0].split(".")[0],
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'ConsoleAppender',
                }
    logAttDic_2 = {#get self name
                 'name':sys.argv[0].split(".")[0],
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'FileAppender',
                 'mode': 'w',
                 'fileName':'fileSourceTest.txt'
                }
    logList = []
    reticLog.addLogger(logList,logAttDic)
    reticLog.addLogger(logList,logAttDic_2)
    src_args = {}
    #get os type
    if sys.platform == 'win32':        
        src_args['filePath'] = '..\\file_source_exp\\'
    else:
        src_args['filePath'] = '/home/ttan/file_source_exp/'
    src_args['fileFilter'] = '*.csv'
    src_args['newExtension'] = ''
    src_args['name'] = 'fileSourceTest'
    src_args['pollPeriod'] = '190'
    testSource = source(src_args,logList)
    testSource.start()
    i = 0;
    while(testSource.next()==1):
        raw_input("content of file %s" % testSource.metadata['filename'][i])
        i = i + 1
        print testSource.msg
        testSource.commit()
    testSource.commit()

                
                
    
        
