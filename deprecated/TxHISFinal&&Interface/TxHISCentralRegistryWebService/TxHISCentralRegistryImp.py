'''
Created on Oct 6, 2010

@author: Tony Tan (CTtan) 
'''
from TxHISCentralRegistry_services_server import *
from ZSI.writer import SoapWriter
from ZSI import ServiceContainer, Fault, ParsedSoap 
from ZSI.fault import Fault, FaultType, Detail
import cStringIO 

from sqlalchemy import orm,and_
from sqlalchemy.orm import join
from sqlalchemy.orm.exc import NoResultFound

import os,sys,traceback,datetime
 
sys.path.append('..')


from DatabaseModel.model import *

WS_PATH = 'TXHISCentralService'

#service implementation
class TxHISCentralRegistryImp(TxHISCentralRegistry):
    def __init__(self,post=WS_PATH):
        TxHISCentralRegistry.__init__(self, post)
    # GetSourcesGEMSS implementations
    def soap_GetSourcesGEMSS(self, ps):
        try:
            rsp = TxHISCentralRegistry.soap_GetSourcesGEMSS(self, ps)
            request = self.request
            #Initializing returning ServiceDetail array
            ServiceDetailsArray = []
            AllSourcesQSet = self.dbsession.query(Sources).all()
            for source in AllSourcesQSet:
                sourceDetail = rsp.new_ServiceDetail()
                sourceDetail.set_element_RemoteSourceURL(source.WSDLLink)
                sourceDetail.set_element_RemoteSourceNetWorkName(source.NetworkName)
                sourceDetail.set_element_SourceFormat(source.SourceFormat)
                sourceDetail.set_element_UpdateFrequencyType(source.UpdateFrequencyType)
                sourceDetail.set_element_UpdateFrequencyValue(source.UpdateFrequencyValue)
                #sourceDetail.set_element_LastUpdatedOn(source.LastUpdatedOn.timetuple())
                sourceDetail.set_element_SourceSummarizedDescription(source.SourceSummerizedDescription)
                #sourceDetail.set_element_SourceDetailedDescription(source.SourceDetailedDescription)
                sourceDetail.set_element_SourceDescriptionLink(source.DescriptionLink)
                sourceDetail.set_element_SourceLogoLink(source.LogoLink)
                remoteParameterCodeArray = sourceDetail.new_RemoteSourceParameterCodes()
                #print source.availableParameterInfo, len(source.availableParameterInfo)
                remoteParameterCodeArray.set_element_SourceParameterCode([i.RemoteVariableCode for i in source.availableParameterInfo])
                sourceDetail.set_element_RemoteSourceParameterCodes(remoteParameterCodeArray)
                ServiceDetailsArray.append(sourceDetail)
            rsp.set_element_ServiceDetail(ServiceDetailsArray)         
        except Exception, e:
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
    # GetTXHISConvertedOutputGEMSS implementation
    def soap_GetTXHISConvertedOutputGEMSS(self, ps):
        try:
            rsp = TxHISCentralRegistry.soap_GetTXHISConvertedOutputGEMSS(self, ps)
            request = self.request
            #extract input
            RemoteSourceURL = request.get_element_RemoteSourceURL()
            RemoteSourceNetworkName = request.get_element_RemoteSourceNetworkName()
            RemoteSourceParameterCode = request.get_element_RemoteSourceParameterCode()
            RemoteValues = request.get_element_RemoteValues().get_element_value()
            #Query database, get parameter mapping
            #  todo:   and unit conversion
            try:
                FindSource = self.dbsession.query(Sources).filter(Sources.WSDLLink == RemoteSourceURL ) \
                                        .filter(Sources.NetworkName == RemoteSourceNetworkName).one()
                VarMapping = [i for i in FindSource.availableParameterInfo if i.RemoteVariableCode == RemoteSourceParameterCode][0] 
            except (NoResultFound, IndexError), e:
                fault = Fault(Fault.Client, "Illegal Source/RemoteParameterCode", actor="Source/RemoteParameterCode", detail=None)
                raise fault
            else:
                # here, do unit conversion formula look-up
                # assumption:
                #    1. If source unit and destination unit are the same, no formula needed in the
                #       lookup table, to a plain in = out
                #    2. if for some reason, formula hasn't been put into the formula table, also do
                #       a plain in = out
                #    3. if formula found, eval() it, get the formula function, map it to the input list
                try:
                    UnitFormula = eval(self.dbsession.query(UnitConversionFormula).filter(UnitConversionFormula.SourceUnitsID == VarMapping.RemoteUnitsID)\
                                        .filter(UnitConversionFormula.DestinationUnitsID == VarMapping.STDcentralVariableInfo.VariableUnitsID).one().ConversionFormula)
                except NoResultFound, e:
                    UnitFormula = (lambda x : x)                    
                returnObj = rsp.new_TXHISResponseObj()
                returnObj.set_element_TXHISParameterName(VarMapping.STDcentralVariableInfo.VariableName)
                returnObj.set_element_TXHISParameterCode(VarMapping.STDcentralVariableInfo.VariableCode)
                returnObj.set_element_TXHISParameterDescription("Somedescription")
                returnObj.set_element_TXHISParameterUnit(VarMapping.STDcentralVariableInfo.UnitInfo.UnitsName)
                returnObj.set_element_TXHISParameterUnitDescription("UnitDescription")
                unitConvertedValue = returnObj.new_TXHISParameterValues()
                unitConvertedValue.set_element_value(map(UnitFormula,RemoteValues))
                returnObj.set_element_TXHISParameterValues(unitConvertedValue) 
                rsp.set_element_TXHISResponseObj(returnObj)              
        except Exception, e:
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp    
    # op: GetTXHISParameters
    def soap_GetTXHISParameters(self, ps):
        try:
            rsp = TxHISCentralRegistry.soap_GetTXHISParameters(self, ps)
            request = self.request
            #initialize the return XML list node
            parameterList = rsp.new_ParameterList()
            variableSet = self.dbsession.query(Variables).all()
            #initialize the python list to be set
            parameterInstanceList = []
            #initialize each network instance node
            for variable in variableSet:
                parameterInstance = parameterList.new_ParameterInstance()
                parameterInstance.set_element_ParameterCode(variable.VariableCode)
                parameterInstance.set_element_ParameterName(variable.VariableName)
                parameterInstanceList.append(parameterInstance)
            #here, set element with python list
            parameterList.set_element_ParameterInstance(parameterInstanceList)
            rsp.set_element_ParameterList(parameterList)
        except Exception, e:
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp 
    # op: soap_GetRemoteParameterCode
    def soap_GetRemoteParameterCode(self, ps):
        try:
            rsp = TxHISCentralRegistry.soap_GetRemoteParameterCode(self,ps)
            request = self.request
            #get the input argument
            RemoteSourceNetworkName = request.get_element_SourceNetworkName()
            TXHISParamCode = request.get_element_TXHISParameterCode()
            RemoteSourceURL    = request.get_element_WSDLLink()
            try:
                #database query
                FindSource = self.dbsession.query(Sources).filter(Sources.WSDLLink == RemoteSourceURL ) \
                                        .filter(Sources.NetworkName == RemoteSourceNetworkName).one()     
                VarMapping = [i for i in FindSource.availableParameterInfo if i.STDcentralVariableInfo.VariableCode == TXHISParamCode][0]
            except (NoResultFound, IndexError), e:
                #if the requested record is not present 
                #destParam = "invalid NetworkName or VariableCode"
                fault = Fault(Fault.Client, "Bad requirement", actor="input_parameters", \
                                  detail="invalid NetworkName, VariableCode and/or WSDLLink")
                raise fault
            #get the remote variable code and set the response value
            else:
                destParam = VarMapping.RemoteVariableCode    
            rsp.set_element_RemoteParameterCode(destParam)
        except Exception, e:
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
    # op:soap_GetHISParamAvailableSources 
    def soap_GetHISParamAvailableSources(self, ps):
        try:
            rsp = TxHISCentralRegistry.soap_GetHISParamAvailableSources(self, ps)
            request = self.request
            lookkupHISParamCode = request.get_element_HISParamCode()
            try:
                sourceMappingSet = self.dbsession.query(VariableMapping,Variables).filter(Variables.VariableID == VariableMapping.variable_id) \
                               .filter(Variables.VariableCode == lookkupHISParamCode).all()
            except NoResultFound, e:
                #if the requested record is not present 
                #destParam = "invalid NetworkName or VariableCode"
                fault = Fault(Fault.Clent, "Bad HIS ParameterCode", actor="Bad HIS ParameterCode", \
                                  detail="Bad HIS ParameterCode: Invalid HIS ParameterCode/No Source with this HIS ParameterCode")               
                raise Fault
            else:
                # here use a dictionary because a source can potentially have one
                # HISParameterCoded mapped to different remote parameter codes
                retSourceMapping = {}
                for sourceMapping in sourceMappingSet:
                    if not retSourceMapping.has_key(sourceMapping.VariableMapping.SourceInfo.NetworkName):
                        SourceWithParamCodeNode = rsp.new_SourceWithParamCodeInstance()
                        SourceWithParamCodeNode.set_element_WSDLLink(sourceMapping.VariableMapping.SourceInfo.WSDLLink)
                        SourceWithParamCodeNode.set_element_SourceName(sourceMapping.VariableMapping.SourceInfo.NetworkName)
                        remoteParamCode = [sourceMapping.VariableMapping.RemoteVariableCode]
                        retSourceMapping[sourceMapping.VariableMapping.SourceInfo.NetworkName] = (SourceWithParamCodeNode,remoteParamCode)
                    else:
                        retSourceMapping[sourceMapping.VariableMapping.SourceInfo.NetworkName][1].append(sourceMapping.VariableMapping.RemoteVariableCode)
                for key in retSourceMapping.keys():
                    retSourceMapping[key][0].set_element_RemoteParamCode(retSourceMapping[key][1])
                rsp.set_element_SourceWithParamCodeInstance([retSourceMapping[key][0] for key in retSourceMapping.keys()])        
        except Exception, e:
            traceback.print_exc(file=sys.stdout) 
            if isinstance(e,Fault):
                detail = None
                if e.detail is not None: 
                    detail = Detail()
                    detail.any = e.detail            
                rsp = FaultType(e.code, e.string, e.actor, detail)
        return rsp
    
    

if __name__ == "__main__":
    #print dbName
    print "Initializing Service Container..."
    TxHISCentralRegistryImp('TXHISCentralService')
    print "Service Container initialization successful..."
    
