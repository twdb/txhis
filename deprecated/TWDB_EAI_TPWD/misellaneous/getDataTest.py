'''
Created on Jul 16, 2010

@author: CTtan
'''
from sqlalchemy import orm, schema, types, create_engine,exc,func,and_
from sqlalchemy.orm.exc import NoResultFound
from StringIO import StringIO
import utility_EAI.twdbEaiLog as reticLog
from sources import HTTPSource
import sys,traceback

RESULT = "1"
EVENT = "2"

class DataValues(object):
    def __init__(self,DataValue,LocalDateTime,SiteID,VariableID,\
                   CensorCode,MethodID,UTCOffset=-6,SourceID=1,QualityControlLevelID=1):
        import datetime
        self.DataValue = DataValue
        self.LocalDateTime = LocalDateTime
        self.UTCOffset = UTCOffset
        self.DateTimeUTC = LocalDateTime + datetime.timedelta(hours=UTCOffset)
        self.SiteID = SiteID
        self.VariableID = VariableID
        self.CensorCode = CensorCode
        self.MethodID = MethodID
        self.SourceID = SourceID
        self.QualityControlLevelID = QualityControlLevelID
        


# main routine
def main():
    #session = initDB()
    logAttDic = {#get self name
                 'name': 'httpsource testing',
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'ConsoleAppender',}
    logList = []
    reticLog.addLogger(logList,logAttDic)
    src_args = {}
    src_args['name'] = "testing httpsource"
    src_args['URL'] = "http://www.tceq.state.tx.us/cgi-bin/compliance/monops/crp/sampquery.pl"
    src_args['pollPeriod'] = 12.45
    src_args['params'] = [{"filetype":EVENT, "basinid":"0510","year":"2005"}]
    src_args['params'].append({"filetype":RESULT, "basinid":"0510","year":"2005"})
    sampleSource = HTTPSource.source(src_args,logList)
    sampleSource.start()
    #echoResult = []
    while(sampleSource.next()==1):
        raw_input("Content of this URL:  %s" % sampleSource.URL)
        print sampleSource.msg
        #add stringIO here
        sampleSource.commit()
    #sampleSource.commit()
    raw_input("here,more message")
    for msg in sampleSource.msg:
        print msg
    

if __name__ == "__main__":
    main()