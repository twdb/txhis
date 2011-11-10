from soaplib.core.service import soap, DefinitionBase
from soaplib.core.model.primitive import String
from soaplib.core.model.clazz import Array, ClassModel
from sqlalchemy.orm import exc as sa_exceptions

import models


class ServiceDetail(ClassModel):
    RemoteSourceURL = String
    SourceFormat = String
    RemoteSourceNetWorkName = String
    UpdateFrequencyType = String
    UpdateFrequencyValue = String
    SourceSummarizedDescription = String
    SourceDescriptionLink = String
    SourceLogoLink = String
    RemoteSourceParameterCodes = Array(String)


class ParameterInfo(ClassModel):
    ParameterCode = String
    ParameterName = String


class SourceWithRemoteParamCode(ClassModel):
    WSDLLink = String
    SourceName = String
    RemoteParamCode = String


def create_registry_service(db_session):
    class CentralRegistryService(DefinitionBase):
        @soap(_returns=Array(ServiceDetail))
        def GetSourcesGEMSS(self):

            """Docstrings for service methods appear as documentation
            in the wsdl <b>what fun</b>

            @param name the name to say hello to
            @param the number of times to say hello
            @return the completed array
            """
            sources = db_session.query(models.Sources).all()
            results = [service_detail_from_source(source)
                       for source in sources]
            return results

        @soap(_returns=Array(ParameterInfo))
        def GetTXHISParameters(self):
            """
            Docstrings for service methods appear as documentation in the wsdl
            <b>what fun</b>
            @param name the name to say hello to
            @param the number of times to say hello
            @return the completed array
            """
            variables = db_session.query(models.Variables).all()
            results = [parameter_info_from_variable(variable)
                       for variable in variables]
            return results

        @soap(String, _returns=Array(SourceWithRemoteParamCode))
        def GetHISParamAvailableSources(self, TXHISParameterCode):
            """
            Docstrings for service methods appear as documentation in the wsdl
            <b>what fun</b>
            @param name the name to say hello to
            @param the number of times to say hello
            @return the completed array
            """
            variable = db_session.query(models.Variables).\
                       filter_by(VariableCode=TXHISParameterCode).one()
            results = []

            for mapping in variable.variable_mapping:
                source = mapping.SourceInfo
                source_with_param = SourceWithRemoteParamCode()
                source_with_param.WSDLLink = source.WSDLLink
                source_with_param.SourceName = source.NetworkName
                source_with_param.RemoteParamCode = mapping.RemoteVariableCode
                results.append(source_with_param)

            return results

        @soap(String, String, String, _returns=String)
        def GetRemoteParameterCode(self, SourceNetworkName,
                                   TXHISParameterCode, WSDLLink):
            """
            Docstrings for service methods appear as documentation in the wsdl
            <b>what fun</b>
            @param name the name to say hello to
            @param the number of times to say hello
            @return the completed array
            """
            try:
                source = db_session.query(models.Sources).\
                             filter_by(NetworkName=SourceNetworkName,
                                       WSDLLink=WSDLLink).one()
            except sa_exceptions.NoResultFound:
                raise Exception(
                    "Could not match (network, parameter, wsdllink): (%s, %s, %s)"
                    % (SourceNetworkName, TXHISParameterCode, WSDLLink))

            for mapping in source.availableParameterInfo:
                if mapping.variable.VariableCode == TXHISParameterCode:
                    return mapping.RemoteVariableCode

    return CentralRegistryService


def service_detail_from_source(source):
    service_detail = ServiceDetail()
    service_detail.RemoteSourceURL = source.SourceLink
    service_detail.SourceFormat = source.SourceFormat
    service_detail.RemoteSourceNetWorkName = source.NetworkName
    service_detail.UpdateFrequencyType = source.UpdateFrequencyType
    service_detail.UpdateFrequencyValue = source.UpdateFrequencyValue
    service_detail.SourceSummarizedDescription = source.SourceSummerizedDescription
    service_detail.SourceDescriptionLink = source.DescriptionLink
    service_detail.SourceLogoLink = source.SourceLink
    service_detail.RemoteSourceParameterCodes = \
                                        [param.RemoteVariableCode\
                                         for param
                                         in source.availableParameterInfo]
    return service_detail


def parameter_info_from_variable(variable):
    parameter_info = ParameterInfo()
    parameter_info.ParameterCode = variable.VariableCode
    parameter_info.ParameterName = variable.VariableName
    return parameter_info


def _class_instance_from_db(soaplib_class, sqlalchemy_obj, variable_map):
    soaplib_instance = soaplib_class()
    for key, val in variable_map.items():
        setattr(soaplib_instance, key, getattr(sqlalchemy_obj, val))
    return soaplib_instance
