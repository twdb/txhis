#=========================================================================
#
# Python Source File
#
# NAME: ftpSource.py
#
# AUTHOR: ADI
# DATE  : 22/07/2003
#
# COMMENT: 
#
#=========================================================================

import shutil, os, sys, string, StringIO, reticLog, traceback
from ftplib import FTP
from fnmatch import *


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
            self.exitOnError = 'y'
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Intitializing ftpSource : " + self.name)            
            self.ftpHost = args['ftpHost']
            self.ftpPort = int(21)
            self.ftpUser = args['ftpUser']
            self.ftpPass = args['ftpPass']
            self.filePath = args['filePath']
            self.fileFilter = args['fileFilter']
            self.newExtension = args['newExtension']
            self.msgList = []
            self.metadata = {}
            self.nbMsg = 0
            self.msg = ''
            self.msgName = ''
            self.name = args['name']
            self.ftpConn = FTP()
            if args.has_key('exitOnError'):
                self.exitOnError = args['exitOnError']
            if self.filePath[-1] != '/':
                self.filePath = self.filePath + '/'
            if args['ftpPort'] != '':
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Using provided port for FTP connection : " + args['ftpPort'])
                self.ftpPort = int(args['ftpPort'])
            else:
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "No port specified for FTP connection. Using default : 21")
        except KeyError:
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on ftpSource initialization")
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Parameter " + str(sys.exc_info()[1]) + " is missing on source definition. Exiting..." )
            sys.exit(1)
        except :
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Unknown error on ftpSource initialization. Exiting...")
            sys.exit(1)        
                
    def start (self):
        'Start the source of the adaptor (begin work...)'
        reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Starting the source adaptor")
        try:
            self.connect()
            self.getMsg()
            self.ftpConn.close()
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on adaptor start on source : " + self.name)                        
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
            if self.exitOnError.lower() == 'y':
                sys.exit(1)

    def next(self):
        'Get the next message to be processed or return that sources are dry'
        try:
            self.connect()
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on message retrieval on source : " + self.name)                        
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
            if self.exitOnError.lower() == 'y':
                sys.exit(1)
                
        if self.nbMsg == 0:
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Sources dry on source ")
            return 0
        else:
            try:
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Messages Left on queue of adaptor : " + str(self.nbMsg))
                reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Processing file : " + self.msgList[0])
                self.msgName = self.msgList[0]

                dotIndex = string.find(self.msgName,'.')
                if dotIndex > 0:
                    self.metadata['filename'] = string.split(self.msgName,'.')[0]
                    self.metadata['extension'] = string.split(self.msgName,'.')[1]
                else:
                    self.metadata['filename'] = self.msgName
                    self.metadata['extension'] = ''
                
                msg = StringIO.StringIO()
                sys.stdout = msg
                self.ftpConn.retrlines('RETR ' + self.msgName)
                sys.stdout = sys.__stdout__
                msg.seek(0)
                self.msg = msg.read()
                self.ftpConn.close()
                return 1
            except:
                errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on message retrieval on source : " + self.name)                        
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
                if self.exitOnError.lower() == 'y':
                    sys.exit(1)
                return 1

    def commit(self):
        'Commit the current message treatment'
        if self.nbMsg > 0 : 
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Commiting msg " + self.msgList[0] + " on source : " + self.msgName)
            msgName = self.msgList[0]
            try:    
                if self.newExtension != '':
                    reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Processing file : " + self.msgList[0])
                    self.connect()
                    self.ftpConn.sendcmd('RNFR ' + self.msgName)
                    self.ftpConn.sendcmd('RNTO ' + self.msgName + '.' + self.newExtension)
                self.nbMsg = self.nbMsg - 1 
                self.msgList = self.msgList[1:]
                self.msg = ''
                return 1
            except:
                errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on commit phase on source - File : " + msgName)                        
                reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)
                if self.exitOnError.lower() == 'y':
                    sys.exit(1)
                return 0
        else:
            return 0
        
                    
# ============================================================= #
#
#      Private methods (optional)
#
# ============================================================= #


    def getMsg (self):
        'Get msg names and how many there are to process in the poll'
        
        fileList = self.ftpConn.nlst()
       
        for i in range(len(fileList)):
            try:
                if fnmatch(fileList[i], self.fileFilter):
                    self.addMsg(fileList[i])
            except: 
                pass

        return self.nbMsg

        
    def connect (self):
        self.ftpConn.connect(host=self.ftpHost, port=self.ftpPort)
        self.ftpConn.login(self.ftpUser,self.ftpPass)
        self.ftpConn.set_pasv(1)
        self.ftpConn.cwd(self.filePath)
        
    def matchesPattern (self, fileName, pattern):
        pattern_split = string.split(pattern,'*')
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
        

                
                
    
            