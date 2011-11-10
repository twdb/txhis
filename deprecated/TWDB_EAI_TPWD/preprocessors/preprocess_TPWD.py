import sys,csv,os,itertools
import datetime,string
sys.path.append("..")
import utility_EAI.twdbEaiLog as reticLog
import utility_EAI.twdbEaiUtil as reticUtils

#configuration section
if (sys.platform == 'linux2'):
    direcotryPath = '/T/SWR/BaysEstuaries/Data/External_Data_Sources/TPWD/Coastal_Fisheries/'
elif (sys.platform == 'win32'): 
    direcotryPath = 'T:\\BaysEstuaries\\Data\\External_Data_Sources\\TPWD\\Coastal_Fisheries\\'
localPath = 'file_source_TPWD/'
##########################################################
#preprocessor program for TPWD
#usage: preprocess_TPWD.py filename
#where file name must be a .csv file from TPWD department
#operation sequence has been modified March,18th 2010 
##########################################################
MA_COL,MB_COL,STA_COL, = ord('B')-ord('A'),ord('E')-ord('A'),ord('C')-ord('A')
DATE,LATITUDE,LONGITUDE = ord('I')-ord('A'),ord('K')-ord('A'),ord('L')-ord('A')
#S_WDEPTH,D_WDEPTH (do not need these two as of right now)
BAROMETRIC_P = ord('P')-ord('A')
TEMPERATURE,DO,SALINITY,TURBIDITY = range(ord('W')-ord('A'),ord('Z')-ord('A')+1)

NEEDED_COL = [ 
               #time, longitude and latitude
               DATE,LATITUDE,LONGITUDE,
               #name indications
               MA_COL,STA_COL,MB_COL,
               # a series of parameter needed (extend here)
               #S_WDEPTH,D_WDEPTH (do not need these two as of right now)
               BAROMETRIC_P,
               TEMPERATURE,DO,SALINITY,TURBIDITY
               ]

def preprocess(filename,loglist):
    """
    function that does preprocessing TPWD file.(in CSV format)
    main functionality:
    1. extract columns needed.
    2. combine repetitive rows (after extract the needed columns)
    3. sort all rows on chronological order
    4. from the results of step 1) 2) 3); save a copy of the csv file,
       and add a timestamp at the end of it
    for this specific case (TPWD), there are 2 more operations performed: 
    a) transfer time into correct date format;
    b) transfer longitude and latitude into correct decimal format
    """
    #open a csv reader
    TPWDReader = csv.reader(open(filename))
    #start processing
    reticLog.logInfo(loglist, "start preprocessing %s......" % filename.split(os.sep)[-1])
    #extract the columns needed:
    #more pythonic way:
    #print "extracting needed columns......",
    extractedList = list(list(row[i] for i in NEEDED_COL) for row in TPWDReader)
    #print "done"
    #transfer date
    #headerRow : the name of all the columns, do not need to change.
    #recordRows : actual data part, need to change
    headerRow,recordRows = extractedList[0],extractedList[1:]
    #sort the output list on timely basis
    #if times are the same, sort on latitude,longitude
    #print "sort rows based on completion time......",   
   
    #print "done"
    #eliminate duplicate rows
    #print "eliminating duplicated rows......",
    groupByList=list(row for row,group in itertools.groupby(recordRows))
    groupByList.sort(date_compare)
    #print "done"     
    #convert time to datetime format
    #convert longitude, latitude to decimal format
    #print "convert date and geological coordinates......", 
    for row in groupByList:
        row[NEEDED_COL.index(DATE)]= str(datetime.datetime.strptime(row[NEEDED_COL.index(DATE)][:-4],'%d%b%Y:%H:%M:%S'))  
        row[NEEDED_COL.index(LONGITUDE)] = GotoDecimal(row[NEEDED_COL.index(LONGITUDE)],True)
        row[NEEDED_COL.index(LATITUDE)] = GotoDecimal(row[NEEDED_COL.index(LATITUDE)])
    #print "done"
    #now add header row back
    groupByList.insert(0,headerRow)    
    #print "%d non-duplicated records generated" % len(groupByList)
    #outputfile name process: add time stamp to the 
    fileSplit = filename.split('.')
    #here, timestamp precesion: minutes, concatenated with underscore 
    fileSplit[0] = string.join([fileSplit[0].split('_')[-2],datetime.datetime.now().strftime("%Y%m%d%H%M")],'_')
    outFileName = ''.join([localPath,
                             string.join(fileSplit,'.').split(os.sep)[-1]])
    #write output file
    #print "write output file with timestamp (%s)......"  % outFileName,
    #Write in binary mode to avoid the extra newline character 
    outWriter = csv.writer(open(outFileName, "wb"))
    outWriter.writerows(groupByList)    
    reticLog.logInfo(loglist, "preprocessing %s is done." % filename.split(os.sep)[-1])
    #print "%d rows generated for %s." % (len(groupByList),outFileName)
        

