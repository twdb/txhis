#=========================================================================
#
# Python Source File
#
# NAME: fileSink.py
#
# AUTHOR: ADI
# DATE  : 1/27/2010
#
# COMMENT: 
#
#=========================================================================

import os, sys, string, StringIO, math, traceback, time,md5
#from pyxml import *
from threading import *

sys.path.append('..')
sys.path.append('../pipes')
sys.path.append('../sources')
sys.path.append('../sinks')

#from multithreads import *
import utility_EAI.twdbEaiLog as reticLog
from utility_EAI.twdbEaiUtil import get_conf_attr 
#orm = Object Relation Mapping
from sqlalchemy import orm,exc,schema, types,func,and_
from sqlalchemy.orm.exc import NoResultFound
#processing xml file
from xml.etree.ElementTree import *
import dbFactory
import csv
#code for TCEQ file types from the SDQ site
EVENT = "1"
RESULT = "2"
#code for TCEQ csv-alike list:
EVENT_IN_HASHTable = 0
RESULT_IN_HASHTable = 1
#column information for Result and Event type of file
RFATAG_COLUMN = 0
#for EVENT file:
SITECODE = 1
DATE = 2
TIME = 3
OFFSETDEPTH = 4
#for RESULT file:
VARIABLECODE = 2
VALUE = 4

#DataValues class
class DataValues(object):
    def __init__(self,ValueID,DataValue,LocalDateTime,SiteID,VariableID,OffsetValue,MethodID,\
                   OffsetTypeID=1,CensorCode=u'nc',UTCOffset=-6,SourceID=1,QualityControlLevelID=1):
        import datetime
        self.ValueID = ValueID
        self.DataValue = DataValue
        self.LocalDateTime = LocalDateTime
        self.UTCOffset = UTCOffset
        self.DateTimeUTC = LocalDateTime + datetime.timedelta(hours=UTCOffset)
        self.SiteID = SiteID
        self.VariableID = VariableID
        self.OffsetValue = OffsetValue
        self.OffsetTypeID = OffsetTypeID
        self.CensorCode = CensorCode
        self.MethodID = MethodID
        self.SourceID = SourceID
        self.QualityControlLevelID = QualityControlLevelID
        
#Sites class --
class Sites(object):
    pass

#Variable class --
class Variables(object):
    pass

#Method class --
class Methods(object):
    pass

class TCEQRecordNotFoundError(Exception):
     def __str__(self):
         return "%s with %sCode: %s Not Found! Maybe need to Update TCEQ Database..." % (self.type,self.type,self.value)

class SiteNotFoundError(TCEQRecordNotFoundError):
    def __init__(self,value,type="Sites"):
        self.value = value
        self.type = type
        
class VariableNotFoundError(TCEQRecordNotFoundError):
    def __init__(self,value,type="Variables"):
        self.value = value
        self.type = type
        
class MethodNotFoundError(TCEQRecordNotFoundError):
    def __init__(self,value,type="Methods"):
        self.value = value
        self.type = type


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
            self.connection = dbFactory.dbFactory(args['dbFactroyArg'], self.logList)
            # map DataValue table in ODM database to DataValue python class
            # to utilize the magic power of sqlalchemy
            metadata = schema.MetaData()
            metadata.bind = self.connection.engine
            DataValues_table = schema.Table('DataValues',metadata,  \
                                autoload=True,autoload_with=self.connection.engine)
            orm.mapper(DataValues,DataValues_table)
            Sites_table = schema.Table('Sites',metadata,  \
                                autoload=True,autoload_with=self.connection.engine)
            orm.mapper(Sites,Sites_table)
            Variables_table = schema.Table('Variables',metadata,  \
                                autoload=True,autoload_with=self.connection.engine)
            orm.mapper(Variables,Variables_table)
            Methods_table = schema.Table('Methods',metadata,  \
                                autoload=True,autoload_with=self.connection.engine)
            orm.mapper(Methods,Methods_table)
            #for i in range(self.nbThreads):
            self.session = self.makeSession(self.connection)
            self.parallelize = 'n'
            self.nbQueriesParal = 10
            ########################################################
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
    
    #get message from pipe, get message ready for further processing
    def getMsg (self, messages):
        """
        for TCEQ, every time, it passes in 2 message StringIO object, one for event, another for result
        """
        try:
            reticLog.logInfo(self.logList, "( " + self.name + " ) Retrieving message for sink : " + self.name)
            # Re-initialize msg to get new message
            # eventString IO is message[0], resultStringIO is messag[1]
            # get a mini hash table for each segment:
            # key: RFA tag id, 
            # value: [event list, result list]
            self.basinSegmentInfo = {}       
            eventCSVList = csv.reader(messages[0],delimiter="|")
            resultCSVLIst = csv.reader(messages[1],delimiter="|")     
