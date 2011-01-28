from sqlalchemy import orm, schema, types, create_engine,exc,func,and_
from sqlalchemy.orm.exc import NoResultFound
import sys
sys.path.append("..")
from sources import HTTPSource
from StringIO import StringIO
import utility_EAI.twdbEaiLog as reticLog
import csv,sys,traceback

VARNAME = 1
METHOD = 4

usr = "AppHisTceqSwqmisUser"
#usr = 'sa'
pw  = "A99!5wqm1s"
#pw = '12345678a'
datasource = "sqltest/HisTceqSwqmis"
#datasource = "localhost:3108/OD_TCEQ"

#variableName table class
class VariableNameCV(object):
    def __init__(self,Term,Definition):
        self.Term = Term
        self.Definition = Definition
        
class Methods(object):
    def __init__(self,MethodID,MethodDescription,MethodLink = None):
        self.MethodID = MethodID
        self.MethodDescription = MethodDescription
        self.MethodLink = MethodLink

# initialize database connection, map database table to python class, and return a session object
def initDB():
    engine = create_engine('mssql://%s:%s@%s'%(usr,pw,datasource),module_name='pyodbc')
    metadata = schema.MetaData()
    metadata.bind = engine   
    #offsets table
    VariableNamceCV_table = schema.Table('VariableNameCV',metadata,     \
                                    autoload=True,autoload_with=engine)
    orm.mapper(VariableNameCV,VariableNamceCV_table)
    Methods_table = schema.Table('Methods',metadata,     \
                                    autoload=True,autoload_with=engine)
    orm.mapper(Methods,Methods_table)
    # create session
    sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, \
                          expire_on_commit=True)
    return orm.scoped_session(sm)

def getMaxId(session):
        maxid = 0
        try:
            column = Methods.MethodID.property.columns[0]
            maxid = (session.query(func.max(column)).one()[0]) + 1
        except Exception:
            pass
        return maxid

if __name__ == "__main__":
    dbSession = initDB()
    thingsList = []
    #logger setup. Here, simply set a consloe logger
    logAttDic = {'name': 'TCEQ sites and parameters importing for the first time',
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'ConsoleAppender'}
    logList = []
    reticLog.addLogger(logList,logAttDic)
    #insert variable names for TCEQ data
    varSrc_args = {}
    varSrc_args['name'] = "TCEQ Variables httpsource"
    varSrc_args['URL'] = "ftp://ftp.tceq.state.tx.us/pub/WaterResourceManagement/WaterQuality/DataCollection/CleanRivers/public/sw_parm_format.txt"
    varHTTPSource = HTTPSource.source(varSrc_args,logList)
    varHTTPSource.start()
    count = 0
    while(varHTTPSource.next()==1):
        raw_input("Content of this URL:  %s" % varHTTPSource.URL)
        variablesListFile = StringIO(varHTTPSource.msg[0])
        variablesListReader = csv.reader(variablesListFile, delimiter='|')
        for index,row in enumerate(variablesListReader):
            if index == 0:
                continue
            try:
                where = and_(VariableNameCV.Term == row[VARNAME],VariableNameCV.Definition == row[VARNAME])
                valueExist = dbSession.query(VariableNameCV).filter(where).one()
                print "find record with Varible name %s in database, skip it..." % row[VARNAME]
                continue
            #this site record does not exist, so insert it
            except NoResultFound, e:
                # This is for system robust
                # retries is max number of insertion times, and execOk is to show whether update is successful
                retries,execOk = 5,0                
                newVarNameCVReocrd = VariableNameCV(row[VARNAME],row[VARNAME])
                while retries >= 0 and execOk == 0:
                    try:
                        ############
                        dbSession.add(newVarNameCVReocrd)
                        dbSession.flush()
                        execOk = 1
                    #this is the handler for some violation of unique constriant on keys
                    except exc.OperationalError:
                        print "DB constraint violation happen"
                        dbSession.rollback()
                        retries = retries - 1
                        continue
                    #this is the handler or invalid request error
                    except exc.InvalidRequestError:
                        print "DB constraint violation happen"
                        dbSession.rollback()
                        retries = retries - 1
                        continue
                if execOk == 0 and retries < 0:
                    raise "Database Exception : all retries failed"
                elif execOk == 1:
                    print "inert new VariableCV record with variableName ==> %s" % row[VARNAME]
                else:
                    errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                    reticLog.logWarning(logList, "VariableNameCV Table in Database Update failed : " + errorMessage)
        #unit of work pattern, only commit one time
        try:                                            
            dbSession.commit()
            reticLog.logInfo(logList, "( " + "VariableNameCV" + " ) Update commited")                    
        except:
            dbSession.rollback()
            reticLog.logWarning(logList, "Commit Failed in SQLSink")
        varHTTPSource.commit()
    varHTTPSource.commit()
    #########################another fetch, for Methods
    #get Methods Data
    methodsHTTPSource = HTTPSource.source(varSrc_args,logList)
    methodsHTTPSource.start()
    while(methodsHTTPSource.next()==1):
        raw_input("Content of this URL:  %s" % methodsHTTPSource.URL)
        variablesListFile = StringIO(methodsHTTPSource.msg[0])
        variablesListReader = csv.reader(variablesListFile, delimiter='|')
        for index,row in enumerate(variablesListReader):
            if index == 0:
                continue
            try:
                where = and_(Methods.MethodDescription == row[METHOD])
                valueExist = dbSession.query(Methods).filter(where).one()
                print "find record with method description %s in database, skip it..." % row[METHOD]
                continue
            #this site record does not exist, so insert it
            except NoResultFound, e:
                # This is for system robust
                # retries is max number of insertion times, and execOk is to show whether update is successful
                retries,execOk = 5,0                
                newMethodReocrd = Methods(getMaxId(dbSession),row[METHOD])
                while retries >= 0 and execOk == 0:
                    try:
                        ############
                        dbSession.add(newMethodReocrd)
                        dbSession.flush()
                        execOk = 1
                    #this is the handler for some violation of unique constriant on keys
                    except exc.OperationalError:
                        print "DB constraint violation happen"
                        dbSession.rollback()
                        retries = retries - 1
                        continue
                    #this is the handler or invalid request error
                    except exc.InvalidRequestError:
                        print "DB constraint violation happen"
                        dbSession.rollback()
                        retries = retries - 1
                        continue
                if execOk == 0 and retries < 0:
                    raise "Database Exception : all retries failed"
                elif execOk == 1:
                    print "inert new methods record with description ==> %s" % row[METHOD]
                else:
                    errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                    reticLog.logWarning(logList, "Methods Table in Database Update failed : " + errorMessage)
        #unit of work pattern, only commit one time
        try:                                            
            dbSession.commit()
            reticLog.logInfo(logList, "( " + "Method" + " ) Update commited")                    
        except:
            dbSession.rollback()
            reticLog.logWarning(logList, "Commit Failed in SQLSink")
        methodsHTTPSource.commit()
    methodsHTTPSource.commit()