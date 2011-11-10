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
import dbFactory
#orm = Object Relation Mapping
from sqlalchemy import orm,exc,func,and_
from sqlalchemy.orm.exc import NoResultFound
#processing xml file
from xml.etree.ElementTree import *
from testTPWDmodel import major_area_str,minor_bay_str,station_str
import testTPWDmodel


TPWDSitesDict = {
                 'aransas':u'Aransas',
                 #'CedarL':u'Cedar Lakes',
                 'corpuschristi': u'Corpus Christi',
                 'eastmatagorda': u'East Matagorda',
                 'matagorda': u'Matagorda',
                 'galveston':u'Galveston',
                 'gulf':u'gulf offshore',
                 'lowerlagunamadre':u'Lower Laguna Madre',
                 'upperlagunamadre':u'Upper Laguna Madre',
                 'sabine':u'Sabine',
                 'sanantonio':u'San Antonio'                
                 }



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
            #self.args['cursorName'] = "cursor"
            #args['cursorName'] = "cursor"
            #here, for multithread updating database, speed up here
            self.connection = dbFactory.dbFactory(args['dbFactroyArg'], self.logList)
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

        
    #before insert actual datavalue, process the sites/geographic infomation first
    def processSites (self,recordList,sitesName):
        try:
            for record in recordList:
                sites_exist = None
                try:
                    where = and_(testTPWDmodel.Sites.Latitude==record['start_latitude_num'], 
                             testTPWDmodel.Sites.Longitude==record['start_longitude_num'])
                    sites_exist = self.session.query(testTPWDmodel.Sites).filter(where).one()
                except NoResultFound, e:
                    newSite = testTPWDmodel.Sites()
                    newSite.SiteID = self.getMaxId('Sites')
#                    mkey = md5.new()
#                    mkey.update(str(record['start_latitude_num'])+str(record['start_longitude_num']))
#                    mStr = mkey.hexdigest()
                    SiteCode_I = ''.join([major_area_str,record['major_area_code'],
                            minor_bay_str,record['minor_bay_code'],
                            station_str,record['station_code']])
                    newSite.SiteCode = unicode('_'.join([SiteCode_I,str(newSite.SiteID)]))
                    #here, changing to name-looking function later
                    #sites name is based on the csv file name processed 
                    newSite.SiteName = TPWDSitesDict[sitesName.split('_')[0]]
                    ###################################
                    newSite.Latitude,newSite.Longitude = float(record['start_latitude_num']),float(record['start_longitude_num'])
                    newSite.LatLongDatumID= 2
                    newSite.VerticalDatum = u'Unknown'
                    newSite.State = u'Texas'
                    self.session.add(newSite)
                    self.session.flush()
                    record['SiteID'] = newSite.SiteID
                else:
                    record['SiteID'] = sites_exist.SiteID
            self.session.commit()
            reticLog.logInfo(self.logList, "( " + self.name + " ) sites info processed on sink : " + self.name)
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "( " + self.name + " ) Error during Sites message processing in sink : " + self.name)
            reticLog.logError(self.logList, "( " + self.name + " ) " + errorMessage)
            return 1                    

    
