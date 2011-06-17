"""
export tceq data to pyhis cache format
"""
import csv
import datetime
import glob
import logging
import os
import sys
import tempfile
import warnings

from sqlalchemy import create_engine, func, Table
from sqlalchemy.schema import UniqueConstraint, ForeignKey
import sqlalchemy as sa
from sqlalchemy.ext.declarative import (declarative_base, declared_attr,
                                        synonym_for)
from sqlalchemy.orm import relationship, backref, sessionmaker, synonym
from sqlalchemy.orm.exc import NoResultFound
from sqlite3 import dbapi2 as sqlite

from pyhis import cache

TCEQ_DATABASE_DIR = "tceq_swqm/"
TCEQ_DATABASE_FILE = os.path.join(TCEQ_DATABASE_DIR, "tceq_swqm.db")
TCEQ_DATABASE_URI = 'sqlite:///' + TCEQ_DATABASE_FILE
TCEQ_DATA_DIR = '/home/wilsaj/data/tceq/'
TCEQ_PARAMETER_FILE = 'sw_parm_format.txt'

ECHO_SQLALCHEMY = False

CACHE_DIR = "cache_files/"
CACHE_DATABASE_FILE = os.path.join(CACHE_DIR, "tceq_pyhis_cache.db")
CACHE_DATABASE_URI = 'sqlite:///' + CACHE_DATABASE_FILE
TCEQ_SOURCE = 'http://his.crwr.utexas.edu/TRACS/cuahsi_1_0.asmx?WSDL'
TCEQ_NETWORK = 'TCEQWaterQuality'
TCEQ_VOCABULARY = 'TCEQWaterQuality'

tceq_engine = create_engine(TCEQ_DATABASE_URI, convert_unicode=True,
                            module=sqlite, echo=ECHO_SQLALCHEMY)
TceqSession = sessionmaker(autocommit=False, autoflush=False,
                           bind=tceq_engine)
tceq_session = TceqSession()

Base = declarative_base(bind=tceq_engine)

# configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
fh = logging.FileHandler(os.path.join(CACHE_DIR, 'tceq_warnings.txt'))
fh.setLevel(logging.WARNING)
formatter = logging.Formatter(LOG_FORMAT)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate = False

