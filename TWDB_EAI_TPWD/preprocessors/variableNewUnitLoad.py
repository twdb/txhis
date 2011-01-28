'''
Created on Jul 7, 2010

@author: CTtan
'''
from sqlalchemy import orm, schema, types, create_engine,exc,func,and_
from sqlalchemy.orm.exc import NoResultFound
from StringIO import StringIO
import utility_EAI.twdbEaiLog as reticLog
import sys,traceback

usr = "AppHisTceqSwqmisUser"
#usr = 'sa'
pw  = "A99!5wqm1s"
#pw = '12345678a'
datasource = "sqltest/HisTceqSwqmis"
#datasource = "localhost:3108/OD_TCEQ"

#new Unit list specific for TCEQ
newUnitList = [
    ['milligram per kilogram','Concentration','mg/kg'],
    ['gram per square meter','Concentration','g/m2'],
    ['gram per kilogram','Concentration','g/kg'],
    ['microgram per kilogram','Concentration','ug/kg'],
    ['milligram per gram','Concentration','mg/g'],
    ['nanogram per kilogram','Concentration','ng/kg'],
    ['nanogram per gram','Concentration','ng/g'],
    ['microgram per square centimeter','Concentration','ug/cm2'],
    ['microgram per gram','Concentration','ug/g'],
    ['milliogram per square centimeter','Concentration','mg/cm2'],
    ['meters per kilometer','Scale','m/km'],
    ['feet per foot','Scale','ft/ft'],
    ['number of organisms per gram','Organism Concentration','#/g'],   
    ['number of organisms per sample','Organism Concentration','#/sample'],
    ['number per milliliter','Organism Concentration','#/ml'],
    ['number of organisms per square feet','Organism Concentration','#/ft2'],
    ['picocuries per liter','Radiation Concentration','PCI/L']
               ]

#variableName table class
class Units(object):
    def __init__(self,name,type,abbre):
        self.UnitsName = name
        self.UnitsType = type
        self.UnitsAbbreviation = abbre
        
# initialize database connection, map database table to python class, and return a session object
def initDB():
    engine = create_engine('mssql://%s:%s@%s'%(usr,pw,datasource),module_name='pyodbc')
    metadata = schema.MetaData()
    metadata.bind = engine   
    #offsets table
    Units_table = schema.Table('Units',metadata,     \
                                    autoload=True,autoload_with=engine)
    orm.mapper(Units,Units_table)
    # create session
    sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, \
                          expire_on_commit=True)
    return orm.scoped_session(sm)

def getMaxId(session):
    maxid = 0
    try:
        column = Units.UnitsID.property.columns[0]
        maxid = (session.query(func.max(column)).one()[0]) + 1
    except Exception:
        pass
    return maxid

if __name__ == "__main__":
    dbSession = initDB()
    print "Initialize Database connection compelete..."
    for record in newUnitList:
        try: 
            where = and_(Units.UnitsName == record[0],Units.UnitsType == record[1],Units.UnitsAbbreviation == record[2])
            valueExist = dbSession.query(Units).filter(where).one()
            print "find record with UnitsName: %s in database, skip it..." % record[0]
            continue
        #this variable record does not exist, so insert it
        except NoResultFound, e:
            # This is for system robust
            # retries is max number of insertion times, and execOk is to show whether update is successful
            retries,execOk = 5,0                
            newUnitRecord = Units(record[0],record[1],record[2])
            while retries >= 0 and execOk == 0:
                try:
                    ############
                    newUnitRecord.UnitsID = getMaxId(dbSession)
                    dbSession.add(newUnitRecord)
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
                    print "inert new Unit record with UnitName ==> %s" % newUnitRecord.UnitsName
                else:
                    errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
                    print errorMessage
    #unit of work pattern, only commit one time
    try:                                            
        dbSession.commit()                    
    except:
        dbSession.rollback()
    print "New Unit record(s) insert Compelete..."
    