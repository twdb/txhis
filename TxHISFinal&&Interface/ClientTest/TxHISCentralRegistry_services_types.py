################################################## 
# TxHISCentralRegistry_services_types.py 
# generated by ZSI.generate.wsdl2python
##################################################


import ZSI
import ZSI.TCcompound
from ZSI.schema import LocalElementDeclaration, ElementDeclaration, TypeDefinition, GTD, GED
from ZSI.generate.pyclass import pyclass_type

##############################
# targetNamespace
# http://greylin/TxHISCentralRegistry/
##############################

class ns0:
    targetNamespace = "http://greylin/TxHISCentralRegistry/"

    class ServiceDetail_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://greylin/TxHISCentralRegistry/"
        type = (schema, "ServiceDetail")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ServiceDetail_Def.schema
            TClist = [ZSI.TC.String(pname="RemoteSourceURL", aname="_RemoteSourceURL", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="SourceFormat", aname="_SourceFormat", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="RemoteSourceNetWorkName", aname="_RemoteSourceNetWorkName", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), self.__class__.UpdateFrequencyType_Dec(minOccurs=1, maxOccurs=1, nillable=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="UpdateFrequencyValue", aname="_UpdateFrequencyValue", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="SourceSummarizedDescription", aname="_SourceSummarizedDescription", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="SourceDescriptionLink", aname="_SourceDescriptionLink", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="SourceLogoLink", aname="_SourceLogoLink", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://greylin/TxHISCentralRegistry/","SourceParameterCodesType",lazy=False)(pname="RemoteSourceParameterCodes", aname="_RemoteSourceParameterCodes", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._RemoteSourceURL = None
                    self._SourceFormat = None
                    self._RemoteSourceNetWorkName = None
                    self._UpdateFrequencyType = None
                    self._UpdateFrequencyValue = None
                    self._SourceSummarizedDescription = None
                    self._SourceDescriptionLink = None
                    self._SourceLogoLink = None
                    self._RemoteSourceParameterCodes = None
                    return
            Holder.__name__ = "ServiceDetail_Holder"
            self.pyclass = Holder


        class UpdateFrequencyType_Dec(ZSI.TC.String, LocalElementDeclaration):
            literal = "UpdateFrequencyType"
            schema = "http://greylin/TxHISCentralRegistry/"
            def __init__(self, **kw):
                kw["pname"] = ("http://greylin/TxHISCentralRegistry/","UpdateFrequencyType")
                kw["aname"] = "_UpdateFrequencyType"
                ZSI.TC.String.__init__(self, **kw)




    class SourceParameterCodesType_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://greylin/TxHISCentralRegistry/"
        type = (schema, "SourceParameterCodesType")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.SourceParameterCodesType_Def.schema
            TClist = [ZSI.TC.String(pname="SourceParameterCode", aname="_SourceParameterCode", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._SourceParameterCode = []
                    return
            Holder.__name__ = "SourceParameterCodesType_Holder"
            self.pyclass = Holder

    class ValuesArray_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://greylin/TxHISCentralRegistry/"
        type = (schema, "ValuesArray")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ValuesArray_Def.schema
            TClist = [ZSI.TCnumbers.FPfloat(pname="value", aname="_value", minOccurs=1, maxOccurs=1000, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._value = []
                    return
            Holder.__name__ = "ValuesArray_Holder"
            self.pyclass = Holder

    class TXHISResponseObjType_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://greylin/TxHISCentralRegistry/"
        type = (schema, "TXHISResponseObjType")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.TXHISResponseObjType_Def.schema
            TClist = [ZSI.TC.String(pname="TXHISParameterName", aname="_TXHISParameterName", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="TXHISParameterCode", aname="_TXHISParameterCode", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="TXHISParameterDescription", aname="_TXHISParameterDescription", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="TXHISParameterUnit", aname="_TXHISParameterUnit", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="TXHISParameterUnitDescription", aname="_TXHISParameterUnitDescription", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://greylin/TxHISCentralRegistry/","ValuesArray",lazy=False)(pname="TXHISParameterValues", aname="_TXHISParameterValues", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._TXHISParameterName = None
                    self._TXHISParameterCode = None
                    self._TXHISParameterDescription = None
                    self._TXHISParameterUnit = None
                    self._TXHISParameterUnitDescription = None
                    self._TXHISParameterValues = None
                    return
            Holder.__name__ = "TXHISResponseObjType_Holder"
            self.pyclass = Holder

    class GetSourcesGEMSS_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "GetSourcesGEMSS"
        schema = "http://greylin/TxHISCentralRegistry/"
        def __init__(self, **kw):
            ns = ns0.GetSourcesGEMSS_Dec.schema
            TClist = []
            kw["pname"] = ("http://greylin/TxHISCentralRegistry/","GetSourcesGEMSS")
            kw["aname"] = "_GetSourcesGEMSS"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    return
            Holder.__name__ = "GetSourcesGEMSS_Holder"
            self.pyclass = Holder

    class GetSourcesGEMSSResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "GetSourcesGEMSSResponse"
        schema = "http://greylin/TxHISCentralRegistry/"
        def __init__(self, **kw):
            ns = ns0.GetSourcesGEMSSResponse_Dec.schema
            TClist = [GTD("http://greylin/TxHISCentralRegistry/","ServiceDetail",lazy=False)(pname="ServiceDetail", aname="_ServiceDetail", minOccurs=0, maxOccurs="unbounded", nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://greylin/TxHISCentralRegistry/","GetSourcesGEMSSResponse")
            kw["aname"] = "_GetSourcesGEMSSResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._ServiceDetail = []
                    return
            Holder.__name__ = "GetSourcesGEMSSResponse_Holder"
            self.pyclass = Holder

    class GetTXHISConvertedOutputGEMSS_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "GetTXHISConvertedOutputGEMSS"
        schema = "http://greylin/TxHISCentralRegistry/"
        def __init__(self, **kw):
            ns = ns0.GetTXHISConvertedOutputGEMSS_Dec.schema
            TClist = [ZSI.TC.String(pname="RemoteSourceURL", aname="_RemoteSourceURL", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="RemoteSourceNetworkName", aname="_RemoteSourceNetworkName", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname="RemoteSourceParameterCode", aname="_RemoteSourceParameterCode", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://greylin/TxHISCentralRegistry/","ValuesArray",lazy=False)(pname="RemoteValues", aname="_RemoteValues", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://greylin/TxHISCentralRegistry/","GetTXHISConvertedOutputGEMSS")
            kw["aname"] = "_GetTXHISConvertedOutputGEMSS"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._RemoteSourceURL = None
                    self._RemoteSourceNetworkName = None
                    self._RemoteSourceParameterCode = None
                    self._RemoteValues = None
                    return
            Holder.__name__ = "GetTXHISConvertedOutputGEMSS_Holder"
            self.pyclass = Holder

    class GetTXHISConvertedOutputGEMSSResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "GetTXHISConvertedOutputGEMSSResponse"
        schema = "http://greylin/TxHISCentralRegistry/"
        def __init__(self, **kw):
            ns = ns0.GetTXHISConvertedOutputGEMSSResponse_Dec.schema
            TClist = [GTD("http://greylin/TxHISCentralRegistry/","TXHISResponseObjType",lazy=False)(pname="TXHISResponseObj", aname="_TXHISResponseObj", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://greylin/TxHISCentralRegistry/","GetTXHISConvertedOutputGEMSSResponse")
            kw["aname"] = "_GetTXHISConvertedOutputGEMSSResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._TXHISResponseObj = None
                    return
            Holder.__name__ = "GetTXHISConvertedOutputGEMSSResponse_Holder"
            self.pyclass = Holder

    class GetConvertedOutputFault_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "GetConvertedOutputFault"
        schema = "http://greylin/TxHISCentralRegistry/"
        def __init__(self, **kw):
            ns = ns0.GetConvertedOutputFault_Dec.schema
            TClist = [ZSI.TC.String(pname="GetConvertedOutputFault", aname="_GetConvertedOutputFault", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://greylin/TxHISCentralRegistry/","GetConvertedOutputFault")
            kw["aname"] = "_GetConvertedOutputFault"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._GetConvertedOutputFault = None
                    return
            Holder.__name__ = "GetConvertedOutputFault_Holder"
            self.pyclass = Holder

# end class ns0 (tns: http://greylin/TxHISCentralRegistry/)
