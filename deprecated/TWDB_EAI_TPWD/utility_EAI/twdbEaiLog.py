#=========================================================================
#
# Python Source File
#
# NAME: twdbEaiLog.py
#
# DATE  : 17/12/2009
#
# COMMENT: Permits to create several loggers for the adaptor with different
#          log level
#
#=========================================================================
import sys, random
import logging
sys.path.append("..")
from guiWidget.GuiStream import GuiOutput


#add loggers to sources, pipes, sinks
def addLogger(logList, logAttributes):
    """
    add a logger instance to log list
    parameters:
    loglist: existed log list
    logAttributes: dictionary describing the log to be added;
       key include : 'name': name of the logger, (technically contatenated with a random number)
                     'level': any of ['DEBUG','INFO','ERROR','WARN','CRITICAL'] 
                     'handler': any of ConsleApp,FileApp,RollingFileApp,
                                 'RollingFileApp', 'SMTP', 'SocketApp',
    """
    newLogger = logging.getLogger(logAttributes['name']+str(int(random.random()*10000)))
    if logAttributes['level'].upper() == 'DEBUG' :
        newLogger.setLevel(logging.DEBUG)
    elif logAttributes['level'].upper() == 'INFO' :
        newLogger.setLevel(logging.INFO)
    elif logAttributes['level'].upper() == 'ERROR' :
        newLogger.setLevel(logging.ERROR)
    elif logAttributes['level'].upper() == 'WARN' :
        newLogger.setLevel(logging.WARN)
    elif logAttributes['level'].upper() == 'CRITICAL' :
        newLogger.setLevel(logging.CRITICAL)

    #if logAttributes['format'].upper() == 'SIMPLE' :
        #layout = SimpleLayout()
    #elif logAttributes['format'].upper() == 'HTML' : 
        #layout = HTMLLayout()
    #else : 
        #layout = PatternLayout(logAttributes['format'])

    

    #console appender
    if logAttributes['handler'] == 'ConsoleAppender':
        #attach the log to a guibox instead of standard input
        #appender = logging.StreamHandler(GuiOutput(logAttributes['name']))
        appender = logging.StreamHandler()
        formatter = logging.Formatter('%(filename)s: %(levelname)s: %(message)s')
        appender.setFormatter(formatter)
    elif logAttributes['handler'] == 'FileAppender':
        if logAttributes['mode'].lower() == 'a' :
            appender = logging.FileHandler(logAttributes['fileName'],'a')
        else:
            appender = logging.FileHandler(logAttributes['fileName'],'w')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        appender.setFormatter(formatter)
    elif logAttributes['handler'] == 'RollingFileAppender':
        if logAttributes['mode'].lower() == 'a' :
            appender = logging.handler.RotatingFileHandler(logAttributes['fileName'],'a',logAttributes['maxBytes'])
        else:
            appender = logging.handler.RotatingFileHandler(logAttributes['fileName'],'w',logAttributes['maxBytes'])
    elif logAttributes['handler'] == 'SMTPAppender':
        appender = logging.handlers.SMTPHandler(logAttributes['SMTPHost'],logAttributes['From'],logAttributes['To'],
                                      logAttributes['Subject'])
        
    elif logAttributes['handler'] == 'SocketAppender':
        appender = logging.handlers.SocketHandler(logAttributes['host'],int(logAttributes['port']))
    
    
        
    newLogger.addHandler(appender)
    #format the handler:
    logList.append(newLogger)

        
def logDebug(logList, message):
    for logger in logList:
        logger.debug(message)
        
def logInfo(logList, message):
    for logger in logList:
        logger.info(message)

def logWarning(logList, message):
    for logger in logList:
        logger.warn(message)
        
def logError(logList, message):
    for logger in logList:
        logger.error(message)
        
def logCritical(logList, message):
    for logger in logList:
        logger.critical(message)


if __name__ == '__main__':
    logList = []
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
                 'fileName':'test.txt'
                }
    addLogger(logList,logAttDic)
    addLogger(logList,logAttDic_2)
    logDebug(logList,"debug message")
    logInfo(logList,"info message")
    logWarning(logList,"warn message")
    logError(logList,"error message")
    logCritical(logList,"critical message")
    print "test complete......"

        