#comparing function
def date_compare(row1, row2):
    """compare two rows in TPWD csv file based on chronological order"""
    date_row1 = datetime.datetime.strptime(row1[NEEDED_COL.index(DATE)][:-4],'%d%b%Y:%H:%M:%S')
    date_row2 = datetime.datetime.strptime(row2[NEEDED_COL.index(DATE)][:-4],'%d%b%Y:%H:%M:%S')
    if date_row1 > date_row2:
        return 1
    elif date_row1 == date_row2:
        #if times are the same, sort by latitude, longitude
        if float(row1[NEEDED_COL.index(LATITUDE)]) > float(row2[NEEDED_COL.index(LATITUDE)]):
            return 1
        elif (float(row1[NEEDED_COL.index(LONGITUDE)]) == float(row2[NEEDED_COL.index(LONGITUDE)])) and \
             (float(row1[NEEDED_COL.index(LONGITUDE)]) == float(row2[NEEDED_COL.index(LONGITUDE)])):
            return 0
        else:
            return -1
    else:
        return -1

#function converting longitude and latitude to decimal
def GotoDecimal(classicalNm,is_WESTlongitude = False):
    """convert longitude and latitude in TPWD file in decimal format
       note: in west semisphere, all longitude should be negative
    """
    degree,minutes,seconds = float(classicalNm[0:2]),float(classicalNm[2:4]),float(classicalNm[4:6])
    if (not is_WESTlongitude):
        return str(float(degree + minutes/60 + seconds/3600))
    # for longitude, negative
    else:
        return str(-float(degree + minutes/60 + seconds/3600))
    

#assumption(s): all the incoming .csv file is placed under the specific location (direcotryPath/directoryName),
#               inside different folders with name of "request_%timstamp$".
def preprocess_batch(directoryName,loglist):
    """Find the fold under secific location(direcotryPath) with the largest time stamp;
       and preprocess each csv file inside it
    """
    reticLog.logInfo(loglist,"Starting TPWD preprocessing procedure")
    import glob
    #get the fold with the largest timestamp
    max_datetime = None
    folderToProcess = None
    for name in glob.glob('%s/request_*' % directoryName):
        import datetime
        year,month,day = int(name.split('request')[1][1:][0:4]), \
                         int(name.split('request')[1][1:][4:6]), \
                         int(name.split('request')[1][1:][6:8])
        tempDateTime = datetime.datetime(year,month,day)
        if (not max_datetime) or (tempDateTime > max_datetime): 
            max_datetime = tempDateTime
            folderToProcess = name
    #at this point, folderToProcess should have the folder name of the latest timestamp
    reticLog.logInfo(loglist, 'preprocess folder: %s, with requested time %s' % (folderToProcess,str(max_datetime)) )
    #so preprocess each file inside folderToProcess
    for name in glob.glob('%s/*.csv' % folderToProcess):
        preprocess(name,loglist)
        #potential archiving logic goes here       
        
        

if __name__ == '__main__':
    import time
    start = time.clock()
    localPath = '../file_source_TPWD/'
    preprocess_batch(direcotryPath,[])
    #sort by completion date/date
    #get the benchmark
    elapsed_time = time.clock()-start
    print "time elapsed: ",elapsed_time

    
    
    

