#=========================================================================
#
# Python Source File
#
# NAME: fileSink.py
#
# AUTHOR: Tony
# DATE  : 3/11/2010
#
# COMMENT: 
#
#=========================================================================

import os, sys, string, StringIO, math, traceback, time
#from pyxml import *
from threading import *

sys.path.append('..')
sys.path.append('../pipes')
sys.path.append('../sources')
sys.path.append('../sinks')

#from multithreads import *
import utility.twdbEaiLog as reticLog
import dbFactory
#orm = Object Relation Mapping
from sqlalchemy import orm,exc,func
#processing xml file
from xml.etree.ElementTree import *
import testTWDBmodel


class myThread(Thread):
    def __init__(self, target, args=(), name=None):
        # we need a tuple here
        #if type(args)<>type((1,)):
            #args = (args,)
        Thread.__init__(self, target=target, name=name, args=args)
        self.start()
    def __str__(self):
        return self.getName()



class sink:


# ============================================================= #
#
#      Public methods (must exist) 
#
# ============================================================= #

    def __init__ (self, args, logger):
        try:
            self.args = args
            self.msg = ''
            self.logList = logger
            self.name = args['name']
            self.dbFactoryArg = args['dbFactroyArg']
            self.inputFormat = args['inputFormat']
            self.delimiter = args['delimiter']
            self.hasHeader = args['hasHeader']            
            #self.replaceEmptyFieldBy = args['replaceEmptyFieldBy']
            if not self.args.has_key('autoCommit'):
                self.autocommit = False
            #session pool
            self.session = None
            self.nbThreads = int(args['nbThreads'])
            if self.nbThreads == 0:
                self.nbThreads = 1
            if args.has_key('retries'):
                self.retries = int(args['retries'])
            else:
                self.retries = 5
            #self.curArgs = {}
            #self.curArgs['cursorName'] = 'cursor1'
            self.metadata = {}
            self.fieldNames = []
            self.fieldLength = []
            if self.inputFormat == 'delimited':
                if self.args.has_key('fieldNames'):
                    self.fieldNames = args['fieldNames']
            elif self.inputFormat == 'fixedLength':
                if self.args.has_key('fieldNames') and self.args.has_key('fieldLength'):
                    self.fieldNames = args['fieldNames']
                    self.fieldLength = args['fieldLength']
            #here, for multithread updating database, speed up here
            self.connection = dbFactory.dbFactory(args['dbFactroyArg'], self.logList)
            #for i in range(self.nbThreads):
            self.session = self.makeSession(self.connection)
            self.parallelize = 'n'
            self.nbQueriesParal = 10
            ########################################################
            #this is for future optimization, may not be needed
            if args.has_key('parallelize'):
                self.parallelize = args['parallelize']
            if args.has_key('nbQueriesParal'):
                self.nbQueriesParal = int(args['nbQueriesParal'])
        except KeyError:
            reticLog.logError(self.logList, "( " + self.name + " ) Error during SQLSink initialization")
            reticLog.logError(self.logList, "( " + self.name + " ) Parameter " + str(sys.exc_info()[1]) + " is missing in sink definition" )
            sys.exit(1)
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Unknown error during initialization in sink")
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            sys.exit(1)

    #make a database session for updating
    def makeSession(self,connection):
        sm = orm.sessionmaker(bind=connection.engine, autoflush=True, autocommit=self.autocommit,expire_on_commit=True)
        session = orm.scoped_session(sm)
        return session

    def getMsg (self, message):
        try:
            reticLog.logInfo(self.logList, "( " + self.name + " ) Retrieving message for sink : " + self.name)
            # Re-initialize msg to get new message
            self.msg = ''
            self.msg = message
            reticLog.logInfo(self.logList, "( " + self.name + " ) Message retrieved in sink : " + self.name)          
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Error during message retrieval in sink : " + self.name)
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            return 1                    

        
    def process (self):
        try:
            
            reticLog.logInfo(self.logList, "( " + self.name + " ) Message processed on sink : " + self.name)
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Error during message processing in sink : " + self.name)
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            return 1                    

    
# ============================================================= #
#
#      Private methods (optional) 
#
# ============================================================= #


    def getRecordList(self):
        # Extraction of the fields and values to map to the SQL statement.
        # The method returns a list of dictionnaries 
        reticLog.logInfo(self.logList, "( " + self.name + " ) getRecordList Start")        
        msg = StringIO.StringIO()
        msg.write(self.msg)
        #print raw_input('msg here...')
        #print msg
        msg.seek(0)
        recordList = []
        msgFormat = ''
        xmlRoot = None
        if self.metadata.has_key(msgFormat) : 
            if self.metadata['msgFormat'] == 'xml':
                xmlRoot = ElementTree(msg) 
                msgFormat = 'xml'
            else:
                msgFormat = 'flat'        
                

        if msgFormat == '':
            try:
                xmlRoot = ElementTree(file=msg)
                msgFormat = 'xml'
            except:
                msgFormat = 'flat'

        reticLog.logDebug(self.logList, "Input format detected :  " + msgFormat)
        # I am here
        if msgFormat == 'xml':
            recNb = 0
            #Create an iterator
            iter = xmlRoot.getiterator()
            #traverse the xml tree
            for element in iter:
                if element.getchildren():
                    for child in element.getchildren():
                        prepRecord = {}
                        if child.getchildren():
                            for subChild in child.getchildren():
                                if subChild.text == '-999':
                                    continue
                                prepRecord[subChild.tag] = subChild.text
                            recordList.append(prepRecord)                
            reticLog.logDebug(self.logList, "All records processed.")
        #here for processing flat file
        elif msgFormat == 'flat':
            raise Exception('Do not support flat file at this time')
                
        reticLog.logInfo(self.logList, "( " + self.name + " ) getRecordList End")                                
        return recordList

        
    def prepareUpdateObject(self, recordList,processInfo,firstTimeImport=True):
        reticLog.logInfo(self.logList, "( " + self.name + " ) prepareUpdateObject Start")                                
        #object list, to be add to session/real database
        objects = []
        for record in recordList:
            result = processInfo(record)
            for ob in result:
                objects.append(ob)        
            #objects.append(tempSQL)
            #reticLog.logDebug(self.logList, "SQL generated : " + tempSQL)    
        reticLog.logInfo(self.logList, "( " + self.name + " ) prepareUpdateObject End")
        #this is for TWDB data, twdb specific
        #Initialize the first ValueID
        if firstTimeImport:
            objects[0].ValueID = 0
        else:
            #get the max id
            column = testTWDBmodel.DataValues.ValueID.property.columns[0]
            seq = column.sequence
            maxid = self.session.query(func.max(column))
            objects[0].ValueID = maxid + 1
        return objects

        
    def executeThreadedStatements (self, statements, threadNumber):
        pass
        
    def updateDB(self, objects):
        reticLog.logInfo(self.logList, "( " + self.name + " ) Starting update objects from sink : " + self.name)
        count = 0
        for ob in objects :
