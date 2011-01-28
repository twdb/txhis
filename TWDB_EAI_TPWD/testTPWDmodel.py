from sqlalchemy import orm, schema, types, create_engine
import datetime

metadata = schema.MetaData()

major_area_str = 'ma'
minor_bay_str = 'mb'
station_str    = 'st'

VariableIDMap = {
                    'start_temperature_num':1,
                    'start_salinity_num':2,
                    'start_turbidity_num':3,
                    'start_dissolved_oxygen_num':4,
                    'start_barometric_pressure_num':5,
                }

#DataValues class  --> object
class DataValues(object):
    pass

#Sites class --
class Sites(object):
    pass

engine = create_engine('mssql://testaaa:12345678a@localhost:3108/OD_TPWD',module_name='pyodbc')
metadata.bind = engine
#here, orm magic happens
#datavalues table
DataValues_table = schema.Table('DataValues',metadata,  \
                                autoload=True,autoload_with=engine)
orm.mapper(DataValues,DataValues_table)
#offsets table
Sites_table = schema.Table('Sites',metadata,
#                           schema.Column('SiteID', types.Integer, \
#                                        schema.Sequence('Sites_seq_id',start=0),
#                                primary_key=True),useexisting=False,
                                autoload=True,autoload_with=engine)
orm.mapper(Sites,Sites_table)

def tpwdProcessInfo(record):
    #resultObjectList
    resObList = []
    #create an object to be update in real database
    LocalDateTime = datetime.datetime.strptime(record['start_dttm'], "%Y-%m-%d %H:%M:%S")
    UTCOffset = float(-6)
    DateTimeUTC = LocalDateTime + datetime.timedelta(hours=UTCOffset)
    #assuming this is from SiteID 53,SourceID 1, MethodID 1,QualityControlLevelID 1, CensorCode nc
    SiteID = record['SiteID']
    SourceID = 1
    MethodID = 0
    CensorCode = u'nc'
    QualityControlLevelID = 0
    #right now 6 data field(s)
    needVar = VariableIDMap.keys()
    #process actual record, only record in needVar list will be processed
    for key in record.keys():
        if (not (key in needVar)) or (not record[key]):
            continue
        else:
            #construct && set object to be inserted to database
            recordObj = DataValues()
            #print "key %s, value %s" % (key,record[key])
            recordObj.DataValue = float(record[key])
            recordObj.LocalDateTime = LocalDateTime
            recordObj.UTCOffset = UTCOffset
            recordObj.DateTimeUTC = DateTimeUTC
            recordObj.SiteID = SiteID
            recordObj.VariableID = VariableIDMap[key]
            recordObj.CensorCode = CensorCode
            recordObj.MethodID = MethodID
            recordObj.SourceID = SourceID
            recordObj.QualityControlLevelID = QualityControlLevelID
            resObList.append(recordObj)
    return resObList




            
    
    
        
