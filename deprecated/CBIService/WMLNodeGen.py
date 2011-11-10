from cuashi import *
from variable_info import *
from backEndhttpReqConstruct import getCBIValues,getCBIParamList,parseSOS

#generate queryInfo node:this piece of crap add criteria inside of an 
#                        queryInfo node
def genQueryInfo(parent_Node,whichpara,value):
    """
    Generate a QueryInfo XML node, under CBI webservice context
    input:  parentNode, parametername to set, value to set
    output: None (because parentNone has been in-place set)
    """
    queryInfoNode = parent_Node.new_queryInfo()
    criteriaNode = queryInfoNode.new_criteria()
    if (whichpara == "location" and value):
        criteriaNode.set_element_locationParam(value)
    #these are to be completed
    else:
        pass
    queryInfoNode.set_element_criteria(criteriaNode)
    parent_Node.set_element_queryInfo(queryInfoNode)
    

#generate site Node
def genSite_forGetSite(parent_Node,xmlNode,key,name,srsInfo,siteList):
    """
    Generate a Site node for the parent_Node.
    input: parent node, xmlNode ("InstituteObPoints Node) in this case, 
           and name (for this site)
    output: None (because parentNone will be set separately)
    """
    newSiteNode = parent_Node.new_site()
    newSiteInfoNode = newSiteNode.new_siteInfo()
    newSiteInfoNode.set_element_siteName(name)
    #here, wait for Daharas
    newSiteCodeNode = newSiteInfoNode.new_siteCode(key)
    newSiteCodeNode._attrs=dict([('network',"CBI"),('siteID',key)])
    #here, WSDL definition is problematic
    newSiteInfoNode.set_element_siteCode([newSiteCodeNode])
    geoLocationOuterNode=newSiteInfoNode.new_geoLocation()
    geoLocationInnerNode=geoLocationOuterNode.new_geogLocation()
    geoLocationInnerNode._attrs = dict([('srs',srsInfo),("xsi:type","ns2:LatLonPointType")])
    #here, XML transform begins
    geoLocationInnerNode._latitude = float(xmlNode[5][0][0].text.split()[0])
    geoLocationInnerNode._longitude = float(xmlNode[5][0][0].text.split()[1])
    geoLocationOuterNode.set_element_geogLocation(geoLocationInnerNode)
    newSiteInfoNode.set_element_geoLocation(geoLocationOuterNode)
    newSiteInfoNode.set_element_verticalDatum(xmlNode[7].text)
    #countyNote = newSiteInfoNode.new_note(':'.join([xmlNode[9].text,"Coastal Water Data"]))
    countyNote = newSiteInfoNode.new_note(':'.join(["CBI","Coastal Water Data"]))
    countyNote._attrs = dict(title='County')
    stateNote = newSiteInfoNode.new_note("Texas")
    stateNote._attrs = dict(title='State')
    commentNote = newSiteInfoNode.new_note(xmlNode[15].text)
    commentNote._attrs = dict(title='Comment')
    newSiteInfoNode.set_element_note([countyNote,stateNote,commentNote])
    newSiteNode.set_element_siteInfo(newSiteInfoNode)                                  
    return siteList.append(newSiteNode)

#generate queryinfor gernerateDS node
def generateQueryInfo_string(locationparam):
    #set location parameters
    criteriaInstance = criteria()
    if type(locationparam) != type(""):
        try: 
            locationparam = '?'.join(locationparam._string)
        except:
            locationparam = ""
    criteriaInstance.set_locationParam(locationparam)
    #set the return query info parameter
    queryInfo = QueryInfoType()
    queryInfo.set_criteria(criteriaInstance)
    return queryInfo

#generate siteInfo node
def generateSiteInfo_string(xmlNode,srsInfo):
    SiteInfoNode = SiteInfoType()
    #set site name
    SiteInfoNode.set_siteName(xmlNode[4].text.split(":")[1])
    #set site code
    siteCodeNode = siteCode()
    siteCodeNode.set_network("CBI")
    siteCodeNode.set_siteID(xmlNode[4].text.split(":")[0])
    SiteInfoNode.set_siteCode([siteCodeNode])
    #timezone info set
    timeZoneInfoNode = timeZoneInfo()
    timeZoneInfoNode.set_defaultTimeZone("UTC")
    timeZoneInfoNode.set_daylightSavingsTimeZone("Unkown")
    SiteInfoNode.set_timeZoneInfo(timeZoneInfoNode)
    #set geolocation
    geoLocationNode = geoLocation()
    #set inner geoglocation
    GeogLocationType.subclass=LatLonPointType
    innerGeoLocationNode = GeogLocationType.factory()
    innerGeoLocationNode.set_srs(srsInfo)
    innerGeoLocationNode.set_latitude(xmlNode[5][0][0].text.split()[0])
    innerGeoLocationNode.set_longitude(xmlNode[5][0][0].text.split()[1])
    geoLocationNode.set_geogLocation(innerGeoLocationNode)
    #set node here         
    SiteInfoNode.set_geoLocation(geoLocationNode)
    SiteInfoNode.set_verticalDatum(xmlNode[7].text)
    countyNote = NoteType(title='County',valueOf_=':'.join(["CBI","Coastal Water Data"]))
    stateNote = NoteType(title='State',valueOf_='Texas')
    commentNote = NoteType(title='Comment',valueOf_=xmlNode[15].text)
    SiteInfoNode.set_note([countyNote,stateNote,commentNote])
    return SiteInfoNode

