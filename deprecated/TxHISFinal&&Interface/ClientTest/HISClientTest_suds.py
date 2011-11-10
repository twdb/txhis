'''
Created on Oct 8, 2010

@author: CTtan
'''
from suds.client import Client
wsdlurl = 'http://midgewater.twdb.state.tx.us/appsWS/TXHISCentralService?wsdl'
client = Client(wsdlurl)
print client
#client.set_options(location='http://greylin:9080/TXHISCentralService?wsdl')

#get all sources
Sources = client.service.GetSourcesGEMSS()
print Sources

#testing GetTXHISConvertedOutputGEMSS
RemoteValues = client.factory.create('ValuesArray')
RemoteValues.value = [1.0, 2.0]
#print RemoteValues
convertedOutput = client.service.GetTXHISConvertedOutputGEMSS('http://riodev/appsWS/HisTpwdCoastal/cuahsi_1_0.asmx?WSDL',
                                                              'TPWD','TEM001',RemoteValues)
print convertedOutput

