#This script load sites and variables to ODM database first
from sqlalchemy import orm, schema, types, create_engine,exc,func,and_
from sqlalchemy.orm.exc import NoResultFound
import sys
sys.path.append("..")
from sources import HTTPSource
from StringIO import StringIO
from utility_EAI.TCEQUnitsMapping import unitsMap,mediaMapping
import utility_EAI.twdbEaiLog as reticLog
import csv,sys,traceback

usr = "AppHisTceqSwqmisUser"
#usr = 'sa'
pw  = "A99!5wqm1s"
#pw = '12345678a'
datasource = "sqltest/HisTceqSwqmis"
#datasource = "localhost:3108/OD_TCEQ"

#metadata description for station list file 
SITECODE = 1
SITENAME = 4
LATITUDE,LONGITUDE = 11,12
COUNTY = 7
HUC,TYPE1,TYPE2 = 13,5,6
#metadata description for variable list file
VARCODE = 0
VARNAME = 1
VARUNITS = 2
MEDIA = 3
METHOD = 4


#Variables class  --> object
class Variables(object):
    def __init__(self,VariableCode,VariableName,VariableUnitsID,SampleMedium,
                 ValueType = "Unknown",Speciation = "Not Applicable", IsRegular = False, TimeSupport = 0,
                   TimeUnitsID = 103, DataType = "Unknown", GeneralCategory = "Water Quality",
                   NoDataValue = float(-9999) ):
        self.VariableCode = VariableCode
        self.VariableName = VariableName
        self.Speciation = Speciation
        self.VariableUnitsID = VariableUnitsID
        self.SampleMedium = SampleMedium
        self.ValueType = ValueType
        self.IsRegular = IsRegular
        self.TimeSupport = TimeSupport
        self.TimeUnitsID = TimeUnitsID
        self.DataType = DataType
        self.GeneralCategory = GeneralCategory
        self.NoDataValue = NoDataValue


#Sites class --> object
class Sites(object):
    def __init__(self,siteCode,siteName,lat,long,county,comments,latlongDatum=2, state="Texas"):
        self.SiteCode = siteCode
        self.SiteName = siteName
        self.Latitude,self.Longitude = lat,long
        self.LatLongDatumID = latlongDatum
        self.State,self.County = state,county
        self.comment = comments

# initialize database connection, map database table to python class, and return a session object
def initDB():
    engine = create_engine('mssql://%s:%s@%s'%(usr,pw,datasource),module_name='pyodbc')
    metadata = schema.MetaData()
    metadata.bind = engine
    #map database table/records to python class
    #datavalues table
    Variables_table = schema.Table('Variables',metadata,  \
                                    autoload=True,autoload_with=engine)
    orm.mapper(Variables,Variables_table)
    #offsets table
    Sites_table = schema.Table('Sites',metadata,     \
                                    autoload=True,autoload_with=engine)
    orm.mapper(Sites,Sites_table)
    # create session
    sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, \
                          expire_on_commit=True)
    return orm.scoped_session(sm)

# function to get the maxID (the primary key) of different kinds of tables
def getMaxId(session,tabFlag):
        maxid = 0
        if tabFlag == 'Sites':
            try:
                column = Sites.SiteID.property.columns[0]
                maxid = (session.query(func.max(column)).one()[0]) + 1
            except Exception:
                pass
        elif tabFlag == 'Variables':
            try:
                column = Variables.VariableID.property.columns[0]
                maxid = (session.query(func.max(column)).one()[0]) + 1
            except Exception:
                pass
        return maxid