# ============================================================= #
#
#      Private methods (optional) 
#
# ============================================================= #

    #transform the xml/flat/other format of file into a list of record(dictionary)
    #return type : a list of csv records to be inserted into database
    def getRecordList(self):
        """Extraction of the fields and values to map to the SQL statement.
        The method returns a list of dictionnaries""" 
        reticLog.logInfo(self.logList, "( " + self.name + " ) getRecordList Start")        
        msg = StringIO.StringIO()
        msg.write(self.msg)
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
                                prepRecord[subChild.tag] = subChild.text
                            recordList.append(prepRecord)                
            reticLog.logDebug(self.logList, "All records processed.")
        #here for processing flat file
        elif msgFormat == 'flat':
            raise Exception('Do not support flat file at this time')
                
        reticLog.logInfo(self.logList, "( " + self.name + " ) getRecordList End")                                
        return recordList

        
    def prepareUpdateObject(self, recordList,processInfo):
        reticLog.logInfo(self.logList, "( " + self.name + " ) prepareUpdateObject Start")                                
        #object list, to be add to session/real database
        objects = []
        for record in recordList:
            #here add sites name here for time stamp comparison            
            #not processed data, so we process here
            result = processInfo(record)
            for ob in result:
                objects.append(ob)            
        reticLog.logInfo(self.logList, "( " + self.name + " ) prepareUpdateObject End")
        print "%d data value objects generated" % len(objects)
        return objects

        
    def executeThreadedStatements (self, statements, threadNumber):
        pass
        
    def updateDB(self, objects):
        reticLog.logInfo(self.logList, "( " + self.name + " ) Starting update objects from sink : " + self.name)
        count = 0
        for ob in objects :
            retries = self.retries
            execOk = 0
            ob.ValueID = self.getMaxId('DV')
            try:
                where = and_(testTPWDmodel.DataValues.DataValue==ob.DataValue, 
                             testTPWDmodel.DataValues.LocalDateTime==ob.LocalDateTime,
                             testTPWDmodel.DataValues.SiteID==ob.SiteID,
                             testTPWDmodel.DataValues.VariableID==ob.VariableID)
                valueExist = self.session.query(testTPWDmodel.DataValues).filter(where).one()
            #this record does not exist,insert it
            except NoResultFound, e:
                while retries >= 0 and execOk == 0:
                    try:
                        ############
                        self.session.add(ob)
                        self.session.flush()
                        execOk = 1
                    #this is the handler for some violation of unique constriant on keys
                    except exc.OperationalError:
                        print "DB constraint violation happen"
                        self.session.rollback()
                        continue
                        #execOk = 0
                       # retries = retries - 1
                    #this is the handler or invalid request error
                    except exc.InvalidRequestError:
                        print "DB constraint violation happen"
                        self.session.rollback()
                        continue
                    #raise
                    if execOk == 0 and retries < 0:
                        raise "Database Exception : all retries failed"
                    elif execOk == 1:
                        print "recordNo == >", ob.ValueID, "generated"
                        count += 1
                    else:
                        errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                        reticLog.logWarning(self.logList, "Database Update failed : " + errorMessage)
            #this record exists, skip it
            else:
                print "record skipped"
                continue
            #end big for loop
        reticLog.logInfo(self.logList, "( " + self.name + " ) Number DB record  (%d) added : " % count + self.name) 
        reticLog.logInfo(self.logList, "( " + self.name + " ) Update of Databases ended in sink : " + self.name)
        #
        #unit of work pattern, only commit one time
        try:                                            
            self.session.commit()
            #self.session.close()
            reticLog.logInfo(self.logList, "( " + self.name + " ) Update commited")                    
        except:
            self.session.rollback()
            #self.session.close()
            reticLog.logWarning(self.logList, "Commit Failed in SQLSink")
        
    def getMaxId(self,tabFlag):
        maxid = 0
        if tabFlag == 'Sites':
            try:
                column = testTPWDmodel.Sites.SiteID.property.columns[0]
                maxid = (self.session.query(func.max(column)).one()[0]) + 1
            except Exception:
                pass
        elif tabFlag == 'DV':
            try:
                column = testTPWDmodel.DataValues.ValueID.property.columns[0]
                maxid = (self.session.query(func.max(column)).one()[0]) + 1
            except Exception:
                pass
        return maxid

if __name__ == '__main__':
    import time
    #place starting time stub
    start = time.clock()
    print 'testing sink....'
    config = ["..\\testAdaptor_config\\logParam.xml","..\\testAdaptor_config\\sinkParam.xml"]
    #get log config parameter dictionary 
    log_args = get_conf_attr(config[0])
    #logList parameter, parameter for source, pipe and sink
    logList = []
    #initialize log(s) according to parameters.
    for attDict in log_args:
         reticLog.addLogger(logList,attDict)
    #initialize sink 
    sink_args = get_conf_attr(config[1],'sink')   #get sink parameters
    testSink = sink(sink_args,logList)            #actual initialization
    #get the message, here we get the "dummy message" from an xml file for test purposes
    dummyPipe = file('..\\pipes\\test_TPWD_Emat_out.xml','r')  
    testSink.getMsg(dummyPipe.read())
    recordList = testSink.getRecordList()
    raw_input(str(len(recordList))+" XML records"+' generated')
    testSink.processSites(recordList)
    print "yeah, sites info processed......"
    updateList = testSink.prepareUpdateObject(recordList,testTPWDmodel.tpwdProcessInfo)
    print raw_input(str(len(updateList))+" database records"+' to be inserted')
    testSink.updateDB(updateList)
    #end time stub
    elapsed_time = time.clock() - start
    print "time elapsed: ",elapsed_time
