from suds.client import Client
#wsdlurl = 'http://his.crwr.utexas.edu/tcoonts/tcoon.asmx?WSDL'
#wsdlurl = 'http://his.crwr.utexas.edu/TRACS/cuahsi_1_0.asmx?WSDL'
#wsdlurl = 'http://his.crwr.utexas.edu/tpwd/cuahsi_1_0.asmx?WSDL'
#wsdlurl = 'http://his.crwr.utexas.edu/TWDB_Sondes/cuahsi_1_0.asmx?WSDL'
client = Client(wsdlurl)
print client

#get all sites
result = client.service.GetSites('','')

#get site info for one site
result1 = client.service.GetSiteInfo('TCOON:016','')

#get variable info for all variables
result2 = client.service.GetVariableInfo('','')

#get variable info for pwl
result3 = client.service.GetVariableInfo('TCOON:pwl','')

#get pwl values for sabine pass
pwldata = client.service.GetValues('TCOON:016','TCOON:pwl','2009-01-01','2009-09-01','')

#data = client.service.GetValues('TPWD:b17s3651m998','TPWD:SAL001','','','')
