"""
pull WOF data from web
"""
import os

import numpy as np

import pyhis
from pyhis import shapefile

CACHE_DIR = "cache_files/"
ECHO_SQLALCHEMY = False
STATE_SHAPEFILE = 'usa_state_shapefile.shp'

services = [
    # {'cache_file': "usgs_pyhis_cache.db",
    #  'wsdl': 'http://river.sdsc.edu/wateroneflow/NWIS/DailyValues.asmx?WSDL',
    #  'use_shapefile': True,
    # },
    {'cache_file': 'cbi_pyhis_cache.db',
     # 'wsdl': 'http://midgewater.twdb.state.tx.us/cbi/soap/wateroneflow.wsdl'}
     'wsdl': 'http://localhost:5000/soap/wateroneflow.wsdl'}
    ]


for service in services:
    cache_uri = 'sqlite:///' + os.path.join(CACHE_DIR, service['cache_file'])
    pyhis.cache.init_cache(cache_uri, ECHO_SQLALCHEMY)

    if service.get('use_shapefile', None):
        states_shp = shapefile.Reader(STATE_SHAPEFILE)
        for shape_record in states_shp.shapeRecords():
            if shape_record.record[1] == 'Texas':
                texas = shape_record
                break

        texas_verts = np.array(texas.shape.points)
        source = pyhis.Source(service['wsdl'])
        texas_sites = source.get_sites_within_polygon(texas_verts).values()
        pyhis.cache.cache_sites(texas_sites)

    else:
        source = pyhis.Source(service['wsdl'])
        pyhis.cache.cache_all(service['wsdl'])

# usgs_source = pyhis.Source(USGS_WSDL_URL)
# pyhis.cache.cache_all(USGS_WSDL_URL)
