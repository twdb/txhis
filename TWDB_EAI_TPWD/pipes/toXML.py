#=========================================================================
#
# Python Source File
#
# NAME: toXML.py
#
# AUTHOR: Tony
# DATE  : 3/07/2010
#
# COMMENT: 
#
#=========================================================================

import os, sys, string, StringIO, traceback

sys.path.append('..')
sys.path.append('../pipes')
sys.path.append('../sources')
sys.path.append('../sinks')


import utility_EAI.twdbEaiLog as reticLog
import utility_EAI.twdbEaiUtil as reticUtils

class pipe:


# ============================================================= #
#
#      Public methods (must exist) 
#
# ============================================================= #

    def __init__ (self, args, logger):
        try:
            self.args = args
            self.logList = logger
            self.name = args['name']
            self.InMsg = ''
            self.msg = ''
            self.msgKind = args['msgKind']
            self.delimiter = ''
            self.fieldNames = []
            self.fieldLength = []
            self.msgList = []
            self.rootTag = args['rootTag']
            self.recTag = args['recTag']
            self.encoding = args['encoding']
            self.metadata = {}
            #here, for update
            if self.msgKind == 'delimited':
                self.delimiter = args['delimiter']
                self.hasHeader = args['hasHeader']
                if self.hasHeader == 'n':
                    self.fieldNames = args['fieldNames']
            elif self.msgKind == 'fixedLength':
                self.fieldNames = args['fieldNames']
                self.fieldLength = args['fieldLength']
                self.hasHeader = 'n'
        except KeyError:
            reticLog.logError(self.logList, '(' + self.name + ') ' + "Error on ToXMLPipe initialization")
            reticLog.logError(self.logList, '(' + self.name + ') ' + "Parameter " + str(sys.exc_info()[1]) + " is missing on pipe definition. Exiting..." )
            sys.exit(1)
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '(' + self.name + ') ' + "Unknown error during initialization of pipe : " + self.name)                        
            reticLog.logError(self.logList, '(' + self.name + ') ' + errorMessage)
            sys.exit(1)


        
            
        
    
    def getMsg (self, message):
        'Initializes input buffer with message content'
        try:
            reticLog.logInfo(self.logList, '(' + self.name + ') ' + "Getting message into pipe")
            self.InMsg = StringIO.StringIO()
            self.msg = ''
            self.InMsg.write(message)
            self.InMsg.seek(0)
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '(' + self.name + ') ' + "Error during message retrieval in pipe" )                        
            reticLog.logError(self.logList, '(' + self.name + ') ' + errorMessage)
            return 1
        
    
    def process (self):
        'Creates the XML file in the output buffer'
        try:
            self.tmpMsg = StringIO.StringIO()
            self.updateAttributesFromMetadata()
            if self.hasHeader == 'y':
                self.fieldNames = self.getHeader()
            self.tmpMsg.write('<?xml version=\"1.0\" encoding=\"' + self.encoding + '\"?>')
            self.tmpMsg.write('\n<' + self.rootTag + '>\n')
            current_record = self.InMsg.readline()
            #print current_record
            while len(current_record) > 0 :
                #print current_record
                if current_record[0] == '#' :
                    current_record = self.InMsg.readline()
                    continue
                if current_record[-1] == '\n':
                    self.writeRecordAsXML(current_record[:-1])
                else:
                    self.writeRecordAsXML(current_record)
                current_record = self.InMsg.readline()                    
            self.tmpMsg.write('</' + self.rootTag + '>')
            self.tmpMsg.seek(0)
            self.msg = self.tmpMsg.read()
            #print self.msg
            self.msgList.append(self.msg)
            #print type(self.msgList)
            reticLog.logInfo(self.logList, '(' + self.name + ') ' + "Message process is finished in pipe")
            return 0
        except:
            errorMessage = traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])[0]
            reticLog.logError(self.logList, '(' + self.name + ') ' + "Error during message processing in pipe")
            reticLog.logError(self.logList, '(' + self.name + ') ' + errorMessage)
            return 1


    def updateAttributesFromMetadata(self):
        self.msgKind = self.args['msgKind']
        self.rootTag = self.args['rootTag']
        self.recTag = self.args['recTag']
        self.encoding = self.args['encoding']
        self.delimiter = self.args['delimiter']


        for key in self.metadata.keys():
            if string.find(self.args['msgKind'],'[[' + key + ']]') >=0:
                self.msgKind = string.replace(args['msgKind'],'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['delimiter'],'[[' + key + ']]') >=0:
                self.delimiter = string.replace(args['delimiter'],'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['rootTag'],'[[' + key + ']]') >=0:
                self.rootTag = string.replace(args['rootTag'],'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['recTag'],'[[' + key + ']]') >=0:
                self.recTag = string.replace(args['recTag'],'[[' + key + ']]',self.metadata[key])
            if string.find(self.args['encoding'],'[[' + key + ']]') >=0:
                self.encoding = string.replace(args['encoding'],'[[' + key + ']]',self.metadata[key])



# ============================================================= #
#
#      Private methods (optional) 
#
# ============================================================= #
        

    def writeRecordAsXML (self, record):
        'Write the record passed as argument to its XML representation '
        '(based on description given in the constructor)'
        
        if self.msgKind == 'delimited':
            #fields = string.split(record, chr(int(self.delimiter)))
            fields = string.split(record, self.delimiter)
            self.tmpMsg.write('    <' + self.recTag + '>\n')
            for i in range(len(self.fieldNames)):
                if len(fields[i]) > 0:
                    if fields[i][-1] == '\n':
                        self.tmpMsg.write('        <' + self.fieldNames[i] + '>' + reticUtils.replaceCharsForXML(fields[i][:-1]) + '</' + self.fieldNames[i] + '>\n')
                    else:
                        self.tmpMsg.write('        <' + self.fieldNames[i] + '>' + reticUtils.replaceCharsForXML(fields[i]) + '</' + self.fieldNames[i] + '>\n')
                else:
                    self.tmpMsg.write('        <' + self.fieldNames[i] + '/>\n')
            self.tmpMsg.write('    </' + self.recTag + '>\n')
        elif self.msgKind == 'fixedLength':
            fields = []
            for i in range(len(self.fieldLength)):
                fields.append(record[:self.fieldLength[i]])
                record = record[self.fieldLength[i]:]                  
            self.tmpMsg.write('    <' + self.recTag + '>\n')
            for i in range(len(self.fieldNames)):
                if fields[i][-1] == '\n':
                    self.tmpMsg.write('        <' + self.fieldNames[i] + '>' + reticUtils.replaceCharsForXML(fields[i][:-1]) + '</' + self.fieldNames[i] + '>\n')
                else:
                    self.tmpMsg.write('        <' + self.fieldNames[i] + '>' + reticUtils.replaceCharsForXML(fields[i]) + '</' + self.fieldNames[i] + '>\n')
            self.tmpMsg.write('    </' + self.recTag + '>\n')

    #need redo this one to accomodate bona fide need
    #fix 3/8/2010; -->find the first line not starting with # 
    def getHeader(self):
        self.InMsg.seek(0)
        header = self.InMsg.readline()
        while (header[0] == '#'):
            header = self.InMsg.readline()
        if header[-1] == '\n' :
            header = header[:-1]        
        headerList = string.split(header,chr(ord(self.delimiter)))
        headerDict = {}
        for i,element in enumerate(headerList):
            headerDict[i] = element
        return headerDict
        


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
    pipe_args = {}
    pipe_args['msgKind']='delimited'
    pipe_args['hasHeader']='y'
    pipe_args['rootTag']='test_TPWD_Emat'
    pipe_args['recTag']='test_TPWD_Emat_record'
    pipe_args['encoding']='UTF-8'
    pipe_args['delimiter']=','
    #pipe_args['fieldNames']={}
    pipe_args['fieldLength']={}
#    pipe_args['fieldNames'][0]='Source_File_Name'
#    pipe_args['fieldNames'][1]='Year'
#    pipe_args['fieldNames'][2]='Month'
#    pipe_args['fieldNames'][3]='Day'
#    pipe_args['fieldNames'][4]='Hour'
#    pipe_args['fieldNames'][5]='Minute'
#    pipe_args['fieldNames'][6]='Second'
#    pipe_args['fieldNames'][7]='DOSat'
#    pipe_args['fieldNames'][8]='AirPressure'
#    pipe_args['fieldNames'][9]='AirTemperature'
#    pipe_args['fieldNames'][10]='BatteryVoltage'
#    pipe_args['fieldNames'][11]='DO'
#    pipe_args['fieldNames'][12]='EC_Norm'
#    pipe_args['fieldNames'][13]='Salinity'
#    pipe_args['fieldNames'][14]='Temperature'
#    pipe_args['fieldNames'][15]='Turbidity'
#    pipe_args['fieldNames'][16]='WaterLevel_Non_Vented'
#    pipe_args['fieldNames'][17]='WaterLevel_Vented'
#    pipe_args['fieldNames'][18]='pH'
    pipe_args['name'] = 'TPWD_Emat_Test'
    #print pipe_args['fieldNames']
    #print raw_input("conitue...")
    testPipe = pipe(pipe_args,logList)
    #get os type
    if sys.platform == 'win32':        
        testPath = '..\\file_source_exp\\'
    else:
        testPath = '/home/ttan/file_source_exp/'
    testFileName = testPath + 'EMat_201003181523.csv'
    fp = open(testFileName)
    if reticUtils.istext(fp):
        fp.close()
        fp = open(testFileName,'r')
    else:
        fp.close()
        fp = open(testFileName,'rb')
    testPipe.getMsg(fp.read())
    testPipe.process()
    for i in range(len(testPipe.msgList)):
        print >> open("test_TPWD_Emat_out.xml",'w'),testPipe.msgList[i]