#            raw_input("print event...")
#            for row in eventCSVList:
#                print row
#            raw_input("print result...")
#            for row in resultCSVLIst:
#                print row
            for row in eventCSVList:
                #this is for basiID 6, year 2010
                if (row[0] == "" and row[1] == "" and row[2] == ""):
                    row = row[3:]
                    print row
                self.basinSegmentInfo[row[RFATAG_COLUMN]] = {}
                self.basinSegmentInfo[row[RFATAG_COLUMN]][EVENT_IN_HASHTable] = row
            for row in resultCSVLIst: 
                if self.basinSegmentInfo[row[RFATAG_COLUMN]].has_key(RESULT_IN_HASHTable):
                    self.basinSegmentInfo[row[RFATAG_COLUMN]][RESULT_IN_HASHTable].append(row)    
                else:
                    #if this is the first result row for this RFATAG
                    self.basinSegmentInfo[row[RFATAG_COLUMN]][RESULT_IN_HASHTable] = [row]                    
#            resultCounter,eventCounter = 0,0
#            for key in self.basinSegmentInfo.keys():
#                #print "key => ",self.basinSegmentInfo[key]
#                eventCounter += 1
#                for resultRow in  self.basinSegmentInfo[key][RESULT_IN_HASHTable]:
#                    #print resultRow
#                    resultCounter += 1
#            #print "%d result in Total......" % eventCounter
#            print "%d result in Total......" % resultCounter
            reticLog.logInfo(self.logList, "( " + self.name + " ) Message retrieved in sink : " + self.name)          
            return 0
        except Exception, e:
            import traceback
            #if row[RFATAG_COLUMN] in self.basinSegmentInfo:
            #    print "In Dictionary Already!"
            #else:
            #    print "Not In Dictionary!"    
            traceback.print_exc(file=sys.stdout)
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Error during message retrieval in sink : " + self.name)
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            return 1                    
  