WDFT_PARAMETER_LIST = [
    # '00217',  # |SALINITY, 24-HR, MAXIMUM, PPT|PPT|Water|N/A Calculation
    # '00218',  # |SALINITY, 24-HR, AVERAGE, PPT|PPT|Water|N/A Calculation
    # '00219',  # |SALINITY, 24-HR, MINIMUM, PPT|PPT|Water|N/A Calculation
    # '00220',  # |SALINITY, # OF MEASUREMENTS IN 24-HRS|NU|Water|N/A Calculation
    '00480',  # |SALINITY - PARTS PER THOUSAND|PPT|Water|N/A Calculation
    '00020',  # |TEMPERATURE, AIR (DEGREES CENTIGRADE)|DEG C|Air|N/A Calculation
    # '00021',  # |TEMPERATURE, AIR (DEGREES FAHRENHEIT)|DEG F|Air|N/A Calculation
    '00010',  # |TEMPERATURE, WATER (DEGREES CENTIGRADE)|DEG C|Water|N/A Calculation
    # '00011',  # |TEMPERATURE, WATER (DEGREES FAHRENHEIT)|DEG F|Water|N/A Calculation
    # '00209',  # |TEMPERATURE, WATER (DEGREES CENTIGRADE), 24HR AVG|DEG C|Water|N/A Calculation
    # '00210',  # |WATER TEMPERATURE, DEGREES CENTIGRADE, 24HR MAX|DEG C|Water|N/A Calculation
    # '00211',  # |TEMPERATURE, WATER (DEGREES CENTIGRADE) 24HR MIN|DEG C|Water|N/A Calculation
    '00062',  # |ELEVATION, RESERVOIR SURFACE WATER IN FEET|FT|Water|N/A Calculation
    # '00070',  # |TURBIDITY, (JACKSON CANDLE UNITS)|JTU|Water|N/A Calculation
    # '00076',  # |TURBIDITY,HACH TURBIDIMETER (FORMAZIN TURB UNIT)|FTU|Water|N/A Calculation
    '13854',  # |TURBIDITY, FIELD SENSOR, CONTINUOUS (NTU)|NTU|Water|N/A Calculation
    # '13856',  # |TURBIDITY, FIELD SENSOR, CONTINUOUS (FNU)|FNU|Water|7027
    # '20485',  # |TURBIDITY, FIELD SENSOR, NTU, 24-HR AVG|NTU|Water|N/A Calculation
    # '20486',  # |TURBIDITY, FIELD SENSOR, NTU, 24-HR MIN|NTU|Water|N/A Calculation
    # '20487',  # |TURBIDITY, FIELD SENSOR, NTU, 24-HR MAX|NTU|Water|N/A Calculation
    # '20488',  # |TURBIDITY, FIELD SENSOR, # MEASUREMENTS, 24-HRS|NU|Water|N/A Calculation
    '82078',  # |TURBIDITY,FIELD NEPHELOMETRIC TURBIDITY UNITS, N|NTU|Water|N/A Calculation
    # '82079',  # |TURBIDITY,LAB NEPHELOMETRIC TURBIDITY UNITS, NTU|NTU|Water|N/A Calculation
    '00300',  # |OXYGEN, DISSOLVED (MG/L)|MG/L|Water|N/A Calculation
    '00301',  # |OXYGEN, DISSOLVED (PERCENT OF SATURATION)|% SAT|Water|N/A Calculation
    '00302',  # |OXYGEN, DISSOLVED, OPTICAL SENSOR|MG/L|Water|N/A Calculation
    '00303',  # |OXYGEN, DISSOLVED (PERCENT OF SATURATION) BY OPTICAL SENSOR|% SAT|Water|N/A Calculation
    # '20388',  # |DISSOLVED OXYGEN, 24-HOUR,%SATURATION,MINIMUM|%|Water|N/A Calculation
    # '20389',  # |DISSOLVED OXYGEN, 24-HOUR, % SATURATION, MAXIMUM|%|Water|N/A Calculation
    # '20390',  # |DISSOLVED OXYGEN, 24-HOUR, % SATURATION, AVERAGE|%|Water|N/A Calculation
    # '20391',  # |DISSOLVED OXYGEN,%SATURATION,# MEAS IN 24HR|NU|Water|N/A Calculation
    # '89855',  # |DISSOLVED OXYGEN, 24-HOUR MIN. (MG/L) MIN. 4 MEA|MG/L|Water|N/A Calculation
    # '89856',  # |DISSOLVED OXYGEN, 24-HOUR MAX. (MG/L) MIN. 4 MEA|MG/L|Water|N/A Calculation
    # '89857',  # |DISSOLVED OXYGEN, 24-HOUR AVG. (MG/L) MIN. 4 MEA|MG/L|Water|N/A Calculation
    # '89858',  # |DISSOLVED OXYGEN, # OF MEASUREMENTS IN 24-HRS|NU|Water|N/A Calculation
    '00064',  # |DEPTH OF STREAM, MEAN (FT)|FT|Water|N/A Calculation
    '72025',  # |DEPTH OF POND OR RESERVOIR IN FEET|FT|Water|N/A Calculation
    '00094',  # |SPECIFIC CONDUCTANCE,FIELD (US/CM @ 25C)|uS/cm|Water|N/A Calculation
    # '00095',  # |SPECIFIC CONDUCTANCE,LAB (UMHOS/CM @ 25C)|uS/cm|Water|N/A Calculation
    # '00212',  # |SPECIFIC CONDUCTANCE, US/CM, FIELD, 24HR AVG|uS/cm|Water|N/A Calculation
    # '00213',  # |SPECIFIC CONDUCTANCE, US/CM, FIELD, 24HR MAX|uS/cm|Water|N/A Calculation
    # '00214',  # |SPECIFIC CONDUCTANCE, US/CM, FIELD, 24HR MIN|uS/cm|Water|N/A Calculation
    # '00222',  # |SPECIFIC CONDUCTANCE, # OF MEASUREMENTS IN 24-HR|NU|Water|N/A Calculation
    # '47004',  # |SOLIDS,TOTAL, DISS, ELECTRICAL-CONDUCTIVITY,MG/L|MG/L|Water|N/A Calculation
    ]

