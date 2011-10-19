"""
export tpwd data to gems format
"""
import csv
from datetime import datetime
import gc
import glob
import os

import sqlalchemy as sa
from pyhis import cache

CACHE_DIR = "cache_files/"
CACHE_DATABASE_FILE = os.path.join(CACHE_DIR, "tpwd_pyhis_cache.db")
CACHE_DATABASE_URI = 'sqlite:///' + CACHE_DATABASE_FILE

TPWD_DATA_DIR = '/home/wilsaj/data/tpwd/'

ECHO_SQLALCHEMY = False

TPWD_SOURCE = 'http://his.crwr.utexas.edu/tpwd/cuahsi_1_0.asmx?WSDL'
TPWD_NETWORK = 'TPWDCoastalFisheries'
TPWD_VOCABULARY = 'TPWDCoastalFisheries'


SITE_LIST = ['aransas',
             'corpuschristi',
             'eastmatagorda',
             'galveston',
             'gulf',
             'lowerlagunamadre',
             'matagorda',
             'sabine',
             'sanantonio',
             'upperlagunamadre']

WDFT_PARAMETERS = {
    'barometric_pressure': ('air_pressure', 'inches hg'),
    'temperature': ('water_temperature', 'degC'),
    'dissolved_oxygen': ('water_dissolved_oxygen_concentration', 'ppm'),
    'salinity': ('salinity', 'ppt'),
    'turbidity': ('turbidity', 'ntu')
    }

UNITS_DICT = {
    # 'key': ('parameter name', standard_units, function_that_converts_to_standard_units)
    'degC': ('degrees celsius', 'degC', None),
    'inches hg': ('inches of mercury', 'inches hg', None),
    'mgl': ('milligrams per liter', 'mgl', None),
    'ntu': ('nephelometric turbidity units', 'ntu', None),
    'ppt': ('parts per thousand', 'ppt', None),
    'ppm': ('parts per million', 'ppt', lambda x: x / 1000.0),
    }

PARAMETERS_DICT = {
    # 'parameter_code': 'parameter_name
    'air_pressure': 'Air Pressure',
    'salinity': 'Salinity',
    'water_dissolved_oxygen_concentration': 'Dissolved Oxygen Concentration',
    'water_temperature': 'Water Temperature',
    'turbidity': 'Turbidity',
}


def commit_data_for_site(site_name):
    """commits data values to the database"""
    timestamp_format = '%d%b%Y:%H:%M:%S.000'
    csv_files = glob.glob('/'.join(
        [TPWD_DATA_DIR, '/request_*/%s*' % site_name]))

    for i, csv_file in enumerate(csv_files):
        print "processing file: %s" % csv_file

        total_lines = 0
        with open(csv_file, 'rb') as f:
            for i, l in enumerate(f):
                pass
            total_lines = i + 1

        line_count = 0
        previous_timestamp = None
        with open(csv_file, 'rb') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if len(cache.db_session.new) > 5000:
                    cache.db_session.commit()

                timestamp = datetime.strptime(row['start_dttm'],
                                              timestamp_format)
                if timestamp != previous_timestamp:
                    cache_row(row, csv_file, timestamp)
                    previous_timestamp = timestamp
        cache.db_session.commit()


def cache_row(row, csv_file_path, timestamp):
    """commit a single row of data to the database"""
    file_source = cache.CacheSource(url=TPWD_SOURCE)
    tpwd_parameter_codes = (
        'barometric_pressure',
        'temperature',
        'dissolved_oxygen',
        'salinity',
        'turbidity')

    site_code = site_code_hash(
        row['major_area_code'],
        row['minor_bay_code'],
        row['station_code'],
        row['start_latitude_num'],
        row['start_longitude_num'])

    site = cache.CacheSite(
        network=TPWD_NETWORK,
        code=site_code,
        latitude=dms_to_decimal_degrees(row['start_latitude_num']),
        longitude=dms_to_decimal_degrees(row['start_longitude_num']),
        source=file_source,
        auto_add=False,
        auto_commit=False,
        skip_db_lookup=False)

    # skip dates from files that are not the 2009 files
    if timestamp.year == 2009 and not '20110524' in csv_file_path:
        return

    for tpwd_parameter_code in tpwd_parameter_codes:
        wdft_parameter_code = WDFT_PARAMETERS[tpwd_parameter_code][0]
        wdft_parameter_name = PARAMETERS_DICT[wdft_parameter_code]

        tpwd_units_code = WDFT_PARAMETERS[tpwd_parameter_code][1]
        wdft_converted_units_code = UNITS_DICT[tpwd_units_code][1]
        wdft_converted_units_name = UNITS_DICT[wdft_converted_units_code][0]
        conversion_func = UNITS_DICT[tpwd_units_code][2]

        if not conversion_func:
            conversion_func = lambda x: x

        units = cache.CacheUnits(
            code=wdft_converted_units_code,
            abbreviation=wdft_converted_units_code,
            name=wdft_converted_units_name)

        variable = cache.CacheVariable(
            units=units,
            name=wdft_parameter_name,
            code=wdft_parameter_code,
            vocabulary=TPWD_VOCABULARY)

        row_index = 'start_%s_num' % tpwd_parameter_code
        if row[row_index]:
            cache.db_session.add(site)
            timeseries = cache.CacheTimeSeries(
                site=site,
                variable=variable,
                auto_add=True,
                auto_commit=False,
                skip_db_lookup=False)
            cache.db_session.add(cache.DBValue(
                timestamp=timestamp,
                value=conversion_func(float(row[row_index])),
                timeseries=timeseries))


def dms_to_decimal_degrees(dms_value):
    """
    returns a string representation of a TPWD latitude or longitude
    representation
    """
    degrees, minutes, seconds = dms_value[:2], dms_value[2:4], dms_value[4:6]
    decimal_degrees = int(degrees) + \
                      ((float(minutes) * 60) + float(seconds)) / 3600.0
    if decimal_degrees > 50:
        decimal_degrees *= -1
    return str(decimal_degrees)


def site_code_hash(major_area_code, minor_bay_code, station_code,
                   latitude, longitude):
    """
    returns hashed site code, this should provide a unique site code
    for each site and lat/long, though there is a small chance for
    collisions
    """
    return '_'.join([latitude.replace('.', ''), longitude.replace('.', '')])


def export_to_cache():
    for site in SITE_LIST:
        cache.init_cache(CACHE_DATABASE_FILE, ECHO_SQLALCHEMY)
        # print "cache._cache size: %s" % reduce(
        #     (lambda x, y: x+y), (len(v) for v in cache._cache.values()))
        cache.clear_memory_cache()
        # print "gc.get_count(): [%s, %s, %s]" % gc.get_count()
        # print "garbage collecting..."
        gc.collect()
        # print "gc.get_count(): [%s, %s, %s]" % gc.get_count()
        # print "cache._cache size: %s" % reduce(
        #     (lambda x, y: x+y), (len(v) for v in cache._cache.values()))
        commit_data_for_site(site)


if __name__ == '__main__':
    export_to_cache()