# ============================================================= #
#
#      Private methods (optional) 
#
# ============================================================= #
      
    def updateDB(self,methodLookUpfile):
        reticLog.logInfo(self.logList, "( " + self.name + " ) Starting update objects from sink : " + self.name)
        count = 0
        for key in self.basinSegmentInfo.keys():
            #need this because for some years (eg: 1973), there is no data collected in result file
            if self.basinSegmentInfo[key].has_key(RESULT_IN_HASHTable) and len(self.basinSegmentInfo[key][RESULT_IN_HASHTable]) >= VALUE : 
                for resultRow in self.basinSegmentInfo[key][RESULT_IN_HASHTable]:
                    retries = self.retries
                    execOk = 0
                    try:
                        import datetime
                        ValueID = self.getMaxId('DV')
                        DataValue = float(resultRow[VALUE])
                        LocalDateTime = datetime.datetime.strptime(" ".join([self.basinSegmentInfo[key][EVENT_IN_HASHTable][DATE],
                                                                             self.basinSegmentInfo[key][EVENT_IN_HASHTable][TIME]]), 
                                                                             "%m/%d/%Y %H:%M") 
                        SiteID = self.lookUpSite(self.basinSegmentInfo[key][EVENT_IN_HASHTable][SITECODE])
                        VariableID = self.lookUpVariableID(resultRow[VARIABLECODE])
                        if not self.basinSegmentInfo[key][EVENT_IN_HASHTable][OFFSETDEPTH] == "":
                            OffsetValue = float(self.basinSegmentInfo[key][EVENT_IN_HASHTable][OFFSETDEPTH])
                        else:
                            OffsetValue = float(-9999)
                        CensorCode = u'nc'
                        #find method id
                        import anydbm
                        methodDBMfile = anydbm.open(methodLookUpfile, 'r')
                        MethodDescription = methodDBMfile[resultRow[VARIABLECODE]] 
                        MethodID = self.lookUpMethodID(MethodDescription)
                        #for production databse:
                        #SourceID = 1 
                        where = and_(DataValues.DataValue == DataValue, 
                                     DataValues.LocalDateTime== LocalDateTime,
                                     DataValues.SiteID== SiteID,
                                     DataValues.VariableID == VariableID,
                                     DataValues.OffsetValue == OffsetValue,
                                     DataValues.MethodID == MethodID)
                        valueExist = self.session.query(DataValues).filter(where).one() 
                    #this DataValue record does not exist,insert it
                    except NoResultFound, e:
                        while retries >= 0 and execOk == 0:
                            try:
                                ############
                                newDataValueRecord = DataValues(ValueID,DataValue,LocalDateTime,SiteID,VariableID,OffsetValue,MethodID)
                                self.session.add(newDataValueRecord)
                                self.session.flush()
                                execOk = 1
                            #this is the handler for some violation of unique constriant on keys
                            except exc.OperationalError:
                                print "DB constraint violation happen"
                                self.session.rollback()
                                #execOk = 0
                               # retries = retries - 1
                            #this is the handler or invalid request error
                            except exc.InvalidRequestError:
                                print "DB constraint violation happen"
                                self.session.rollback()
                            #raise
                            if execOk == 0 and retries < 0:
                                raise "Database Exception : all retries failed"
                            elif execOk == 1:
                                print "recordNo == >", newDataValueRecord.ValueID, "generated"
                                count += 1
                            else:
                                errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                                reticLog.logWarning(self.logList, "Database Update failed : " + errorMessage)
                    except TCEQRecordNotFoundError, e:
                         errorMessage = str(e)
                         reticLog.logWarning(self.logList, "Database Update failed : " + errorMessage)                
                    #this record exists, skip it
                    except Exception, e:
                        traceback.print_exc(file=sys.stdout)
                        print resultRow
                        raise 
                    else:
                        print "record found, need to skip this record (may be wrong behavior....)"
            #end big for loop
        reticLog.logInfo(self.logList, "( " + self.name + " ) Number DB record  (%d) added : " % count + self.name) 
        reticLog.logInfo(self.logList, "( " + self.name + " ) Update of Databases ended in sink : " + self.name)
        #unit of work pattern, only commit one time
        try:                                            
            self.session.commit()
            #self.session.close()
            reticLog.logInfo(self.logList, "( " + self.name + " ) Update commited")                    
        except:
            self.session.rollback()
            #self.session.close()
            reticLog.logWarning(self.logList, "Commit Failed in SQLSink")
            
            
    #auto generate new record for new DataValues table record    
    def getMaxId(self,tabFlag):
        maxid = 0
        #for TCEQ, right now only need generate id generate DataValue
        if tabFlag == 'DV':
            try:
                column = DataValues.ValueID.property.columns[0]
                maxid = (self.session.query(func.max(column)).one()[0]) + 1
            except Exception:
                pass
        return maxid
    
    
    def lookUpSite(self,siteCode):
        import traceback
        try:
            where = and_(Sites.SiteCode == unicode(siteCode))
            existingSite = self.session.query(Sites).filter(where).one()
            return existingSite.SiteID
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            raise SiteNotFoundError(siteCode)
        
    def lookUpVariableID(self,VariableCode):
        import traceback
        try:
            where = and_(Variables.VariableCode == unicode(VariableCode))
            existingVariable = self.session.query(Variables).filter(where).one()
            return existingVariable.VariableID
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            raise VariableNotFoundError(VariableCode)
        
    def lookUpMethodID(self,MethodDescription):
        import traceback
        try:
            where = and_(Methods.MethodDescription == MethodDescription)
            existingVariable = self.session.query(Methods).filter(where).one()
            return existingVariable.MethodID
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            raise MethodNotFoundError(MethodDescription)

if __name__ == '__main__':
    import time
    pass