WDFT_PARAMETERS = {
    # 'tceq_parameter_code': ('wdft_parameter_code', 'unit_code')
    # |SALINITY - PARTS PER THOUSAND|PPT|Water|N/A Calculation
    '00480': ('salinity', 'ppt'),
    # |TEMPERATURE, AIR (DEGREES CENTIGRADE)|DEG C|Air|N/A Calculation
    '00020': ('air_temperature', 'degC'),
    # '00021',  # |TEMPERATURE, AIR (DEGREES FAHRENHEIT)|DEG F|Air|N/A Calculation
    '00021': ('air_temperature', 'degF'),
    # |TEMPERATURE, WATER (DEGREES CENTIGRADE)|DEG C|Water|N/A Calculation
    '00010': ('water_temperature', 'degC'),
    # |TEMPERATURE, WATER (DEGREES FAHRENHEIT)|DEG F|Water|N/A Calculation
    '00011': ('water_temperature', 'degF'),
    # |TURBIDITY, FIELD SENSOR, CONTINUOUS (NTU)|NTU|Water|N/A Calculation
    '13854': ('turbidity', 'ntu'),
    # |TURBIDITY,FIELD NEPHELOMETRIC TURBIDITY UNITS, N|NTU|Water|N/A Calculation
    '82078': ('turbidity', 'ntu'),
    # |TURBIDITY,LAB NEPHELOMETRIC TURBIDITY UNITS, NTU|NTU|Water|N/A Calculation
    '82079': ('turbidity', 'ntu'),
    # |OXYGEN, DISSOLVED (MG/L)|MG/L|Water|N/A Calculation
    '00300': ('water_dissolved_oxygen_concentration', 'mgl'),
    # |OXYGEN, DISSOLVED, OPTICAL SENSOR|MG/L|Water|N/A Calculation
    '00302': ('water_dissolved_oxygen_concentration', 'mgl'),
    # |OXYGEN, DISSOLVED (PERCENT OF SATURATION)|% SAT|Water|N/A Calculation
    '00301': ('water_dissolved_oxygen_percent_saturation', 'percent'),
    # |OXYGEN, DISSOLVED (PERCENT OF SATURATION) BY OPTICAL SENSOR|% SAT|Water|N/A Calculation
    '00303': ('water_dissolved_oxygen_percent_saturation', 'percent'),
    # |SPECIFIC CONDUCTANCE,FIELD (US/CM @ 25C)|uS/cm|Water|N/A Calculation
    '00094': ('water_specific_conductance', 'uScm'),
    # |SPECIFIC CONDUCTANCE,LAB (UMHOS/CM @ 25C)|uS/cm|Water|N/A
    '00095': ('water_specific_conductance', 'uScm'),
    # XXX: todo
           # '00070',  # |TURBIDITY, (JACKSON CANDLE UNITS)|JTU|Water|N/A Calculation
           # '00076',  # |TURBIDITY,HACH TURBIDIMETER (FORMAZIN TURB UNIT)|FTU|Water|N/A Calculation

           # '13856',  # |TURBIDITY, FIELD SENSOR, CONTINUOUS (FNU)|FNU|Water|7027
           # '47004',  # |SOLIDS,TOTAL, DISS, ELECTRICAL-CONDUCTIVITY,MG/L|MG/L|Water|N/A Calculation
           # '00064',  # |DEPTH OF STREAM, MEAN (FT)|FT|Water|N/A Calculation
           # '72025',  # |DEPTH OF POND OR RESERVOIR IN FEET|FT|Water|N/A Calculation
           # '00062' |ELEVATION, RESERVOIR SURFACE WATER IN FEET|FT|Water|N/A Calculation
    }

