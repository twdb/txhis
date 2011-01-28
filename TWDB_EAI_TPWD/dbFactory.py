#=========================================================================
#
# Python Source File
#
# NAME: dbFactory.py
#
# AUTHOR: Tony Tan
# DATE  : 06/08/2003
#
# COMMENT: the dbFactory class permits to get an abstraction layer
#          for db calls
#=========================================================================


import string, traceback, sys
import utility_EAI.twdbEaiLog as reticLog
from sqlalchemy import create_engine

class dbFactory:
    
    def __init__ (self, args, logger):
        self.session = None
        #use sqlalchemy, so no cusor needed
        #self.cursors = {}
        self.logList = logger
        self.connect(args)
        
        
    def connect (self, args):
        'Establish a connection with the database'
        try:
            reticLog.logInfo(self.logList, "Intitializing Database Connection : " + args['dsn'])            
            #construct connection string according to parameters
            engineStr = string.join([args['dbType'],
                                     ''.join(['//', args['user']],),
                                     ''.join([args['password'],"@",args['dsn']]) ],
                                     ':')
            #print engineStr
            dbDriverMod = args['driverName']
            self.engine = create_engine(engineStr,module_name = dbDriverMod)
            reticLog.logInfo(self.logList, "DataBase Connection established")
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, "Database error : " + errorMessage ); raise "Database Error";                        
        
            
    


if __name__ == '__main__':
    logAttDic = {#get self name
                 'name':sys.argv[0].split(".")[0],
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'ConsoleAppender',
                }
    logAttDic_2 = {#get self name
                 'name':sys.argv[0].split(".")[0],
                 'level': 'DEBUG',
                 'format':'Simple',
                 'handler':'FileAppender',
                 'mode': 'w',
                 'fileName':'fileSourceTest.txt'
                }
    logList = []
    reticLog.addLogger(logList,logAttDic)
    reticLog.addLogger(logList,logAttDic_2)
    dbArg = {}
    dbArg['dbType'] = 'mssql'
    dbArg['user']='sa'
    dbArg['password']='12345678a'
    dbArg['dsn']='10.10.13.77:3108/OD_TPWD'
    dbArg['driverName']='pyodbc'
    #self test   
    dbInstance = dbFactory(dbArg,logList)
    dbInstance.connect(dbArg)
