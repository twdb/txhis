"""
export pyhis cache database to the gems database
"""
import os

from sqlalchemy import create_engine, func, Table
from sqlalchemy.schema import UniqueConstraint, ForeignKey
from sqlalchemy import (Column, Boolean, Integer, Index, Text, String, Float,
                        DateTime, Enum)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import (declarative_base, declared_attr,
                                        synonym_for)
from sqlalchemy.orm import relationship, backref, sessionmaker, synonym
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import asc, desc
from sqlite3 import dbapi2 as sqlite

from pyhis import cache

CACHE_DIR = "cache_files/"
CACHE_DATABASE_FILES = [
    "tpwd_pyhis_cache.db",
    "tceq_pyhis_cache.db",
    "twdb_pyhis_cache.db",
    ]

GEMS_DATABASE_DIR = "gems_database/"
GEMS_DATABASE_FILE = os.path.join(GEMS_DATABASE_DIR, "gems_database.db")
GEMS_DATABASE_URI = 'sqlite:///' + GEMS_DATABASE_FILE
ECHO_SQLALCHEMY = False

gems_engine = create_engine(GEMS_DATABASE_URI, convert_unicode=True,
                            module=sqlite, echo=ECHO_SQLALCHEMY)
GemsSession = sessionmaker(autocommit=False, autoflush=False,
                           bind=gems_engine)
gems_session = GemsSession()

Base = declarative_base(bind=gems_engine)


# this units dict is handled a little differently than those in the
# *_to_cache.py scripts. Basically, this dict saves us a sql query for
# variable.units per each value.
UNITS_DICT = {
    # 'variable_code': ('unit_code', 'unit_name', 'conversion_func')
    'air_pressure': ('inches hg', 'inches of mercury'),
    'air_temperature': ('degC', 'degrees celsius'),
    'gage_height': ('gage height', 'international feet'),
    'salinity': ('ppt', 'parts per thousand'),
    'turbidity': ('ntu', 'nephelometric turbidity units'),
    'water_dissolved_oxygen_concentration': (
        'mg/l', 'milligrams per liter'),
    'water_dissolved_oxygen_percent_saturation': ('percent', 'percent'),
    'water_ph': ('dimensionless', 'dimensionless'),
    'water_specific_conductance': ('uS/cm', 'microsiemens'),
    'water_temperature': ('degC', 'degrees celsius'),
    }


class GEMSSite(Base):
    __tablename__ = 'tbl_TexasHIS_Vector_TWDB_ODM_Sites'
    __table_args__ = (
        Index('idx_ODM_Network_ODM_Site_Code', 'ODM_Network',
              'ODM_Site_Code', unique=True),
        {}
        )

    ODM_SQL_SiteID = Column(Integer, primary_key=True)
    ODM_Network = Column(String)
    ODM_URL = Column(String)
    ODM_Site_Code = Column(String)
    ODM_Site_Name = Column(String)
    ODM_Source_Desc = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    ODM_Param_FromDate = Column(DateTime)
    ODM_Param_ToDate = Column(DateTime)

    values = relationship('GEMSData', backref='site', lazy='dynamic')

    def __init__(self, ODM_SQL_SiteID=None, ODM_Network=None, ODM_URL=None,
                 ODM_Site_Code=None, ODM_Site_Name=None,
                 ODM_Source_Desc=None, latitude=None, longitude=None,
                 ODM_Param_FromDate=None, ODM_Param_ToDate=None):
        self.ODM_SQL_SiteID = ODM_SQL_SiteID
        self.ODM_Network = ODM_Network
        self.ODM_URL = ODM_URL
        self.ODM_Site_Code = ODM_Site_Code
        self.ODM_Site_Name = ODM_Site_Name
        self.ODM_Source_Desc = ODM_Source_Desc
        self.latitude = latitude
        self.longitude = longitude
        self.ODM_Param_FromDate = ODM_Param_FromDate
        self.ODM_Param_ToDate = ODM_Param_ToDate


class GEMSData(Base):
    __tablename__ = 'tbl_TexasHIS_Vector_TWDB_ODM_Data'

    ODM_SQL_ID = Column(Integer, primary_key=True)
    ODM_SQL_SiteID = Column(
        Integer,
        ForeignKey('tbl_TexasHIS_Vector_TWDB_ODM_Sites.ODM_SQL_SiteID'))
    ODM_TWDB_Param = Column(String)
    ODM_TWDB_Param_Name = Column(String)
    ODM_TWDB_Param_Desc = Column(String)
    ODM_Param_Date = Column(DateTime)
    ODM_Param_Value = Column(Float)
    ODM_Param_Units = Column(String)
    ODM_Param_Unit_Desc = Column(String)
    ODM_Param_Datum = Column(String)
    ODM_Param_Depth = Column(Float)
    ODM_Load_Date = Column(DateTime)

    def __init__(self, ODM_SQL_SiteID=None, ODM_TWDB_Param=None,
                 ODM_TWDB_Param_Name=None, ODM_TWDB_Param_Desc=None,
                 ODM_Param_Date=None, ODM_Param_Value=None,
                 ODM_Param_Units=None, ODM_Param_Unit_Desc=None,
                 ODM_Param_Datum=None, ODM_Param_Depth=None,
                 ODM_Load_Date=None):
        self.ODM_SQL_SiteID = ODM_SQL_SiteID
        self.ODM_TWDB_Param = ODM_TWDB_Param
        self.ODM_TWDB_Param_Name = ODM_TWDB_Param_Name
        self.ODM_TWDB_Param_Desc = ODM_TWDB_Param_Desc
        self.ODM_Param_Date = ODM_Param_Date
        self.ODM_Param_Value = ODM_Param_Value
        self.ODM_Param_Units = ODM_Param_Units
        self.ODM_Param_Unit_Desc = ODM_Param_Unit_Desc
        self.ODM_Param_Datum = ODM_Param_Datum
        self.ODM_Param_Depth = ODM_Param_Depth
        self.ODM_Load_Date = ODM_Load_Date