UNITS_DICT = {
    # 'key': ('parameter name', standard_units, function_that_converts_to_standard_units)
    'ppt': ('parts per thousand', 'ppt', None),
    'degC': ('degrees celsius', 'degC', None),
    'degF': ('degrees fahrenheit', 'degC', lambda x: x * (5.0/9) + 32),
    'ft': ('feet', 'ft', None),
    'ntu': ('nephelometric turbidity units', 'ntu', None),
    'mgl': ('milligrams per liter', 'mgl', None),
    'percent': ('percent', 'percent', None),
    'uScm': ('microsiemens per centimeter', 'uScm', None),
    }

PARAMETERS_DICT = {
    # 'parameter_code': 'parameter_name
    'air_temperature': 'Air Temperature',
    'salinity': 'Salinity',
    'water_dissolved_oxygen_concentration': 'Dissolved Oxygen Concentration',
    'water_dissolved_oxygen_percent_saturation': 'Dissolved Oxygen Saturation Concentration',
    'water_specific_conductance': 'Specific Conductance(Normalized @25degC)',
    'water_temperature': 'Water Temperature',
    'turbidity': 'Turbidity',
}


# ftp://ftp.tceq.state.tx.us/pub/WaterResourceManagement/WaterQuality/DataCollection/CleanRivers/public/stnsmeta.txt
class Station(Base):
    __tablename__ = 'station'

    id = sa.Column(sa.Integer, primary_key=True)
    basin_id = sa.Column(sa.Integer)
    tceq_station_id = sa.Column(sa.String, unique=True)
    usgs_gauge_id = sa.Column(sa.String)
    short_description = sa.Column(sa.String)
    long_description = sa.Column(sa.Text)
    stream_station_location_type = sa.Column(sa.String)
    stream_station_condition_type = sa.Column(sa.String)
    county = sa.Column(sa.String)
    tceq_county_id = sa.Column(sa.Integer)
    stream_segment = sa.Column(sa.String)
    tceq_region = sa.Column(sa.Integer)
    latitude = sa.Column(sa.Float)
    longitude = sa.Column(sa.Float)
    nhd_reach = sa.Column(sa.Integer)
    on_segment = sa.Column(sa.String)
    events = relationship('Event', lazy='dynamic')


# # http://www.tceq.texas.gov/assets/public/compliance/monops/crp/data/ParameterCodeFieldDescriptions.pdf
class Parameter(Base):
    __tablename__ = 'parameter'

    id = sa.Column(sa.Integer, primary_key=True)
    parameter_code = sa.Column(sa.String)
    description = sa.Column(sa.String)
    units = sa.Column(sa.String)
    media = sa.Column(sa.String)
    method = sa.Column(sa.String)

    results = relationship('Result', lazy='dynamic')


# http://www.tceq.state.tx.us/assets/public/compliance/monops/crp/data/event_struct.pdf
class Event(Base):
    __tablename__ = 'event'

    id = sa.Column(sa.Integer, primary_key=True)
    tag_id = sa.Column(sa.String, unique=True)
    # fk to site
    station_id = sa.Column(sa.String, sa.ForeignKey('station.tceq_station_id'))
    end_date = sa.Column(sa.Date)
    end_time = sa.Column(sa.Time)
    end_depth = sa.Column(sa.Float)
    start_date = sa.Column(sa.Date)
    start_time = sa.Column(sa.Time)
    start_depth = sa.Column(sa.Float)
    # T=time, S=space, B=both, and F=flow weightpth
    category = sa.Column(sa.String)
    #called type ##/CN/GB
    number_of_samples = sa.Column(sa.String)
    comment = sa.Column(sa.Text)
    # fk to Chapter 4 of the Data Management Reference Guide
    submitting_entity = sa.Column(sa.String)
    # fk to Chapter 4 of the Data Management Reference Guide
    collecting_entity = sa.Column(sa.String)
    # fk TCEQ assigns valid codes, and they are listed in Chapter 4 of
    # the Data Management Reference Guide (e.g., RT=Routine ambient
    # sampling, BF=Sampling biased to high or low flow).ty
    monitoring_type = sa.Column(sa.String)

    results = relationship('Result', lazy='dynamic')


