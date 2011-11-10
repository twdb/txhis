#=========================================================================
#
# Jython Source File
#
# NAME: SQLTreeSource.py
#
# AUTHOR: ADI
# DATE  : 05/08/2003
#
# COMMENT: 
#
#=========================================================================

import os, sys, string, StringIO, math, traceback, copy
import random
from org.apache.xerces.parsers import DOMParser
from org.xml.sax import InputSource
from org.apache.xpath import *
from org.w3c.dom import Document
from org.w3c.dom import Node
from org.w3c.dom import NodeList
from org.apache.xml.serialize import DOMSerializerImpl
import java.io.StringReader



sys.path.append('..')
sys.path.append('../pipes')
sys.path.append('../sources')
sys.path.append('../sinks')


import dbFactory, reticLog, reticUtils

class sink:


# ============================================================= #
#
#      Public methods (must exist) 
#
# ============================================================= #

    def __init__ (self, args, logger):
        try:
            self.logList = logger
            self.name = args['name']
            self.args = args
            reticLog.logInfo(self.logList, '( ' + self.name + ' ) ' +  "Intitializing SQLTreeSource : " + self.name)            
            self.exitOnError = 'y'
            self.xpath = XPathAPI()
            self.metadata = {}
            self.dsn = args['dsn']
            self.user = args['user']
            self.password = args['password']
            self.dbType = args['dbType']
#            self.db = args['db']
            self.msgSize = args['msgSize']
            self.treeQ = args['treeQ']
            self.rootTag = args['rootTag']
            self.encoding = args['encoding']
            self.msgSize = float(args['msgSize'])
            self.msgList = []
            self.fieldList = []
            self.nbMsg = 0
            self.tmpFileName = 'tmp_SQLTreeSource' + str(int(random.random()*100000000)) + '.dat'
#            self.msg = open(self.tmpFileName,'w+')
            self.msg = ''
            self.tmpMsg = StringIO.StringIO()
            self.msgName = ''
            self.curArgs = {}
            self.dbConnection = dbFactory.dbFactory(args, self.logList)
            self.dbConnection.connect(args)            
            if args.has_key('exitOnError'):
                self.exitOnError = args['exitOnError']
        except KeyError:
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Error on SQLTreeSource initialization")
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Parameter " + str(sys.exc_info()[1]) + " is missing on source definition" )
            sys.exit(1)
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + "Unknown error on SQLTreeSource initialization. Exiting...")
            reticLog.logError(self.logList, '( ' + self.name + ' ) ' + errorMessage)         
            sys.exit(1)                
                    


    def getMsg (self, message):
        'Initializes input buffer with message content'
        try:
            reticLog.logInfo(self.logList, '(' + self.name + ') ' + "Getting message into sink")
            self.InMsg = ''
            self.msg = ''
            self.InMsg = message
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '(' + self.name + ') ' + "Error during message retrieval in sink" )                        
            reticLog.logError(self.logList, '(' + self.name + ') ' + errorMessage)
            return 1
        
    

    def process(self):
        'Get the next message to be processed or return that sources are dry'
        self.msg = ''
        self.tmpMsg = StringIO.StringIO()
        try:
            parser = DOMParser( )
            parser.parse(InputSource(java.io.StringReader(self.InMsg)))
            XMLStream = parser.getDocument()
            print "message parsed ok" 
            
            resultNodeList = self.xpath.selectNodeList(XMLStream,'/*/' + self.treeQ['request']['recTag'])
            for i in range(resultNodeList.getLength()):
                currentTag = resultNodeList.item(i)
                print "query 1"
                fieldList = self.xpath.selectNodeList(currentTag,'*')
                query = self.treeQ['request']['SQL']
                (generatedId, modQuery) = self.prepareInsert(query, fieldList)
                print "Generated query : "  + str(modQuery)
                self.executeQuery(modQuery)
                for nextQuery in self.treeQ['request']['nextRequests']:
                    print "next query" 
                    self.processQuery(nextQuery, generatedId, currentTag)
                    
            return 0
            
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '(' + self.name + ') ' + "Error during message processing" )                        
            reticLog.logError(self.logList, '(' + self.name + ') ' + errorMessage)
            return 1


# ============================================================= #
#
#      Private methods (optional)
#
# ============================================================= #

    def prepareInsert(self,query,fieldList):
