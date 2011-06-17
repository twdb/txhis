"""
export twdb data to pyhis cache format
"""
import os

import pyhis

CACHE_DIR = "cache_files/"
CACHE_DATABASE_FILE = os.path.join(CACHE_DIR, "twdb_pyhis_cache.db")
CACHE_DATABASE_URI = 'sqlite:///' + CACHE_DATABASE_FILE

WOF_CACHE_DATABASE_URI = 'sqlite:///cache_files/twdb_wof_pyhis_cache.db'

ECHO_SQLALCHEMY = False
TWDB_WSDL_URL = 'http://his.crwr.utexas.edu/TWDB_Sondes/cuahsi_1_0.asmx?WSDL'

TWDB_NETWORK = 'TWDBSurfaceWater'
TWDB_VOCABULARY = 'TWDBSurfaceWater'


WDFT_PARAMETERS = {
    # 'wof_parameter_code': ('wdft_parameter_code', 'unit_code', 'parameter_description')
    'CON001': ('water_specific_conductance', 'mScm', 'Specific Conductance(Normalized @25degC)'),
    'DIO001': ('water_dissolved_oxygen_concentration', 'mgl', 'Dissolved Oxygen Concentration'),
    'GAH001': ('gage_height', 'ft', 'Gage Height'),
    'TEM001': ('water_temperature', 'degC', 'Water Temperature'),
    'PEH001': ('water_ph', 'dimensionless', 'pH Level'),
    'SAL001': ('salinity', 'ppt', 'Salinity'),
    }

UNITS_DICT = {
    # 'key': ('parameter name', standard_units, function_that_converts_to_standard_units)
    'degC': ('degrees celsius', 'degC', None),
    'ft': ('feet', 'ft', None),
    'ntu': ('nephelometric turbidity units', 'ntu', None),
    'mgl': ('milligrams per liter', 'mgl', None),
    'ppt': ('parts per thousand', 'ppt', None),
    'dimensionless': ('dimensionless', 'dimensionless', None),
    'mScm': ('millisiemens per centimeter', 'uScm', lambda x: x / 1000.0),
    'uScm': ('microsiemens per centimeter', 'uScm', None),
   }


def cache_normalized_values():
    pyhis.cache.init_cache(WOF_CACHE_DATABASE_URI, ECHO_SQLALCHEMY)
    #pyhis.cache.cache_all(TWDB_WSDL_URL)

    # pyhis.cache.init_cache() will close out db_session to save
    # memory. But in this case, we need to hold on to the db_session
    # so we want to make a copy of the pyhis cache db session and set
    # the pyhis.cache.db_session to None so we can still have access
    # to the db_session that has cached all the values from the WOF
    # web service
    wof_db_session = pyhis.cache.db_session
    pyhis.cache.db_session = None

    # now initialize the cache that will point to our database
    # file that will be cached into gems
    pyhis.cache.init_cache(CACHE_DATABASE_FILE, ECHO_SQLALCHEMY)
    wdft_db_session = pyhis.cache.db_session

    wof_source = wof_db_session.query(pyhis.cache.DBSource).one()
    wdft_source = pyhis.cache.CacheSource(
        url=wof_source.url)

    for wof_site in wof_db_session.query(pyhis.cache.DBSite).all():
        wdft_site = pyhis.cache.CacheSite(
            code=wof_site.code,
            network=TWDB_NETWORK,
            name=wof_site.name,
            site_id=wof_site.site_id,
            latitude=wof_site.latitude,
            longitude=wof_site.longitude,
            auto_commit=False,
            source=wdft_source)

        for wof_timeseries in wof_site.timeseries_list.all():
            if wof_timeseries.values.count() > 0:
                cache_timeseries(wof_timeseries, wdft_site, wdft_db_session)

    wdft_db_session.commit()


def cache_timeseries(wof_timeseries, wdft_site, wdft_db_session):
    wof_variable = wof_timeseries.variable
    wof_units = wof_variable.units

    wdft_parameter_code = WDFT_PARAMETERS[wof_variable.code][0]
    wdft_parameter_name = WDFT_PARAMETERS[wof_variable.code][2]

    twdb_units_code = WDFT_PARAMETERS[wof_variable.code][1]
    wdft_converted_units_code = UNITS_DICT[twdb_units_code][1]
    wdft_converted_units_name = UNITS_DICT[wdft_converted_units_code][0]

    conversion_func = UNITS_DICT[twdb_units_code][2]
    if not conversion_func:
        conversion_func = lambda x: x

    wdft_units = pyhis.cache.CacheUnits(
        code=wdft_converted_units_code,
        abbreviation=wdft_converted_units_code,
        name=wdft_converted_units_name)

    wdft_variable = pyhis.cache.CacheVariable(
        name=wdft_parameter_name,
        code=wdft_parameter_code,
        vocabulary=TWDB_VOCABULARY)

    wdft_timeseries = pyhis.cache.CacheTimeSeries(
        site=wdft_site,
        variable=wdft_variable,
        auto_commit=False)

    for wof_value in wof_timeseries.values.all():
        if len(wdft_db_session.new) > 5000:
            wdft_db_session.commit()
        wdft_value = pyhis.cache.DBValue(
            timestamp=wof_value.timestamp,
            value=conversion_func(wof_value.value))
        wdft_timeseries.values.append(wdft_value)


if __name__ == '__main__':
    cache_normalized_values()