#generate series node: to be compelted
def generateSeriesNode(xmlNode):
    seriesNode = series()
    variableNode = VariableInfoType()
    #for element variable code
    variableCodeNode = variableCode()
    variableCodeNode.set_default(True)
    #get property of this variable
    variableCodeInfoSet = variable_Dictionary[name_to_code_mappingDictionary[xmlNode[2].text]]
    variableCodeNode.set_variableID(int(variableCodeInfoSet["variableID"]))
    variableCodeNode.set_vocabulary("CBI")
    variableCodeNode.setValueOf_(variableCodeInfoSet['variableCode'])
    variableNode.set_variableCode([variableCodeNode])
    #set variable name
    variableNode.set_variableName(variableCodeInfoSet["variableName"])
    #set value type
    variableNode.set_valueType("Field Observation")
    #set value data type
    variableNode.set_dataType("Unknown")
    #set general Category
    variableNode.set_generalCategory("Hydrology")
    #set sample medium
    variableNode.set_sampleMedium(variableCodeInfoSet['medium'])
    #set units element
    unitNode = units()
    unitNode.set_unitsAbbreviation(variableCodeInfoSet['units']['abbr'])
    unitNode.set_unitsCode(variableCodeInfoSet['units']['unitsCode'])
    if variableCodeInfoSet['units'].has_key("unitsType"):
        unitNode.set_unitsType(variableCodeInfoSet['units']["unitsType"])
    unitNode.setValueOf_(variableCodeInfoSet['units']["name"])
    variableNode.set_units(unitNode)
    #set nodata value
    variableNode.set_NoDataValue("-9999")
    #time support. In CBI's case, it's not regular
    timeSupportNode = timeSupport(isRegular=False)
    variableNode.set_timeSupport(timeSupportNode)
    #series Node
    seriesNode.set_variable(variableNode)
    #Time Peiod
    variableTimeIntervalNode = TimeIntervalType()
    from datetime import datetime,timedelta
    UTCOffset = timedelta(hours=float(6))
    #adjust xml ZULU time to CST time
    startTimeStr = ""
    if not xmlNode[10].text:
        startTimeStr = None
    else:
        startTime = datetime.strptime(xmlNode[10].text,'%Y-%m-%dT%H:%M:%SZ')+UTCOffset
        startTimeStr = "T".join(str(startTime).split())
    endTimeStr = ""
    if not xmlNode[11].text:
        endTimeStr = None
    else:
        endTime = datetime.strptime(xmlNode[11].text,'%Y-%m-%dT%H:%M:%SZ')+UTCOffset
        endTimeStr = "T".join(str(endTime).split())
    variableTimeIntervalNode.set_beginDateTime(startTimeStr)
    variableTimeIntervalNode.set_endDateTime(endTimeStr)
    seriesNode.set_variableTimeInterval(variableTimeIntervalNode)
    #Method lement
    MethodNode = MethodType()
    MethodNode.set_methodID(0)
    MethodNode.set_MethodDescription("No method specified")
    seriesNode.set_Method(MethodNode)
    #Source element
    sourceNode = SourceType()
    sourceNode.set_Organization("CBI")
    sourceNode.set_SourceDescription('Texas Coastal Ocean Observation Network')
    seriesNode.set_Source(sourceNode)
    #Quality Control ID
    qcLevelNode = QualityControlLevelType()
    qcLevelNode.set_qualityControlLevelID(-9999)
    seriesNode.set_QualityControlLevel(qcLevelNode)
    return seriesNode
    
