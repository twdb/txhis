from ODMTPWDPrestProc import Sources,Variables
from sqlalchemy import schema,orm
from sqlalchemy.engine import create_engine

mydb = "HisTpwdCoastalwq"
#mydb = 'OD_TPWD'
user = 'AppHisTpwdCoastalwqUser'
#user = 'testaaa'
password = 'A99!tpwdcoa5t'
#password = '12345678a'

varSpe = [[1,u'TEM001',u'Temperature',u"Not Applicable",96,u'Surface Water',u'Unknown',False,0,103,u'Unknown',u'Unknown',float(-9999)],
          [2,u'SAL001',u'Salinity',   u"Not Applicable",306,u'Surface Water',u'Unknown',False,0,103,u'Unknown',u'Unknown',float(-9999)],
          [3,u'TUR001',u'Turbidity',  u"Not Applicable",221,u'Surface Water',u'Unknown',False,0,103,u'Unknown',u'Unknown',float(-9999)],
          [4,u'OXY001',u'Oxygen, dissolved',u"Not Applicable",199,u'Surface Water',u'Unknown',False,0,103,u'Unknown',u'Unknown',float(-9999)],
          [5,u'BAP001',u'Barometric Pressure',u"Not Applicable",84,u'Surface Water',u'Unknown',False,0,103,u'Unknown',u'Unknown',float(-9999)],
         ] 
def main_engine(mydb):
    engine = create_engine("mssql://%s:%s@localhost:3108/%s"%(user,password,mydb),module_name='pyodbc')
    return engine

def get_session(engine):
    return orm.scoped_session(orm.sessionmaker(bind=engine,autoflush=True,expire_on_commit=True))
    
if __name__ == '__main__':
    engine = main_engine(mydb)
    connection = engine.connect()
    #engine.echo = True
    print "engine establishment successful......"
    result =  connection.execute("select * from Sources")
    for row in result: print row
    metadata = schema.MetaData(bind=engine,reflect=True)
    print metadata
    #print metadata.sorted_tables
    Sources_table = schema.Table('Sources',metadata,  \
                                autoload=True,autoload_with=engine)
    Variables_table = schema.Table('Variables',metadata,  \
                                autoload=True,autoload_with=engine)
    #engine.echo = True
    orm.mapper(Sources,Sources_table)
    orm.mapper(Variables,Variables_table)
    session = get_session(engine)
    print "session, ORM mapper establishment successful......"
    #add new source
    newSource = Sources()
    newSource.SourceID,newSource.Organization = 1,u'TPWD'
    newSource.SourceDescription = u'Texas Parks and WildLife Department Data'
    newSource.ContactName,newSource.Phone = u'Unknown',u'Unknown'
    newSource.Email,newSource.Address,newSource.City,newSource.State,newSource.ZipCode = [u'Unknown']*5
    newSource.Citation,newSource.MetadataID = u"Unknown",0
    session.add(newSource)
    for vec in varSpe:
        newVar = Variables()
        newVar.VariableID = vec[0]
        newVar.VariableCode = vec[1]
        newVar.VariableName = vec[2]
        newVar.Speciation = vec[3]
        newVar.VariableUnitsID = vec[4]
        newVar.SampleMedium = vec[5]
        newVar.ValueType = vec[6]
        newVar.IsRegular = vec[7]
        newVar.TimeSupport = vec[8]
        newVar.TimeUnitsID = vec[9]
        newVar.DataType = vec[10]
        newVar.GeneralCategory = vec[11]
        newVar.NoDataValue = vec[12]
        session.add(newVar)
    print "inserting preset_record complete"
    session.flush()
    session.commit()
    
