from sqlalchemy import (Column, Integer, String, ForeignKey, Float, DateTime)

from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base

import wof.models as wof_base

Base = declarative_base()


def init_model(db_session):
    Base.query = db_session.query_property()

#TODO: Andy, please check
param_to_medium_dict = {
    'water_ph': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_y_velocity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_x_velocity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_temperature': wof_base.SampleMediumTypes.SURFACE_WATER,
    'upward_water_velocity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_turbidity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_total_dissolved_salts': wof_base.SampleMediumTypes.SURFACE_WATER,
    'seawater_salinity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'northward_water_velocity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_electrical_conductivity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'eastward_water_velocity': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_dissolved_oxygen_percent_saturation':
        wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_dissolved_oxygen_concentration':
        wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_depth_vented': wof_base.SampleMediumTypes.SURFACE_WATER,
    'water_depth_non_vented': wof_base.SampleMediumTypes.SURFACE_WATER,
    'instrument_battery_voltage': wof_base.SampleMediumTypes.NOT_RELEVANT,
    'air_pressure': wof_base.SampleMediumTypes.AIR,
    'air_temperature': wof_base.SampleMediumTypes.AIR,
    'water_specific_conductance': wof_base.SampleMediumTypes.SURFACE_WATER
}

#TODO: Andy, please check
param_to_gen_category_dict = {
    'water_ph': wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'water_y_velocity': wof_base.GeneralCategoryTypes.HYDROLOGY,
    'water_x_velocity': wof_base.GeneralCategoryTypes.HYDROLOGY,
    'water_temperature': wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'upward_water_velocity': wof_base.GeneralCategoryTypes.HYDROLOGY,
    'water_turbidity': wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'water_total_dissolved_salts': wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'seawater_salinity': wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'northward_water_velocity': wof_base.GeneralCategoryTypes.HYDROLOGY,
    'water_electrical_conductivity':
        wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'eastward_water_velocity': wof_base.GeneralCategoryTypes.HYDROLOGY,
    'water_dissolved_oxygen_percent_saturation':
        wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'water_dissolved_oxygen_concentration':
        wof_base.GeneralCategoryTypes.WATER_QUALITY,
    'water_depth_vented': wof_base.GeneralCategoryTypes.HYDROLOGY,
    'water_depth_non_vented': wof_base.GeneralCategoryTypes.HYDROLOGY,
    'instrument_battery_voltage':
         wof_base.GeneralCategoryTypes.INSTRUMENTATION,
    'air_pressure': wof_base.GeneralCategoryTypes.CLIMATE,
    'air_temperature': wof_base.GeneralCategoryTypes.CLIMATE,
    'water_specific_conductance': wof_base.GeneralCategoryTypes.WATER_QUALITY
}


class Site(Base, wof_base.BaseSite):
    __tablename__ = 'site'

    # just use id, since SiteID is not guaranteed to exist
    SiteID = Column('id', Integer, primary_key=True)
    #SiteID = Column('site_id', Integer)
    SiteCode = Column('code', String)
    SiteName = Column('name', String)
    Latitude = Column('latitude', Float)
    Longitude = Column('longitude', Float)

    #Elevation_m = Column(Float)
    #VerticalDatum = Column(String)

    #All sites are in WGS84
    LatLongDatum = wof_base.BaseSpatialReference()
    LatLongDatum.SRSID = 4326
    LatLongDatum.SRSName = "WGS84"


class Variable(Base, wof_base.BaseVariable):
    __tablename__ = 'variable'

    VariableID = Column('id', Integer, primary_key=True)
    VariableCode = Column('code', String)
    VariableName = Column('name', String)
    IsRegular = False
    ValueType = "Field Observation"
    DataType = "Sporadic"
    NoDataValue = Column('no_data_value', String)
    # VariableUnitsID = Column(Integer, ForeignKey('units.id'))

    @property
    def SampleMedium(self):
        try:
            return param_to_medium_dict[self.VariableCode]
        except KeyError:
            return wof_base.SampleMediumTypes.UNKNOWN

    @property
    def GeneralCategory(self):
        try:
            return param_to_gen_category_dict[self.VariableCode]
        except KeyError:
            return wof_base.GeneralCategoryTypes.UNKNOWN

    #TODO
    #TimeSupport = Column(Float)
    #TimeUnitsID = Column(Integer, ForeignKey('Units.UnitsID'))