#generate variable node string version (using generatedDS)
def generateVariableTypeNodeString(key,variableKeyedValue):
    variableNode = VariableInfoType()
    #generate variableCode node 
    varCodeNode = variableCode()
    varCodeNode.set_default(True)
    varCodeNode.set_variableID(int(variableKeyedValue['variableID']))
    varCodeNode.set_vocabulary("CBI")
    varCodeNode.setValueOf_(variableKeyedValue['variableCode'])
    variableNode.set_variableCode([varCodeNode])
    #set variable name
    variableNode.set_variableName(variableKeyedValue["variableName"])
    #set value type
    variableNode.set_valueType("Field Observation")
    #set value data type
    variableNode.set_dataType("Unknown")
    #set general Category
    variableNode.set_generalCategory("Hydrology")
    #set sample medium
    variableNode.set_sampleMedium(variableKeyedValue['medium'])
    #set units element
    unitNode = units()
    unitNode.set_unitsAbbreviation(variableKeyedValue['units']['abbr'])
    unitNode.set_unitsCode(variableKeyedValue['units']['unitsCode'])
    if variableKeyedValue['units'].has_key("unitsType"):
        unitNode.set_unitsType(variableKeyedValue['units']["unitsType"])
    unitNode.setValueOf_(variableKeyedValue['units']["name"])
    variableNode.set_units(unitNode)
    #set nodata value
    variableNode.set_NoDataValue("-9999")
    #time support. In CBI's case, it's not regular
    timeSupportNode = timeSupport(isRegular=False)
    variableNode.set_timeSupport(timeSupportNode)
    return variableNode

#generate variable node node version (using ZSI stub code)
def generateVariableTypeNode(emptyNode,key,variableKeyedValue):
    #variable code element
    variableCodeNode = emptyNode.new_variableCode(variableKeyedValue['variableCode'])
    variableCodeNode._attrs = dict([('vocabulary',"CBI"),('default','true'),('variableID',variableKeyedValue['variableID'])])
    emptyNode.set_element_variableCode([variableCodeNode])
    #variable name element
    emptyNode.set_element_variableName(variableKeyedValue["variableName"])
    #value type element
    emptyNode.set_element_valueType("Field Observation")
    #data type element
    emptyNode.set_element_dataType("Unknown")
    #general Category element
    emptyNode.set_element_generalCategory("Hydrology")
    #sample medium element
    emptyNode.set_element_sampleMedium(variableKeyedValue['medium'])   
    #units element
    unitsNode = emptyNode.new_units(variableKeyedValue['units']["name"])
    attributeDictionary = [('unitsAbbreviation',variableKeyedValue['units']['abbr']),
                           ('unitsCode',variableKeyedValue['units']['unitsCode'])]
    if variableKeyedValue['units'].has_key("unitsType"):
        attributeDictionary.append(('unitsType',variableKeyedValue['units']["unitsType"]))
    unitsNode._attrs = dict(attributeDictionary)
    emptyNode.set_element_units(unitsNode)
    emptyNode.set_element_NoDataValue("-9999")
    timeSupportNode = emptyNode.new_timeSupport()
    timeSupportNode._attrs = dict([('isRegular',False)])
    emptyNode.set_element_timeSupport(timeSupportNode)
    return emptyNode


#generate a the value list for timeSeries node.
def generateSeriesValueList(siteCode,variableCode,startDate,endDate):
    valuesNode = TsValuesSingleVariableType()
    valuesNode.set_unitsAbbreviation(variable_Dictionary[variableCode]['units']['abbr'])
    valuesNode.set_unitsCode(variable_Dictionary[variableCode]['units']['unitsCode'])
    qurey = getCBIParamList(siteCode,variableCode,startDate,endDate)
    outPutStringIO = getCBIValues(qurey)
    valueSingleNodeList = []
    parseResult = parseSOS(outPutStringIO)
    for row in parseResult[1].split():
        #generate value node here
        csvReturn = row.split(',')
        import time
        datetimeString,realValue = csvReturn[1],csvReturn[5]
        valueSingleNode = ValueSingleVariable()
        valueSingleNode.set_censorCode("nc")
        valueSingleNode.set_qualityControlLevel("-9999")
        valueSingleNode.set_dateTime(datetimeString)
        valueSingleNode.set_methodID(0)
        valueSingleNode.set_sourceID(1)
        valueSingleNode.setValueOf_(realValue)
        valueSingleNodeList.append(valueSingleNode)
#    while line:
#        #generate value node here
#        if line.startswith("#"):
#            line = outPutStringIO.readline() 
#            continue
#        else:
#            import time
#            datetimeString,realValue = line.split()
#            #format datetime string
#            fmtDateTimeString = time.strftime("%Y-%m-%dT%H:%M:%S", \
#                                              time.strptime(datetimeString,"%Y%j+%H%M"))
#            if realValue == "NA":
#                realValue = "-9999"
#            valueSingleNode = ValueSingleVariable()
#            valueSingleNode.set_censorCode("nc")
#            valueSingleNode.set_qualityControlLevel("-9999")
#            valueSingleNode.set_dateTime(fmtDateTimeString)
#            valueSingleNode.set_methodID(0)
#            valueSingleNode.set_sourceID(1)
#            valueSingleNode.setValueOf_(realValue)
#            valueSingleNodeList.append(valueSingleNode)
#            line = outPutStringIO.readline()
    valuesNode.set_value(valueSingleNodeList) 
    return valuesNode
