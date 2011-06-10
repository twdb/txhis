"""
export tpwd data to gems format
"""
import csv
from datetime import datetime
import gc
import glob

import sqlalchemy as sa
from pyhis import cache

CACHE_DATABASE_FILE = "pyhis_tpwd_cache.db"
CACHE_DATABASE_URI = 'sqlite:///' + CACHE_DATABASE_FILE

TPWD_DATA_DIR = '/home/wilsaj/data/tpwd/'

ECHO_SQLALCHEMY = True

TPWD_SOURCE = 'TPWDFiles'
TPWD_NETWORK = 'TPWDCoastalFisheries'
TPWD_VOCABULARY = 'TPWDCoastalFisheries'


site_list = ['aransas',
             'corpus_christi',
             'eastmatagorda',
             'galveston',
             'gulf',
             'lowerlagunamadre',
             'matagorda',
             'sabine',
             'sanantonio',
             'upperlagunamadre']


def tpwd_cache_variable(variable_code):
    return cache.CacheVariable(
        vocabulary=TPWD_VOCABULARY,
        code=variable_code,
        name=variable_code)


def commit_data_for_site(site_name):
    """commit data values to the database"""
    file_source = cache.CacheSource(url='file:///' + TPWD_SOURCE)
    csv_files = glob.glob('/'.join([TPWD_DATA_DIR, '/request_*/%s*' % site_name]))
    variable_codes = (
        'barometric_pressure',
        'temperature',
        'dissolved_oxygen',
        'salinity',
        'turbidity')

    variables = dict([code, tpwd_cache_variable(code)]
                     for code in variable_codes)

    for i, csv_file in enumerate(csv_files):
        with open(csv_file, 'rb') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if len(cache.db_session.new) > 15000:
                    cache.db_session.commit()

                site_code = site_code_hash(
                    row['major_area_code'],
                    row['minor_bay_code'],
                    row['station_code'],
                    row['start_latitude_num'],
                    row['start_longitude_num'])

                site = cache.CacheSite(
                    network=TPWD_NETWORK,
                    code=site_code,
                    latitude=row['start_latitude_num'],
                    longitude=row['start_longitude_num'],
                    source=file_source,
                    auto_add=True,
                    auto_commit=False,
                    skip_db_lookup=True)

                timestamp_format = '%d%b%Y:%H:%M:%S.000'
                timestamp = datetime.strptime(row['start_dttm'],
                                              timestamp_format)

                # skip dates from files that are not the 2009 files
                if timestamp.year == 2009 and not '20110524' in csv_file:
                    continue

                for code, cache_var in variables.items():
                    row_index = 'start_%s_num' % code
                    if row[row_index]:
                        timeseries = cache.CacheTimeSeries(
                            site=site,
                            variable=cache_var,
                            auto_add=True,
                            auto_commit=False,
                            skip_db_lookup=True)
                        timeseries.values.append(cache.DBValue(
                            timestamp=timestamp,
                            value=row[row_index],
                            timeseries=timeseries))

        cache.db_session.commit()


def site_code_hash(major_area_code, minor_bay_code, station_code,
                   latitude, longitude):
    """return hashed site code, this should provide a unique site code
    for each site and lat/long, though there is a small chance for
    collisions"""
    return '_'.join([major_area_code, minor_bay_code, station_code,
                     latitude.split('.')[-1][-4:],
                     longitude.split('.')[-1][:-4]])


def export_to_cache():
    cache.init_cache(CACHE_DATABASE_FILE, ECHO_SQLALCHEMY)
    for site in site_list:
        cache.clear_memory_cache()
        commit_data_for_site(site)


if __name__ == '__main__':
    export_to_cache()