class DataValue(Base, wof_base.BaseDataValue):
    __tablename__ = 'value'

    ValueID = Column('id', Integer, primary_key=True)
    DataValue = Column('value', Float)
    DateTimeUTC = Column('timestamp', DateTime)

    #Data are non-censored TODO: Check if this is always the case
    CensorCode = "nc"

    #Only have one Source for SWIS data
    SourceID = 1

    #All of SWIS data values are "raw data"
    QualityControlLevel = wof_base.QualityControlLevelTypes['RAW_DATA'][0]
    QualityControlLevelID = wof_base.QualityControlLevelTypes['RAW_DATA'][1]

    SeriesID = Column('timeseries_id', Integer, ForeignKey('timeseries.id'))
    Series = relationship('Series',
                          backref=backref('DataValues', lazy='dynamic'))

    @property
    def VariableID(self):
        try:
            return Series.VariableID
        except AttributeError:
            return None

    @property
    def SiteID(self):
        try:
            return Series.SiteID
        except AttributeError:
            return None


    #TODO
    #ValueAccuracy = Column(Float)
    #LocalDateTime = Column('timestamp', DateTime)
    #UTCOffset = None
    #OffsetValue = Column('vertical_offset', Float)
    #OffsetTypeID = Column(Integer)
    #QualifierID = Column(Integer)
    #MethodID = None
    #SampleID = None


class Method(wof_base.BaseMethod):
    pass
    # MethodID = None
    # MethodDescription = None
    # MethodLink = None


#TWDB is the Source/contact for all SWIS data
class Source(wof_base.BaseSource):
    SourceID = 1
    #TODO: Metadata
    Metadata = None


#TODO: Metadata
# Not a clear mapping.  project.name could be title,
# project.description could be abstract
#class Metadata(wof_base.BaseMetadata):
#    __tablename__='ISOMetadata'
#
#    MetadataID = Column(Integer, primary_key=True)
#    TopicCategory = Column(String)
#    Title = Column(String)
#    Abstract = Column(String)
#    ProfileVersion = Column(String)
#    MetadataLink = Column(String)

class Qualifier(wof_base.BaseQualifier):
    pass
    #TODO
    # QualifierID = None
    # QualifierCode = None
    # QualifierDescription = None


class OffsetType(wof_base.BaseOffsetType):
    pass


class Series(Base, wof_base.BaseSeries):
    __tablename__ = 'timeseries'

    SeriesID = Column('id', Integer, primary_key=True)
    # VariableUnitsID = None
    # VariableUnitsName = None
    # SampleMedium = None
    # ValueType = None
    # TimeSupport = None
    # TimeUnitsID = None
    # TimeUnitsName = None
    # DataType = None
    # GeneralCategory = None
    # MethodID = None
    # MethodDescription = None
    # SourceID = None
    # Organization = None
    # SourceDescription = None
    # QualityControlLevelID = None
    # QualityControlLevelCode = None
    # BeginDateTime = None
    # EndDateTime = None
    # BeginDateTimeUTC = None
    # EndDateTimeUTC = None
    # ValueCount = None

    # Variable = BaseVariable()
    # Method = BaseMethod()

    SiteID = Column('site_id', ForeignKey('site.id'))
    Site = relationship('Site', backref=('Series'), lazy='dynamic')
    VariableID = Column('variable_id', ForeignKey('variable.id'))
    Variable = relationship('Variable', backref=('Series'))

    @property
    def SiteCode(self):
        try:
            return self.Site.SiteCode
        except AttributeError:
            return None

    @property
    def SiteName(self):
        try:
            return self.Site.SiteName
        except AttributeError:
            return None

    @property
    def VariableCode(self):
        try:
            return self.Variable.VariableCode
        except AttributeError:
            return None

    @property
    def VariableName(self):
        try:
            return self.Variable.VariableName
        except AttributeError:
            return None

    @property
    def Source(self):
        try:
            return self.Site.Source
        except AttributeError:
            return None

    @property
    def ValueCount(self):
        try:
            return self.value_count
        except AttributeError:
            self.value_count = self.DataValues.count()
            return self.value_count

    # def __init__(self, site=None, variable=None, value_count=None,
    #              begin_date_time_utc=None, end_date_time_utc=None,
    #              source=None):
    #     self.Site = site
    #     self.Variable = variable
    #     self.value_count = value_count
    #     self.BeginDateTimeUTC = begin_date_time_utc
    #     self.EndDateTimeUTC = end_date_time_utc

    #     #SWIS data are all "Raw Data"
    #     # though might have more than one QC level in the future
    #     self.QualityControlLevelID = \
    #                         wof_base.QualityControlLevelTypes['RAW_DATA'][1]
    #     self.QualityControlLevelCode = \
    #                         wof_base.QualityControlLevelTypes['RAW_DATA'][0]

    #     self.Source = source