#           print "Executing SQL : " + statement
            retries = self.retries
            execOk = 0
            if count > 0:
                ob.ValueID = self.getMaxId()
            while retries >= 0 and execOk == 0:
                try:
                    ############
                    self.session.add(ob)
                    self.session.flush()
                    print "recordNo == >", ob.ValueID, "generated"
                    count = count+1
                    execOk = 1
                #this is the handler for some violation of unique constriant on keys
                except exc.OperationalError:
                    print "DB constraint violation happen"
                    self.session.rollback()
                    continue
                    #execOk = 0
                   # retries = retries - 1
                #this is the handler ofr invalid request error
                except exc.InvalidRequestError:
                    print "DB constraint violation happen"
                    self.session.rollback()
                    continue
                #raise
                if execOk == 0 and retries < 0:
                    raise "Database Exception : all retries failed"
                elif execOk == 1:
    #               reticLog.logDebug(self.logList, "SQL executed : " + statement)    
                    try:
                       self.session.commit()
            ##            #self.session.close()
                       #reticLog.logInfo(self.logList, "( " + self.name + " ) Update commited")                    
                    except:
                        self.session.rollback()
                        #self.session.close()
                        reticLog.logWarning(self.logList, "Commit Failed in SQLSink")
                else:
                    errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                    reticLog.logWarning(self.logList, "Database Update failed : " + errorMessage)
        reticLog.logInfo(self.logList, "( " + self.name + " ) Number DB record  (%d) added : " % count + self.name) 
        reticLog.logInfo(self.logList, "( " + self.name + " ) Update of Databases ended in sink : " + self.name)
        #self.session.commit()

##        try:            
##            self.session.commit()
##            #self.session.close()
##            reticLog.logInfo(self.logList, "( " + self.name + " ) Update commited")                    
##        except:
##            self.session.rollback()
##            #self.session.close()
##            reticLog.logWarning(self.logList, "Commit Failed in SQLSink")
        
    def getMaxId(self):
        #get the max id
        column = testTWDBmodel.DataValues.ValueID.property.columns[0]
        #bind sequence with current session
        maxid = self.session.query(func.max(column)).one()[0]
        return maxid+1
        

if __name__ == '__main__':
    print 'here'