class Result(Base):
    __tablename__ = 'result'

    id = sa.Column(sa.Integer, primary_key=True)
    # fk to Event
    tag_id = sa.Column(sa.String, sa.ForeignKey('event.tag_id'))
    # must match event end_data
    end_date = sa.Column(sa.Date)
    parameter_code = sa.Column(sa.String,
                               sa.ForeignKey('parameter.parameter_code'))
    # value > or < quantification limits or blankmeter_code
    gtlt = sa.Column(sa.String)
    value = sa.Column(sa.Float)
    # limit of Detectionue
    limit_of_detection = sa.Column(sa.Float)
    # Limit of Quantification
    limit_of_quantification = sa.Column(sa.Float)
    # from chapter 9 of reference
    qualifier_code = sa.Column(sa.String)
    # if value outside max/min limits & TCEQ verifies as correct then = 1ode
    verify_flag = sa.Column(sa.Integer)

    event = relationship('Event')
    parameter = relationship('Parameter')

    # backrefs:
    #   parameter: Parameter  (many to one)


def create_tceq_stations(stations_file):
    """
    read a stations file and save all the stations in that file to the
    database
    """
    temp_file = clean_file(stations_file)
    with open(temp_file, 'rb') as f:
        reader = csv.DictReader(f, delimiter='|')
        for row in reader:
            station = Station(
                basin_id=row['basinid'],
                tceq_station_id=row['stationid'],
                usgs_gauge_id=row['gaugeid'],
                short_description=row['shortdesc'],
                long_description=row['longdesc'],
                stream_station_location_type=row['streamtype'],
                stream_station_condition_type=row['streamtype2'],
                county=row['county'],
                tceq_county_id=row['tceqcountyid'],
                stream_segment=row['segment'],
                tceq_region=row['tceqregion'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                nhd_reach=row['nhdreachid'],
                on_segment=row['onsegflag'])
            tceq_session.add(station)
    tceq_session.commit()
    os.remove(temp_file)


def create_tceq_parameters(parameter_file):
    """
    read a parameter file and save all the parameters in that file to
    the database
    """
    with open(parameter_file, 'rb') as f:
        reader = csv.DictReader(f, delimiter='|')
        for row in reader:
            parameter = Parameter(
                parameter_code=row['Parameter Code'],
                description=row['Parameter Description'],
                units=row['Units of Measurement'],
                media=row['Media'],
                method=row['Method'])
            tceq_session.add(parameter)
        tceq_session.commit()


def create_tceq_events(event_file):
    """
    read an event file and save all the events in that file to
    the database
    """
    temp_file = clean_file(event_file)
    with open(temp_file, 'rU') as f:
        # these aren't the data you're looking for
        if 'You requested' in f.readline():
            return
        f.seek(0)

        keys = ['tag_id', 'station_id', 'end_date', 'end_time', 'end_depth',
                'start_date', 'start_time', 'start_depth', 'category',
                'number_of_samples', 'comment', 'submitting_entity',
                'collecting_entity', 'monitoring_type']
        reader = csv.DictReader(f, delimiter='|', fieldnames=keys, quoting=csv.QUOTE_NONE)
        for row in reader:
            # skip non-unique tag id (see note at bottom of file)
            if row['tag_id'] == '3198440':
                continue

            event = Event(
                tag_id=row['tag_id'],
                station_id=row['station_id'],
                end_date=convert_date(row['end_date']),
                end_time=convert_time(row['end_time']),
                end_depth=row['end_depth'] if row['end_depth'] != '' else None,
                start_date=convert_date(row['start_date']),
                start_time=convert_time(row['start_time']),
                start_depth=row['start_depth'] if row['start_depth'] != '' else None,
                category=row['category'],
                number_of_samples=row['number_of_samples'],
                comment=row['comment'],
                submitting_entity=row['submitting_entity'],
                collecting_entity=row['collecting_entity'],
                monitoring_type=row['monitoring_type'])
            tceq_session.add(event)
        tceq_session.commit()
    os.remove(temp_file)


def create_tceq_results(results_file):
    """
    read a results file and save all the results in that file to
    the database
    """
    temp_file = clean_file(results_file)
    with open(temp_file, 'rb') as f:
        # these aren't the data you're looking for
        if 'You requested' in f.readline():
            return
        f.seek(0)

        keys = ['tag_id', 'end_date', 'parameter_code', 'gtlt', 'value',
                'limit_of_detection', 'limit_of_quantification',
                'qualifier_code', 'verify_flag']
        reader = csv.DictReader(f, delimiter='|', fieldnames=keys)
        for row in reader:
            result = Result(
                tag_id=row['tag_id'],
                end_date=convert_date(row['end_date']),
                parameter_code=row['parameter_code'],
                gtlt=row['gtlt'],
                value=row['value'],
                limit_of_detection=row['limit_of_detection'] if row['limit_of_detection'] != '' else None,
                limit_of_quantification=row['limit_of_quantification'] if row['limit_of_quantification'] != '' else None,
                qualifier_code=row['qualifier_code'],
                verify_flag=row['verify_flag'])
            tceq_session.add(result)
        tceq_session.commit()
    os.remove(temp_file)


def convert_date(datestr):
    """returns a date from a string formatted as MM/DD/YYYY"""
    date_split = datestr.split('/')
    if len(date_split) == 3:
        return datetime.date(int(date_split[2]), int(date_split[0]),
                             int(date_split[1]))
    else:
        return None


def convert_time(timestr):
    """returns a time from a string formatted as HH:SS"""
    time_split = timestr.split(':')
    if len(time_split) == 2:
        return datetime.time(int(time_split[0]), int(time_split[1]))
    else:
        return None


def clean_file(dirty_file_path):
    """returns a file path string for a temp file that is a cleaned up
    version of this file"""
    fh, temp_path = tempfile.mkstemp()
    temp_fid = open(temp_path, 'w')
    dirty_fid = open(dirty_file_path, 'rb')
    for line in dirty_fid:
        # 11_2005_1.psv has a few lines with extra pipes at the
        # beginning of them
        if line.startswith('|||'):
            temp_fid.write(line[3:])
        else:
            # 4_2001_1.psv contains null characters
            replace_line = line.replace('\x00', '% c')
            # 22_2009_1.psv contains \xbf for apostrophes
            replace_line = replace_line.replace('\xbf', "'")
            # stations file contains some weird ctrl sequence for apostrophes
            replace_line = replace_line.replace('\xc2\x92', "'")
            temp_fid.write(replace_line)
    temp_fid.close()
    dirty_fid.close()
    os.close(fh)
    return temp_path


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


def create_tceq_database():
    Base.metadata.create_all()

    stations_file = os.path.join(TCEQ_DATA_DIR, 'stations.txt')
    create_tceq_stations(stations_file)

    param_file = os.path.join(TCEQ_DATA_DIR, TCEQ_PARAMETER_FILE)
    create_tceq_parameters(param_file)

    event_files = glob.glob('/'.join([TCEQ_DATA_DIR, '*_1.psv']))
    found = False
    for event_file in event_files:
        print "creating events for: %s" % event_file
        create_tceq_events(event_file)

    results_files = glob.glob('/'.join([TCEQ_DATA_DIR, '*_2.psv']))
    for results_file in results_files:
        print "creating results for: %s" % results_file
        create_tceq_results(results_file)


def convert_to_pyhis():
    """convert the tceq database to a pyhis database"""
    # if os.path.exists(CACHE_DATABASE_FILE):
    #     print ("Hold up.. %s already exists. You need to delete or "
    #            "rename it before continuing." % CACHE_DATABASE_FILE)
    #     sys.exit(1)
    # create_pyhis_sites(stations, file_source)

    found = False
    for tceq_parameter_code in WDFT_PARAMETERS:

        cache.init_cache(CACHE_DATABASE_FILE, ECHO_SQLALCHEMY)
        file_source = cache.CacheSource(url=TCEQ_SOURCE)
        parameter = tceq_session.query(Parameter).filter_by(
            parameter_code=tceq_parameter_code).one()
        results_query = parameter.results.filter_by(gtlt='')
        results_count = results_query.count()

        wdft_parameter_code = WDFT_PARAMETERS[tceq_parameter_code][0]
        wdft_parameter_name = PARAMETERS_DICT[wdft_parameter_code]

        tceq_units_code = WDFT_PARAMETERS[tceq_parameter_code][1]
        wdft_converted_units_code = UNITS_DICT[tceq_units_code][1]
        wdft_converted_units_name = UNITS_DICT[wdft_converted_units_code][0]
        conversion_func = UNITS_DICT[tceq_units_code][2]
        if not conversion_func:
            conversion_func = lambda x: x

        print("converting %s values for param: %s (%s)" % (
            results_count, tceq_parameter_code, wdft_parameter_name))

        units = cache.CacheUnits(
            code=wdft_converted_units_code,
            abbreviation=wdft_converted_units_code,
            name=wdft_converted_units_name)

        variable = cache.CacheVariable(
            name=wdft_parameter_name,
            code=wdft_parameter_code,
            vocabulary=TCEQ_VOCABULARY)

        param_total = 0
        param_count = results_count
        for result in page_query(results_query):
            if len(cache.db_session.new) > 5000:
                param_total += len(cache.db_session.new)
                cache.db_session.commit()
                print("committing %s of %s" % (param_total, param_count))

            if result.gtlt != '':
                logger.warning ("result being thrown out, gtlt value. "
                               "result id: %s" % result.id)
                continue

            if not result.event:
                logger.warning("no event found for orphaned result: %s, %s" %
                              (result.id, result.tag_id))
                continue

            event = result.event
            try:
                station = tceq_session.query(Station).filter_by(tceq_station_id=event.station_id).one()
            except NoResultFound:
                logger.warning("station not found for event %s, station_id %s: " %
                              (event.id, event.station_id))
                continue

            if getattr(event, 'start_date', None) and \
                   getattr(event, 'start_time', None):
                timestamp = datetime.datetime.combine(event.start_date,
                                                      event.start_time)
            elif getattr(event, 'end_date', None) and \
                     getattr(event, 'end_time', None):
                timestamp = datetime.datetime.combine(event.end_date,
                                                      event.end_time)
            else:
                logger.warning("event being thrown out, could not determine "
                              "timestamp. event tag_id: %s" % event.tag_id)
                continue

            site = cache.CacheSite(
                site_id=station.tceq_station_id,
                code=station.tceq_station_id,
                name=station.short_description,
                network=TCEQ_NETWORK,
                source=file_source,
                latitude=station.latitude,
                longitude=station.longitude,
                auto_commit=False,
                auto_add=True)

            timeseries = cache.CacheTimeSeries(
                site=site,
                variable=variable,
                auto_commit=False,
                auto_add=True)

            value = cache.DBValue(
                timestamp=timestamp,
                value=conversion_func(result.value))
            timeseries.values.append(value)

        tceq_session.commit()


if __name__ == '__main__':
    # param_file = os.path.join(TCEQ_DATA_DIR, TCEQ_PARAMETER_FILE)
    # create_tceq_parameters(param_file)
    convert_to_pyhis()


# notes:
# events file tag id 3198440 does not appear to be unique
# file: 24_2010_1.psv line 112:
#     3198440|13302|06/09/2010|9:05|2.8|06/09/2010|9:00|2.8|Analytical Result|03||WC|FO|RT
# file: 22_1999_1.psv line 124:
#     3198440|13782|06/15/1999|10:42|4.5|||||||WC|FO|RT