##        print "preparing insert"
##        print fieldList
        try:
            fieldDict = {}
            id = -1
            for i in range(fieldList.getLength()):
                field = fieldList.item(i)
                if field.nodeType == field.ELEMENT_NODE:
                    if field.firstChild <> None:
                        fieldDict[field.tagName] = field.firstChild.data
                    else:
                        fieldDict[field.tagName] = ''
                
            if string.find(query,'$generateId$') > 0:
                id = self.generateId()
                query = string.replace(query,'$generateId$',str(id))
    ##        print "Generated Id : " + str(id)
            for key in fieldDict.keys():
                if string.find(query,"'$" + str(key) + "$'") < 0:
                    if str(fieldDict[key]) == '':
                        query = string.replace(query, '$' + str(key) + '$', 'null')
                    else:
                        query = string.replace(query, '$' + str(key) + '$', str(fieldDict[key]))
                else:
                    query = string.replace(query, '$' + str(key) + '$', str(fieldDict[key]))
    ##        print "Generated Query : " + query
            
            return (id, query)
        except:
            traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
        

    def executeQuery(self, modQuery):
        curArgs = {}
        curArgs['cursorName'] = 'cursor'
        curArgs['SQL'] = modQuery
        curArgs['nbRecToFetch'] = 0
        self.dbConnection.addCursor(curArgs)
        self.dbConnection.executeSQL(curArgs)
        self.dbConnection.commit()
        self.dbConnection.closeCursor(curArgs)
        self.dbConnection.removeCursor(curArgs)
        
        


    def processQuery(self, currentQuery, parentId, currentTag):
        try:
            resultNodeList = self.xpath.selectNodeList(currentTag,currentQuery['recTag'])
            for i in range(resultNodeList.getLength()):
                nextTag = resultNodeList.item(i)
                fieldList = self.xpath.selectNodeList(nextTag,'*')
                query = currentQuery['SQL']
                query = string.replace(query,'$parentGeneratedId$',str(parentId))
                (generatedId, modQuery) = self.prepareInsert(query, fieldList)
                print "Generated Query : " + modQuery
                self.executeQuery(modQuery)
                for nextQuery in currentQuery['nextRequests']:
                    print "Deeper"
                    self.processQuery(nextQuery, generatedId, nextTag)
        except:
            print traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]

    def generateId(self):
        try:
            fp = open(os.path.join('.','sysdb','id.dat'),'r')
            txtId = fp.read()
            fp.close()
            txtId = string.replace(txtId,'\n','')
            newId = int(txtId) + 1
        except:
            newId = 1
            
        fp = open(os.path.join('.','sysdb','id.dat'),'w')
        fp.write(str(newId))
        fp.close()
    
        return newId

    
    def updateAttributesFromMetadata(self):
        self.dsn = self.args['dsn']
        self.user = self.args['user']
        self.password = self.args['password']
        self.dbType = self.args['dbType']
        self.msgSize = float(self.args['msgSize'])
        self.rootTag = self.args['rootTag']
        self.encoding = self.args['encoding']
        self.nbThreads = self.args['nbThreads']
    
      
        for key in self.metadata.keys():
            if string.find(self.args['dsn'],'[[' + key + ']]') >=0:
                self.dsn = string.replace(self.dsn,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['user'],'[[' + key + ']]') >=0:
                self.user = string.replace(self.user,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['password'],'[[' + key + ']]') >=0:
                self.password = string.replace(self.password,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['dbType'],'[[' + key + ']]') >=0:
                self.dbType = string.replace(self.dbType,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['msgSize'],'[[' + key + ']]') >=0:
                self.msgSize = string.replace(self.msgSize,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['rootTag'],'[[' + key + ']]') >=0:
                self.rootTag = string.replace(self.rootTag,'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['encoding'],'[[' + key + ']]') >=0:
                self.encoding = string.replace(self.encoding,'[[' + key + ']]',self.metadata[key])
                
        
    
    def updateSQLFromMetadata(self,args):
        newArgs = copy.copy(args)
        for key in self.metadata.keys():
            if string.find(newArgs['SQL'],'[[' + key + ']]') >=0:
                newArgs['SQL'] = string.replace(newArgs['SQL'],'[[' + key + ']]',self.metadata[key])
        return newArgs
                