# main routine
def main():
    session = initDB()
    #logger setup. Here, simply set a consloe logger
    logAttDic = {'name': 'TCEQ sites and parameters importing for the first time',
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'ConsoleAppender'}
    logList = []
    reticLog.addLogger(logList,logAttDic)
    #get sites list (a text file) from an HTTPSource
    # and insert all the sites into the "Sites" table of ODM database
    siteSrc_args = {}
    siteSrc_args['name'] = "TCEQ sites httpsource"
    siteSrc_args['URL'] = "ftp://ftp.tceq.state.tx.us/pub/WaterResourceManagement/WaterQuality/DataCollection/CleanRivers/public/stations.txt"
    sitesHTTPSource = HTTPSource.source(siteSrc_args,logList)
    sitesHTTPSource.start()
    while(sitesHTTPSource.next()==1):
        print "Content of this URL:  %s" % sitesHTTPSource.URL
        sitesFile = StringIO(sitesHTTPSource.msg[0])
        sitesListReader = csv.reader(sitesFile, delimiter='|')
        for index,row in enumerate(sitesListReader):
            if index == 0:
                continue
            try:
                newRecordSiteName = row[SITENAME] if len(row[SITENAME]) <= 255 else row[SITENAME][0:255]
                where = and_(Sites.SiteCode == unicode(row[SITECODE])
                              ,Sites.Latitude == float(row[LATITUDE])
                              ,Sites.Longitude == float(row[LONGITUDE]))
                valueExist = session.query(Sites).filter(where).one()
                print "find record with SiteCode %s in database, skip it..." % row[SITECODE]
                continue
            #this site record does not exist, so insert it
            except NoResultFound, e:
                # This is for system robust
                # retries is max number of insertion times, and execOk is to show whether update is successful
                retries,execOk = 5,0                
                newSiteRecord = Sites(row[SITECODE],newRecordSiteName,
                                      float(row[LATITUDE]),float(row[LONGITUDE]),row[COUNTY], \
                                      ";".join(["HUC 8 = ",row[HUC],"EPA_Type1 = ",row[TYPE1],"EPA_Type2 = ",row[TYPE2]]))
                while retries >= 0 and execOk == 0:
                    try:
                        ############
                        newSiteRecord.SiteID = getMaxId(session,"Sites")
                        session.add(newSiteRecord)
                        session.flush()
                        execOk = 1
                    #this is the handler for some violation of unique constriant on keys
                    except exc.OperationalError:
                        print "DB constraint violation happen"
                        session.rollback()
                        retries = retries - 1
                        continue
                    #this is the handler or invalid request error
                    except exc.InvalidRequestError:
                        print "DB constraint violation happen"
                        session.rollback()
                        retries = retries - 1
                        continue
                if execOk == 0 and retries < 0:
                    raise "Database Exception : all retries failed"
                elif execOk == 1:
                    print "inert new Site record with SiteCode ==> %s" % row[SITECODE]
                else:
                    errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                    reticLog.logWarning(logList, "Sites Table in Database Update failed : " + errorMessage)
        #unit of work pattern, only commit one time
        try:                                            
            session.commit()
            reticLog.logInfo(logList, "( " + "TCEQ Sites" + " ) Update commited")                    
        except:
            session.rollback()
            reticLog.logWarning(logList, "Commit Failed in SQLSink")
        sitesHTTPSource.commit()
    sitesHTTPSource.commit()
    #get Variables list (a text file) from an HTTPSource
    # and insert all the parameters into the "Variables" table of ODM database
#    varSrc_args = {}
#    varSrc_args['name'] = "TCEQ Variables httpsource"
#    varSrc_args['URL'] = "ftp://ftp.tceq.state.tx.us/pub/WaterResourceManagement/WaterQuality/DataCollection/CleanRivers/public/sw_parm_format.txt"
#    varHTTPSource = HTTPSource.source(varSrc_args,logList)
#    varHTTPSource.start()
#    while(varHTTPSource.next()==1):
#        raw_input("Content of this URL:  %s" % varHTTPSource.URL)
#        variablesListFile = StringIO(varHTTPSource.msg[0])
#        variablesListReader = csv.reader(variablesListFile, delimiter='|')
#        import anydbm
#        varMethodfile = anydbm.open(".//additionalInfo/varMethod.vmdb",'c')
#        for index,row in enumerate(variablesListReader):
#            if index == 0:
#                continue
#            try:
#                newRecordVarName = row[VARNAME]
#                ##here, we need to store "Variable(code), method" mapping info in a file for future usage.
#                #print "here, for anydbm..."
#                varMethodfile[row[VARCODE]] = row[METHOD] 
#                where = and_(Variables.VariableCode == row[VARCODE],Variables.VariableName == newRecordVarName)
#                valueExist = session.query(Variables).filter(where).one()
#                print "find record with VariableCode %s in database, skip it..." % row[VARCODE]
#                continue
#             #this variable record does not exist, so insert it
#            except NoResultFound, e:
#                # This is for system robust
#                # retries is max number of insertion times, and execOk is to show whether update is successful
#                retries,execOk = 5,0                
#                newVarRecord = Variables(row[VARCODE],newRecordVarName,unitsMap[row[VARUNITS]],mediaMapping[row[MEDIA]])
#                while retries >= 0 and execOk == 0:
#                    try:
#                        ############
#                        newVarRecord.VariableID = getMaxId(session,"Variables")
#                        session.add(newVarRecord)
#                        session.flush()
#                        execOk = 1
#                    #this is the handler for some violation of unique constriant on keys
#                    except exc.OperationalError:
#                        print "DB constraint violation happen"
#                        session.rollback()
#                        retries = retries - 1
#                        continue
#                    #this is the handler or invalid request error
#                    except exc.InvalidRequestError:
#                        print "DB constraint violation happen"
#                        session.rollback()
#                        retries = retries - 1
#                        continue
#                if execOk == 0 and retries < 0:
#                    raise "Database Exception : all retries failed"
#                elif execOk == 1:
#                    print "inert new Variable record with VariableCode ==> %s" % row[VARCODE]
#                else:
#                    errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
#                    reticLog.logWarning(logList, "Variables Table in Database Update failed : " + errorMessage)
#        #unit of work pattern, only commit one time
#        try:                                            
#            session.commit()
#            reticLog.logInfo(logList, "( " + "TCEQ Variables" + " ) Update commited")                    
#        except:
#            session.rollback()
#            reticLog.logWarning(logList, "Commit Failed in SQLSink")
#            #print ','.join(row)
#        varHTTPSource.commit()
#    varMethodfile.close()
#    varHTTPSource.commit()

if __name__ == "__main__":
    main()
    print "processing TCEQ sites list from HTTP source complete......"
    