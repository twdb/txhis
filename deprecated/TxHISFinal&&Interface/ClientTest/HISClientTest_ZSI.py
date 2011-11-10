'''
Created on Oct 8, 2010

@author: CTtan
'''
from TxHISCentralRegistry_services_types import *
from TxHISCentralRegistry_services import *

def GetSources():
    HISCentralServiceLocator = TxHISCentralRegistryLocator()
    HISCentralServiceProxy = HISCentralServiceLocator.getTxHISCentralRegistry("http://midgewater.twdb.state.tx.us/appsWS/TXHISCentralService?wsdl")
    request = GetSourcesGEMSSRequest()
    response = HISCentralServiceProxy.GetSourcesGEMSS(request)
    for i in response.get_element_ServiceDetail():
        print "WSDLlink:", i.get_element_RemoteSourceURL()
        print "SourceFormat:", i.get_element_SourceFormat()
        print "NetworkName:", i.get_element_RemoteSourceNetWorkName()
        print "UpdateFrequencyType:", i.get_element_UpdateFrequencyType()
        print "UpdateFrequencyValue:", i.get_element_SourceSummarizedDescription()
        print "SourceSummarizedDescription:", i.get_element_SourceSummarizedDescription()
        print "SourceDescriptionLink:", i.get_element_SourceDescriptionLink()
        print "SourceLogoLink:", i.get_element_SourceLogoLink()
        print "Available parameter codes:", [str(j) for j in i.get_element_RemoteSourceParameterCodes().get_element_SourceParameterCode()]
        


def GetConvertedOutput():
    HISCentralServiceLocator = TxHISCentralRegistryLocator()
    HISCentralServiceProxy = HISCentralServiceLocator.getTxHISCentralRegistry("http://midgewater.twdb.state.tx.us/appsWS/TXHISCentralService?wsdl")
    request = GetTXHISConvertedOutputGEMSSRequest()
    request.set_element_RemoteSourceURL("http://riodev/appsWS/HisTpwdCoastal/cuahsi_1_0.asmx?WSDL")
    request.set_element_RemoteSourceNetworkName("TPWD_CoastalWQ")
    request.set_element_RemoteSourceParameterCode("TEM001")
    RemoteValues = request.new_RemoteValues()
    RemoteValues.set_element_value([1.1,2.2,3.4])
    request.set_element_RemoteValues(RemoteValues)
    response = HISCentralServiceProxy.GetTXHISConvertedOutputGEMSS(request).get_element_TXHISResponseObj()
    print "HISParameterName: ", response.get_element_TXHISParameterName()
    print "HISParameterCode: ", response.get_element_TXHISParameterCode()
    print "HISParameterDescprition: ", response.get_element_TXHISParameterDescription()
    print "HISParameterUnit: ", response.get_element_TXHISParameterUnit()
    print "HISParameterUnitDescription: ", response.get_element_TXHISParameterUnitDescription()
    print "HISConvertedValue: ", [i for i in response.get_element_TXHISParameterValues().get_element_value()]
    
    

if __name__ == "__main__":
    GetSources()
    GetConvertedOutput()   