#!/usr/bin/python
from WaterOneFlow_services_server import *
from WaterOneFlow_services_types import *
from backEndhttpReqConstruct import *
from WMLNodeGen import *
from datetime import datetime,timedelta
from ZSI.ServiceContainer import AsServer
from ZSI import ServiceContainer, Fault, ParsedSoap 
from ZSI.fault import Fault, FaultType, Detail
from portablelocker import *
from variable_info import variable_Dictionary
from cuashi import *
import cStringIO

###########################################################################
#siteInfo_dictionary: _modTime, and SiteInfo (only geological information
#                     XML nodes keyed by its site ID _modTime 
#                      is the last time this dictionary updated/recached
#   global siteInfo_site_dictionary variable. used for cache 
###########################################################################
siteInfo_site_dictionary={"__modTime":datetime.now()}
###########################################################################
WSDLAddress = "http://midgewater.twdb.state.tx.us/WMLWS/CBIWML?wsdl"
WS_PATH = "CBIWML"

#service implementation
class WaterOneFlowServiceImpl(WaterOneFlow):
    #class_member:
    #initialization
    #post: actual published URL address
    def __init__(self,post=None):
        #complete later
        WaterOneFlow.__init__(self,post)
    #GetSites method
    def soap_GetSites(self, ps):
        """
        implementation of the "GetSites" operation
        specification:
        if empty input sitecode, return all the sites
        if multiple inpute sitecodes, return the corresponding sites
        """
        try:
            rsp = WaterOneFlow.soap_GetSites(self,ps)
            request = self.request
            #get input parameter, save it in a string list strSiteCodeList.
            siteCodeList = request.get_element_site()
            strSiteCodeList = map(str,siteCodeList.get_element_string())
            #construct/renew the siteInfo_site_dictionary.
            #currently, renew it every 14 days (subject to change)?
            if(len(siteInfo_site_dictionary.keys())==1 or 
                    datetime.now() >= siteInfo_site_dictionary["__modTime"] + timedelta(days=14)):
                #here has a possible race condition, so a lock is placed
                semaphore = open('/home/txhis/CBIService/semaphore/semaphore.file', "w")
                lock(semaphore, LOCK_EX)
                treeIter = getIterator(centralRegUrl)
                #save the srs information in dictionary
                buildSiteInfo_siteDictionary(treeIter,siteInfo_site_dictionary)
                siteInfo_site_dictionary["__modTime"]=datetime.now()
                #close semaphore, release the lock file. (otherwise deadlock will be possible)
                semaphore.close()            
            #construct siteResponseNode XML node    
            siteResponseNode = rsp.new_sitesResponse()
            #construct the queryInfo XML node part. It is ofen used, so make it a function
            genQueryInfo(siteResponseNode,"location",','.join(strSiteCodeList))
            #get the "key" part, ready to match in cached dictionary:
            def getKeyPart(str): 
                tempstr = str.split(':')
                if tempstr[0] == 'CBI':return tempstr[1]
            #use map, get siteCode part of every string, saving a loop    
            strSiteCodeList = map(getKeyPart,strSiteCodeList)
            #Eliminate the "None" element
            strSiteCodeList = [i for i in strSiteCodeList if i]
            #site List array (if multiple sites)
            siteList = []
            #if input is empty, return all the Sites as the response
            if (not siteCodeList.get_element_string() or (not siteCodeList.get_element_string()[0] 
                    and len(siteCodeList.get_element_string())==1)):
                for key in siteInfo_site_dictionary.keys():
                    if key == "__modTime" or key == 'srs' : continue
                    #here, look at the documentation of site_info_dictionary of backEndhttpReqConstr
                    genSite_forGetSite(siteResponseNode,siteInfo_site_dictionary[key][1][0],
                                                key,siteInfo_site_dictionary[key][0],siteInfo_site_dictionary['srs'],siteList)
            #otherwise, only return the matched sites. Notice sites with non-existing 
            #sitecode will not return any sites node, which means the sites part could be empty
            else:               
                #Search the dictionary list, transforming the correspond XML node
                for siteCode in strSiteCodeList:
                    if siteInfo_site_dictionary.has_key(siteCode):
                    #find site with the sitecode in cache, generating XML node
                        genSite_forGetSite(siteResponseNode,siteInfo_site_dictionary[siteCode][1][0],
                                                siteCode,siteInfo_site_dictionary[siteCode][0],siteInfo_site_dictionary['srs'],siteList)
            siteResponseNode.set_element_site(siteList)                
            rsp.set_element_sitesResponse(siteResponseNode)                      
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout)
        return rsp
    #GetSitesXML method:
    def soap_GetSitesXml(self, ps):
        """
        implementation of the "GetSites" operation
        specification:
        if empty input sitecode, return all the sites
        if multiple inpute sitecodes, return the corresponding sites
        """
        try:
            #this code is just for deploying on apache
            #httpReq = kw['request']
            rsp = WaterOneFlow.soap_GetSitesXml(self,ps)
            request = self.request
            #get input parameter, save it in a string list strSiteCodeList.
            siteCodeList = request.get_element_site()
            strSiteCodeList = map(str,siteCodeList.get_element_string())
            #construct/renew the siteInfo_site_dictionary.
            #currently, renew it every 14 days (subject to change)?
            if(len(siteInfo_site_dictionary.keys())==1 or 
                    datetime.now() >= siteInfo_site_dictionary["__modTime"] + timedelta(days=14)):
                #here has a possible race condition, so a lock is placed
                semaphore = open('/home/txhis/CBIService/semaphore/semaphore.file', "w")
                lock(semaphore, LOCK_EX)
                treeIter = getIterator(centralRegUrl)
                #save the srs information in dictionary
                buildSiteInfo_siteDictionary(treeIter,siteInfo_site_dictionary)
                siteInfo_site_dictionary["__modTime"]=datetime.now()
                #close semaphore, release the lock file. (otherwise deadlock will be possible)
                semaphore.close()
            # Generate XML String
            #big response node
            siteResponse = SiteInfoResponseType()
            #set queryInfo
            queryInfo = generateQueryInfo_string(request.get_element_site());
            siteResponse.set_queryInfo(queryInfo)
            #get the "key" part, ready to match in cached dictionary:
            def getKeyPart(str): 
                tempstr = str.split(':')
                if tempstr[0] == 'CBI':return tempstr[1]
            #use map, get siteCode part of every string, saving a loop    
            strSiteCodeList = map(getKeyPart,strSiteCodeList)
            #Eliminate the "None" element
            strSiteCodeList = [i for i in strSiteCodeList if i]
            #site List array (if multiple sites)
            siteList = []
            # read this logic:
            #if input is empty, return all the Sites as the response
            if (not siteCodeList.get_element_string() or (not siteCodeList.get_element_string()[0] 
                    and len(siteCodeList.get_element_string())==1)):
                for key in siteInfo_site_dictionary.keys():
                    if key == "__modTime" or key == 'srs' : continue
                    #site nodes
                    siteNode = site()
                    #siteCodeArray[1]][1][1] is an arbitrary xml node of a certain location
                    siteInfoNode = generateSiteInfo_string(siteInfo_site_dictionary[key][1][0],siteInfo_site_dictionary['srs'])
                    siteNode.set_siteInfo(siteInfoNode)
                    siteList.append(siteNode)
            siteResponse.set_site(siteList) 
            siteResponseString = cStringIO.StringIO()                               
            siteResponse.export(siteResponseString, 0, \
                                     namespacedef_=' '.join(['xmlns:gml="http://www.opengis.net/gml"',
                                                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                                                   'xmlns:xlink="http://www.w3.org/1999/xlink"',
                                                   'xmlns:wtr="http://www.cuahsi.org/waterML/"',
                                                   'xmlns:xsd="http://www.w3.org/2001/XMLSchema"',
                                                   'xmlns="http://www.cuahsi.org/waterML/1.0/"']))        
            rsp.set_element_GetSitesXmlResult(siteResponseString.getvalue())
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout)
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp    
    #GetSiteInfo method
    def soap_GetSiteInfo(self, ps):
        """
        implementation of the "GetSiteInfo" operation
        """
        try:
            #this code is just for deploying on apache
            #httpReq = kw['request']
            rsp = WaterOneFlow.soap_GetSiteInfo(self,ps)
            request = self.request
            #construct/renew the siteInfo_site_dictionary.
            #currently, renew it every 14 days (subject to change)?
            if(len(siteInfo_site_dictionary.keys())==1 or 
                    datetime.now() >= siteInfo_site_dictionary["__modTime"] + timedelta(days=14)):
                #here has a possible race condition, so a lock is placed
                semaphore = open('/home/txhis/CBIService/semaphore/semaphore.file', "w")
                lock(semaphore, LOCK_EX)
                treeIter = getIterator(centralRegUrl)
                #save the srs information in dictionary
                buildSiteInfo_siteDictionary(treeIter,siteInfo_site_dictionary)
                siteInfo_site_dictionary["__modTime"]=datetime.now()
                #close semaphore, release the lock file. (otherwise deadlock will be possible)
                semaphore.close()            
            #get input parameter, save it in a string siteCode.
            siteCodeArray = map(str, request.get_element_site().split(":"))
            #print len(siteInfo_site_dictionary["001"][1])
            if  len(siteCodeArray) < 2 or\
                    not siteInfo_site_dictionary.has_key(siteCodeArray[1]) or \
                    not siteCodeArray[0].upper() == "CBI":
                fault = Fault(Fault.Client, "Illegal SiteCode", actor="SiteCode", detail="site code \"%s\" is illegal/not found" % ":".join(siteCodeArray))
                raise fault
            else:
                #big response node
                siteResponse = SiteInfoResponseType()
                #set queryInfo
                queryInfo = generateQueryInfo_string(request.get_element_site());
                siteResponse.set_queryInfo(queryInfo)
                #site nodes
                siteNode = site()
                #siteCodeArray[1]][1][1] is an arbitrary xml node of a certain location
                siteInfoNode = generateSiteInfo_string(siteInfo_site_dictionary[siteCodeArray[1]][1][1],siteInfo_site_dictionary['srs'])
                siteNode.set_siteInfo(siteInfoNode)                
                #seriesCatalog node
                seriesCatalogNode = seriesCatalogType()
                seriesCatalogNode.set_menuGroupName("CBI Observation Data")
                seriesCatalogNode.set_serviceWsdl(WSDLAddress)
                #here, to be completed
                seriresList = []
                for xmlNode in siteInfo_site_dictionary[siteCodeArray[1]][1]:
                    seriresList.append(generateSeriesNode(xmlNode))
                seriesCatalogNode.set_series(seriresList)
                #
                siteNode.set_seriesCatalog([seriesCatalogNode])
                siteResponse.set_site([siteNode])
                #actual xml string
                siteResponseString = cStringIO.StringIO()
                #                                
                siteResponse.export(siteResponseString, 0, \
                                     namespacedef_=' '.join(['xmlns:gml="http://www.opengis.net/gml"',
                                                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                                                   'xmlns:xlink="http://www.w3.org/1999/xlink"',
                                                   'xmlns:wtr="http://www.cuahsi.org/waterML/"',
                                                   'xmlns:xsd="http://www.w3.org/2001/XMLSchema"',
                                                   'xmlns="http://www.cuahsi.org/waterML/1.0/"']))
                rsp.set_element_GetSiteInfoResult(siteResponseString.getvalue()) 
                #generating corresponding WaterML xml string here    
        #here, how to generate a fault!!!           
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
    #GetSiteInfoObj method
    def soap_GetSiteInfoObject(self, ps):
        """
        implementation of the "GetSiteInfoObject" operation
        """
        try:
            rsp = WaterOneFlow.soap_GetSiteInfoObject(self,ps)
            request = self.request
            #construct/renew the siteInfo_site_dictionary.
            #currently, renew it every 14 days (subject to change)?
            if(len(siteInfo_site_dictionary.keys())==1 or 
                    datetime.now() >= siteInfo_site_dictionary["__modTime"] + timedelta(days=14)):
                #here has a possible race condition, so a lock is placed
                semaphore = open('/home/txhis/CBIService/semaphore/semaphore.file', "w")
                lock(semaphore, LOCK_EX)
                treeIter = getIterator(centralRegUrl)
                #save the srs information in dictionary
                buildSiteInfo_siteDictionary(treeIter,siteInfo_site_dictionary)
                siteInfo_site_dictionary["__modTime"]=datetime.now()
                #close semaphore, release the lock file. (otherwise deadlock will be possible)
                semaphore.close()
            #get input parameter, save it in a string siteCode.
            siteCodeArray = map(str, request.get_element_site().split(":"))
            #print len(siteInfo_site_dictionary["001"][1])
            if  len(siteCodeArray) < 2 or\
                    not siteInfo_site_dictionary.has_key(siteCodeArray[1]) or \
                    not siteCodeArray[0].upper() == "CBI":
                fault = Fault(Fault.Client, "Illegal SiteCode", actor="SiteCode", detail="site code \"%s\" is illegal/not found" % ":".join(siteCodeArray))
                raise fault
            else:
                #construct siteResponseNode XML node    
                siteResponseNode = rsp.new_sitesResponse()
                #construct the queryInfo XML node part. It is ofen used, so make it a function
                genQueryInfo(siteResponseNode,"location",','.join(siteCodeArray))                       
                #site List array (if multiple sites)
                siteList = []
                try:
                    genSite_forGetSite(siteResponseNode,siteInfo_site_dictionary[siteCodeArray[1]][1][0],
                                                siteCode,siteInfo_site_dictionary[siteCodeArray[1]][0],siteInfo_site_dictionary['srs'],siteList)
                except:
                    fault = Fault(Fault.Client, "Illegal SiteCode", actor="SiteCode", detail="site code \"%s\" is illegal/not found" % ":".join(siteCodeArray))    
                    raise fault
            #seriesCatalog node
            seriesCatalogNode = siteList[0].new_seriesCatalog()
            seriesCatalogNode._attrs = dict(menuGroupName="CBI Observation Data", serviceWsdl = WSDLAddress) 
            #here, to be completed
            seriresList = []
            for xmlNode in siteInfo_site_dictionary[siteCodeArray[1]][1]:
                seriresList.append(generateSeriesNodeObj(xmlNode,seriesCatalogNode))
            seriesCatalogNode.set_element_series(seriresList)
            siteList[0].set_element_seriesCatalog([seriesCatalogNode])
            siteResponseNode.set_element_site(siteList) 
            rsp.set_element_sitesResponse(siteResponseNode)                       
        #here, how to generate a fault!!!           
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
            
    #GetVariableInfo method
    def soap_GetVariableInfo(self, ps):
        """
        implementation of the "GetVariableInfo" operation
        """
        try:
            rsp = WaterOneFlow.soap_GetVariableInfo(self,ps)
            request = self.request
            variableCodeArray = map(str, request.get_element_variable().split(":"))
            #if pass in empty string, show info of all variables
            variablesNode = variables()
            #for the variable list
            variableList = []
            if variableCodeArray == [""]:
                for key in variable_Dictionary.keys():
                    #notice here the protocol of function generateVariableTypeNodeString
                    variableList.append(generateVariableTypeNodeString(key,variable_Dictionary[key]))
            elif not variableCodeArray[0].upper()=="CBI"  or not variable_Dictionary.has_key(variableCodeArray[1]) \
                    or len(variableCodeArray) != 2:
                fault = Fault(Fault.Client, "Illegal variableCode", actor="variableCode", detail="variable code \"%s\" is illegal/not found" % ":".join(variableCodeArray))
                raise fault
            elif variable_Dictionary.has_key(variableCodeArray[1]):
                variableList.append(generateVariableTypeNodeString(variableCodeArray[1],variable_Dictionary[variableCodeArray[1]]))
            #here, to decide if queryInfo required 
            variablesNode.set_variable(variableList)
            variableResponseNode = VariablesResponseType()
            variableResponseNode.set_variables(variablesNode)     
            #actual xml string
            variableResponseString = cStringIO.StringIO()
            #                                
            variableResponseNode.export(variableResponseString, 0, \
                                     namespacedef_=' '.join(['xmlns:gml="http://www.opengis.net/gml"',
                                                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                                                   'xmlns:xlink="http://www.w3.org/1999/xlink"',
                                                   'xmlns:wtr="http://www.cuahsi.org/waterML/"',
                                                   'xmlns:xsd="http://www.w3.org/2001/XMLSchema"',
                                                   'xmlns="http://www.cuahsi.org/waterML/1.0/"']))
            rsp.set_element_GetVariableInfoResult(variableResponseString.getvalue())
        #here, how to generate a fault!!!           
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
    #GetVariableInfoObject method
    def soap_GetVariableInfoObject(self, ps):
        """
        implementation of the "GetVariableInfo" operation
        """
        try:
            #this code is just for deploying on apache
            #httpReq = kw['request']
            rsp = WaterOneFlow.soap_GetVariableInfoObject(self,ps)
            request = self.request            
            variableCodeArray = map(str, request.get_element_variable().split(":"))
            variableResponseNode=rsp.new_variablesResponse()
            variablesNode = variableResponseNode.new_variables()
            variableList = []             
            if variableCodeArray == [""]:
                for key in variable_Dictionary.keys():
                    variableNode = variablesNode.new_variable()
                    variableList.append(generateVariableTypeNode(variableNode,key,variable_Dictionary[key]))
            elif not variableCodeArray[0].upper()=="CBI"  or not variable_Dictionary.has_key(variableCodeArray[1]) \
                    or len(variableCodeArray) != 2:
                fault = Fault(Fault.Client, "Illegal variableCode", actor="variableCode", detail="variable code \"%s\" is illegal/not found" % ":".join(variableCodeArray))
                raise fault
            elif variable_Dictionary.has_key(variableCodeArray[1]):
                variableNode = variablesNode.new_variable()
                variableList.append(generateVariableTypeNode(variableNode,variableCodeArray[1],variable_Dictionary[variableCodeArray[1]]))
            variablesNode.set_element_variable(variableList)
            variableResponseNode.set_element_variables(variablesNode)
            rsp.set_element_variablesResponse(variableResponseNode)
        #here, how to generate a fault!!!           
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
    def soap_GetValues(self,ps):
        """
        implementation of the "GetValues" operation
        """
        try:
            #this code is just for deploying on apache
            #httpReq = kw['request']
            rsp = WaterOneFlow.soap_GetValues(self,ps)
            request = self.request 
            #get input variable
            siteCodeUnicodeStr = request.get_element_location()
            variableCodeUnicodStr = request.get_element_variable()
            startDate = request.get_element_startDate()
            endDate = request.get_element_endDate()
            #construct/renew the siteInfo_site_dictionary.
            #currently, renew it every 14 days (subject to change)?
            if(len(siteInfo_site_dictionary.keys())==1 or 
                    datetime.now() >= siteInfo_site_dictionary["__modTime"] + timedelta(days=14)):
                #here has a possible race condition, so a lock is placed
                semaphore = open('/home/txhis/CBIService/semaphore/semaphore.file', "w")
                lock(semaphore, LOCK_EX)
                treeIter = getIterator(centralRegUrl)
                #save the srs information in dictionary
                buildSiteInfo_siteDictionary(treeIter,siteInfo_site_dictionary)
                siteInfo_site_dictionary["__modTime"]=datetime.now()
                #close semaphore, release the lock file. (otherwise deadlock will be possible)
                semaphore.close()
            #some basic error checking
            #validity of siteCode:
            siteCodeArray = map(str,siteCodeUnicodeStr.split(":"))
            if  len(siteCodeArray) < 2 or\
                    not siteInfo_site_dictionary.has_key(siteCodeArray[1]) or \
                    not siteCodeArray[0].upper() == "CBI":
                fault = Fault(Fault.Client, "Illegal SiteCode", actor="SiteCode", detail="site code \"%s\" is illegal/not found" % ":".join(siteCodeArray))
                raise fault
            #check validity of variableCode
            variableCodeArray = map(str, variableCodeUnicodStr.split(":"))
            if  len(variableCodeArray) < 2 or\
                    not variable_Dictionary.has_key(variableCodeArray[1]) or \
                    not variableCodeArray[0].upper() == "CBI":
                fault = Fault(Fault.Client, "Illegal VariableCode", actor="Variable", detail="variable code \"%s\" is illegal/not found" % ":".join(variableCodeArray))
                raise fault
            #preprocessing passing-in time
            if startDate == "":
                startDate = (datetime.now()-timedelta(years=float(100))).__str__()
            if endDate == "":
                endDate = datetime.now().__str__()              
            #time format validation
            try:
                time.strptime(startDate,"%Y-%m-%d")
                time.strptime(endDate,"%Y-%m-%d")
            except:
                fault = Fault(Fault.Client, "Illegal start/end Date", actor="startDate/endDate", \
                                  detail="The format of starDate/endDate string is illegal, please use format 'YYYY-MM-DD HH:MM:S'(CST timezone) error startDate: %s   erro endDate: %s " %(startDate,endDate))
                raise fault
            ##################################################################################################################################################
            #timeSeries type
            timeSeriesResponseNode = TimeSeriesResponseType()
            #generate return XML info
            queryInfoNode = QueryInfoType()
            #here, set creation time in ZULU zone
            #get the UTC time for now
            nowTime = datetime.now()+ timedelta(hours=float(6))
            strNowTime = "".join(["T".join(str(nowTime)[:str(nowTime).index(".")].split()),"Z"])
            queryInfoNode.set_creationTime(strNowTime)
            queryInfoNode.set_queryURL(getCBIURLqueryString(siteCodeArray[1],variableCodeArray[1],startDate,endDate))
            #criteria Node
            criteriaNode = criteria()
            criteriaNode.set_locationParam(":".join(siteCodeArray))
            criteriaNode.set_variableParam(":".join(variableCodeArray))
            #time parameter
            timeParamNode = timeParam()
            timeParamNode.set_beginDateTime(startDate)
            timeParamNode.set_endDateTime(endDate)
            criteriaNode.set_timeParam(timeParamNode)
            queryInfoNode.set_criteria(criteriaNode)
            timeSeriesResponseNode.set_queryInfo(queryInfoNode)
            #time series node
            timeSeriesNode = TimeSeriesType()
            SourceInfoType.subclass = SiteInfoType
            sourceInfoNode = SourceInfoType.factory()
            sourceInfoNode.set_siteName(siteInfo_site_dictionary[siteCodeArray[1]][0].strip())
            #get any of the xmlNode
            xmlNode = siteInfo_site_dictionary[siteCodeArray[1]][1][0]
            #set site code
            siteCodeNode = siteCode()
            siteCodeNode.set_network("CBI")
            siteCodeNode.set_siteID(xmlNode[4].text.split(":")[0])
            siteCodeNode.setValueOf_(xmlNode[4].text.split(":")[0])
            sourceInfoNode.set_siteCode([siteCodeNode])
            ##
            timeZoneInfoNode = timeZoneInfo()
            timeZoneInfoNode.set_defaultTimeZone("CST")
            timeZoneInfoNode.set_daylightSavingsTimeZone("Unkown")
            sourceInfoNode.set_timeZoneInfo(timeZoneInfoNode)
            #set geolocation
            geoLocationNode = geoLocation()
            #set inner geoglocation
            GeogLocationType.subclass=LatLonPointType
            innerGeoLocationNode = GeogLocationType.factory()
            innerGeoLocationNode.set_srs(siteInfo_site_dictionary['srs'])
            innerGeoLocationNode.set_latitude(xmlNode[5][0][0].text.split()[0])
            innerGeoLocationNode.set_longitude(xmlNode[5][0][0].text.split()[1])
            geoLocationNode.set_geogLocation(innerGeoLocationNode)
            #set node here         
            sourceInfoNode.set_geoLocation(geoLocationNode)
            sourceInfoNode.set_verticalDatum(xmlNode[7].text)
            #countyNote = NoteType(title='County',valueOf_=':'.join(["CBI","Coastal Water Data"]))
            stateNote = NoteType(title='State',valueOf_='Texas')
            commentNote = NoteType(title='Comment',valueOf_=xmlNode[15].text)
            sourceInfoNode.set_note([stateNote,commentNote])
            timeSeriesNode.set_sourceInfo(sourceInfoNode)
            ###################################################
            #variable node
            variableNode = generateVariableTypeNodeString(variableCodeArray[1],variable_Dictionary[variableCodeArray[1]])
            timeSeriesNode.set_variable(variableNode)
            #values node
            try:
                valuesNode=generateSeriesValueList(siteCodeArray[1],variableCodeArray[1],startDate,endDate)
                timeSeriesNode.set_values(valuesNode)
            except:
                fault = Fault(Fault.Client, "Bad requirement", actor="input_parameters", \
                                  detail="Invalid input parameters.Please chek the input parameters: (sitecode, variablecode, startdate, enddate)")
                raise fault
            #################           
            timeSeriesResponseNode.set_timeSeries(timeSeriesNode) 
            #actual xml string
            timeSeriesResponseString = cStringIO.StringIO()
            #export the xml string                                 
            timeSeriesResponseNode.export(timeSeriesResponseString, 0, \
                                     namespacedef_=' '.join(['xmlns:gml="http://www.opengis.net/gml"',
                                                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                                                   'xmlns:xlink="http://www.w3.org/1999/xlink"',
                                                   'xmlns:wtr="http://www.cuahsi.org/waterML/"',
                                                   'xmlns:xsd="http://www.w3.org/2001/XMLSchema"',
                                                   'xmlns="http://www.cuahsi.org/waterML/1.0/"']))
            print timeSeriesResponseString.getvalue()
            rsp.set_element_GetValuesResult(timeSeriesResponseString.getvalue())                                      
        #here, how to generate a fault!!!           
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
    #implementation of GetValuesObj
    def soap_GetValuesObject(self, ps):
        """
        implementation of the "GetValues" operation
        """
        try:
            #this code is just for deploying on apache
            #httpReq = kw['request']
            rsp = WaterOneFlow.soap_GetValuesObject(self,ps)
            request = self.request 
            #get input variable
            siteCodeUnicodeStr = request.get_element_location()
            variableCodeUnicodStr = request.get_element_variable()
            startDate = request.get_element_startDate()
            endDate = request.get_element_endDate()
            #construct/renew the siteInfo_site_dictionary.
            #currently, renew it every 14 days (subject to change)?
            if(len(siteInfo_site_dictionary.keys())==1 or 
                    datetime.now() >= siteInfo_site_dictionary["__modTime"] + timedelta(days=14)):
                #here has a possible race condition, so a lock is placed
                semaphore = open('/home/txhis/CBIService/semaphore/semaphore.file', "w")
                lock(semaphore, LOCK_EX)
                treeIter = getIterator(centralRegUrl)
                #save the srs information in dictionary
                buildSiteInfo_siteDictionary(treeIter,siteInfo_site_dictionary)
                siteInfo_site_dictionary["__modTime"]=datetime.now()
                #close semaphore, release the lock file. (otherwise deadlock will be possible)
                semaphore.close()
            #some basic error checking
            #validity of siteCode:
            siteCodeArray = map(str,siteCodeUnicodeStr.split(":"))
            if  len(siteCodeArray) < 2 or\
                    not siteInfo_site_dictionary.has_key(siteCodeArray[1]) or \
                    not siteCodeArray[0].upper() == "CBI":
                fault = Fault(Fault.Client, "Illegal SiteCode", actor="SiteCode", detail="site code \"%s\" is illegal/not found" % ":".join(siteCodeArray))
                raise fault
            #check validity of variableCode
            variableCodeArray = map(str, variableCodeUnicodStr.split(":"))
            if  len(variableCodeArray) < 2 or\
                    not variable_Dictionary.has_key(variableCodeArray[1]) or \
                    not variableCodeArray[0].upper() == "CBI":
                fault = Fault(Fault.Client, "Illegal VariableCode", actor="Variable", detail="variable code \"%s\" is illegal/not found" % ":".join(variableCodeArray))
                raise fault
            #preprocessing passing-in time
            if startDate == "":
                startDate = (datetime.now()-timedelta(years=float(100))).isoformat()
            if endDate == "":
                endDate = datetime.now().isoformat()              
            #time format validation
            try:
                time.strptime(startDate,"%Y-%m-%d")
                time.strptime(endDate,"%Y-%m-%d")
            except:
                fault = Fault(Fault.Client, "Illegal start/end Date", actor="startDate/endDate", \
                                  detail="The format of starDate/endDate string is illegal, please use format 'YYYY-MM-DDTHH:MM:S'(CST timezone) error startDate: %s   erro endDate: %s " %(startDate,endDate))
                raise fault
            ##################################################################################################################################################
            #timeSeries type
            timeSeriesResponseNode = rsp.new_timeSeriesResponse()
            #generate return XML info
            queryInfoNode = timeSeriesResponseNode.new_queryInfo()
            #here, set creation time in ZULU zone
            #get the UTC time for now
            nowTime = datetime.now()+ timedelta(hours=float(6))
            strNowTime = "".join(["T".join(str(nowTime)[:str(nowTime).index(".")].split()),"Z"])
            queryInfoNode.set_element_creationTime(strNowTime)
            queryInfoNode.set_element_queryURL(getCBIURLqueryString(siteCodeArray[1],variableCodeArray[1],startDate,endDate))
            #criteria Node
            criteriaNode = queryInfoNode.new_criteria()
            criteriaNode.set_element_locationParam(":".join(siteCodeArray))
            criteriaNode.set_element_variableParam(":".join(variableCodeArray))
            #time parameter
            timeParamNode = criteriaNode.new_timeParam()
            timeParamNode.set_element_beginDateTime(startDate)
            timeParamNode.set_element_endDateTime(endDate)
            criteriaNode.set_element_timeParam(timeParamNode)
            queryInfoNode.set_criteria(criteriaNode)
            timeSeriesResponseNode.set_element_queryInfo(queryInfoNode)
            #time series node
            timeSeriesNode = timeSeriesResponseNode.new_timeSeries()
            #.......................................................
            rsp.set_element_timeSeriesResponse(timeSeriesResponseNode)
        except Exception, e:
            import traceback
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
                    
