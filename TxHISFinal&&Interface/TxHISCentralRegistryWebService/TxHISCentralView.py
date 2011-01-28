'''
Created on Oct 13, 2010

@author: CTtan
'''
import web,re,sys,traceback
from ZSI import ParseException, FaultFromException, FaultFromZSIException, Fault, resolvers
from ZSI.ServiceContainer import ServiceSOAPBinding
from ZSI.parse import ParsedSoap
from ZSI.writer import SoapWriter
from sqlalchemy.orm import scoped_session, sessionmaker

sys.path.append('..')

from TxHISCentralRegistryImp import TxHISCentralRegistryImp,WS_PATH
from DatabaseModel.syncdb import DBENGINE


#Exception classes, for better understanding of exceptions
class PostNotSpecified(Exception): pass
class NoSuchService(Exception): pass

_ZSISERVICECLS = TxHISCentralRegistryImp

#customize this to real WSURL
WSURLPREFIX = "/appsWS"

class GenericSOAPView:
    ServiceInstance = _ZSISERVICECLS(WS_PATH)
    def start_response(self,status, headers):
        web.ctx.status = status
        for header, value in headers:
            web.header(header, value)
    
    def GET(self):
        """
        The GET command.
        """         
        if web.ctx.fullpath.lower().endswith("?wsdl"):
            service_path = web.ctx.homepath
            service = self.ServiceInstance
            if hasattr(service, "_wsdl"):
                wsdl = service._wsdl
                # update the soap:location tag in the wsdl to the actual server
                #   location
                # - default to 'http' as protocol, or use server-specified protocol
                serviceUrl = '%s://%s%s' % (web.ctx.protocol,
                                                web.ctx.host,
                                                "".join([#WSURLPREFIX,
                                                         service_path]))
                soapAddress = '<soap:address location="%s"/>' % serviceUrl
                wsdlre = re.compile('\<soap:address[^\>]*>',re.IGNORECASE)
                wsdl = re.sub(wsdlre,soapAddress,wsdl)
                web.header('Content-Type', 'text/xml')
                return wsdl
            else:
                self.start_response('404 WSDL not found',[('Content-Type', 'text/html')])
                return ("WSDL not available for that service [%s]." % self.path)
        else:
            self.start_response('404 Service not found',[('Content-Type', 'text/html')])
            return ("Service not found at [%s]." % self.path)
        
    def POST(self):
        self.ServiceInstance.dbsession = web.ctx.orm
        soapAction = web.ctx.environ.get('HTTP_SOAPACTION')
        self.path = web.ctx.homepath[len(WSURLPREFIX):]
        if not self.path:
            raise PostNotSpecified, 'HTTP POST not specified in request'
        if soapAction:
            soapAction = soapAction.strip('\'"')
        self.path = self.path.strip('\'"')
        if web.ctx.environ['REQUEST_METHOD'].lower() != 'post':
            errMsg = '<h1>405 Method Not Allowed</h1>'
            self.start_response('405 Method Not Allowed',[('Content-Type', 'text/html'),
                                                          ('Content-Length', str(len(errMsg))),
                                                          ('Allow','POST')])
            return errMsg
        input = web.ctx.environ.get('wsgi.input')
        length = int(web.ctx.environ.get("CONTENT_LENGTH"))
        try:
            ct = web.ctx.environ.get('CONTENT_TYPE')
            if ct.startswith('multipart/'):
                cid = resolvers.MIMEResolver(ct, input)
                xml = cid.GetSOAPPart()
                ps = ParsedSoap(xml, resolver=cid.Resolve)
            else:
                xml = input.read(length)
                ps = ParsedSoap(xml)
        except ParseException, e:
            retXMLstr = FaultFromZSIException(e).AsSOAP()
            self.start_response('202 Accepted', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
            return retXMLstr
        except Exception, e:
            # Faulted while processing; assume it's in the header.
            retXMLstr = FaultFromException(e, 1, sys.exc_info()[2]).AsSOAP()
            self.start_response('202 Accepted', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
            return retXMLstr
        else:
            #self.start_response("200 OK", [('Content-Type', 'text/xml; charset="utf-8"')])
            # fill in "RPC" logic
            if isinstance(self.ServiceInstance, ServiceSOAPBinding) is False:
                e = NoSuchService('no service at POST(%s) in container: %s' %(web.ctx.path,web.ctx.host))
                retXMLstr = FaultFromException(e, 0, sys.exc_info()[2]).AsSOAP()
                self.start_response('202 Accepted', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
                return retXMLstr
            if not self.ServiceInstance.authorize(None, self.path, soapAction):
                retXMLstr = Fault(Fault.Server, "Not authorized").AsSOAP()
                self.start_response('401 Unauthorized', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
                return retXMLstr
            try:
                method = self.ServiceInstance.getOperation(ps, soapAction)
            except Exception, e:
                retXMLstr = FaultFromException(e, 0, sys.exc_info()[2]).AsSOAP()
                self.start_response('400 Bad Request', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
                return retXMLstr
            # Verify if Signed
            self.ServiceInstance.verify(ps)
            try:
                result = method(ps)
            except Exception, e:
                retXMLstr = FaultFromException(e, 0, sys.exc_info()[2]).AsSOAP()
                self.start_response('202 Accepted', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
                return retXMLstr
            # If No response just return.
            if result is None:
                self.start_response('202 Accepted', [('Content-Type', 'text/xml; charset="utf-8"')])
                return ''
            sw = SoapWriter(nsdict={})
            try:
                sw.serialize(result)
            except Exception, e:
                retXMLstr = FaultFromException(e, 0, sys.exc_info()[2]).AsSOAP()
                self.start_response('202 Accepted', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
                return retXMLstr
            # Create Signatures
            self.ServiceInstance.sign(sw)            
            # Finally, send SOAP response
            try:
                soapdata = str(sw)
                self.start_response('200 OK', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(soapdata)))])
                return soapdata
            except Exception, e:
                retXMLstr = FaultFromException(e, 0, sys.exc_info()[2]).AsSOAP()
                self.start_response('202 Accepted', [('Content-Type', 'text/xml; charset="utf-8"'),
                                                 ('Content-Length', str(len(retXMLstr)))])
                return retXMLstr
                

#for apache
#############################
#application = app.wsgifunc()

if __name__ == "__main__":
    app.run()