# run create_all to make sure the database tables are all there
def init():
    Base.metadata.create_all(bind=gems_engine)
init()


def export_cache():
    global_site_index = 1
    for database_file in CACHE_DATABASE_FILES:
        cache.init_cache(os.path.join(CACHE_DIR, database_file),
                         ECHO_SQLALCHEMY)
        # create an index on timeseries values if it doesn't exist
        try:
            i = Index('ix_value_timeseries_id',
                      cache.DBValue.__table__.c.timeseries_id)
            i.create(cache.engine)
        except OperationalError:
            pass
        sources = cache.db_session.query(cache.DBSource).all()
        for source in sources:
            global_site_index = export_source(source, global_site_index)


def export_source(source, global_site_index):
    sites_query = cache.db_session.query(cache.DBSite)
    site_count = sites_query.count()
    source_site_index = 1
    for site in page_query(sites_query):
        if source_site_index == 1 or source_site_index % 1000 == 0:
            print("processing site %s of %s" % (source_site_index, site_count))
        try:
            gems_site = gems_session.query(GEMSSite).filter_by(
                ODM_Site_Code=site.code,
                ODM_Network=site.network).one()
        except NoResultFound:
            gems_site = GEMSSite(
                ODM_SQL_SiteID=global_site_index,
                ODM_Network=site.network,
                ODM_URL=source.url,
                ODM_Site_Code=site.code,
                ODM_Site_Name=site.name,
                # ODM_Source_Desc=source.description,
                ODM_Source_Desc='',
                latitude=site.latitude,
                longitude=site.longitude,
                ODM_Param_FromDate=None,
                ODM_Param_ToDate=None)
            gems_session.add(gems_site)
        for timeseries in site.timeseries_list.all():
            export_timeseries(timeseries, gems_site)
        global_site_index += 1
        source_site_index += 1
    gems_session.commit()
    return global_site_index


def export_timeseries(timeseries, gems_site):
    for value in timeseries.values:
        if len(gems_session.new) > 1500:
            gems_session.commit()

        variable_code = timeseries.variable.code
        units_code, units_name = UNITS_DICT[variable_code]

        data = GEMSData(
            ODM_SQL_SiteID=gems_site.ODM_SQL_SiteID,
            ODM_TWDB_Param=variable_code,
            ODM_TWDB_Param_Name=timeseries.variable.name,
            ODM_TWDB_Param_Desc=None,
            ODM_Param_Date=value.timestamp,
            ODM_Param_Value=value.value,
            ODM_Param_Units=units_code,
            ODM_Param_Unit_Desc=units_name,
            ODM_Param_Datum=None,
            ODM_Param_Depth=None,
            ODM_Load_Date=None)
        gems_session.add(data)


def page_query(q):
    """
    loop over a large sqlalchemy query with an offset (to avoid having
    to load the result of a huge query into memory)
    """
    offset = 0
    r = False
    while True:
        for elem in q.limit(1000).offset(offset):
            r = True
            yield elem
        offset += 1000
        if not r:
            break
        r = False


def set_from_and_to_dates():
    try:
        index_str = 'CREATE INDEX ' +\
                    '"ix_GEMSData__ODM_SQL_SiteID_ODM_Param_asc" ON ' +\
                    '"tbl_TexasHIS_Vector_TWDB_ODM_Data" ("ODM_SQL_SiteID",' +\
                    '"ODM_Param_Date" ASC);'
        gems_engine.execute(index_str)
    except OperationalError:
        pass
    sites_query = gems_session.query(GEMSSite)
    site_count = sites_query.count()
    for index, site in enumerate(page_query(sites_query)):
        if index == 1 or index % 1000 == 0:
            print "setting from and to dates for %s of %s sites" % (
                index, site_count)

        if len(gems_session.dirty) > 1500:
            gems_session.commit()

        from_value = site.values.order_by(asc('ODM_Param_Date')).first()
        to_value = site.values.order_by(desc('ODM_Param_Date')).first()
        if from_value:
            site.ODM_Param_FromDate = from_value.ODM_Param_Date
            site.ODM_Param_ToDate = to_value.ODM_Param_Date
        else:
            # if for some reason there are no values for a site
            gems_session.delete(site)
    gems_session.commit()


if __name__ == '__main__':
    export_cache()
    set_from_and_to_dates()
