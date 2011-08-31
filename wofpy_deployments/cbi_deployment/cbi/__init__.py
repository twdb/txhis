import logging
import os
import tempfile

import soaplib
from soaplib.core.server import wsgi
from werkzeug.wsgi import DispatcherMiddleware
import wof

from cbi_dao import CbiDao

# CBI_DEPLOYMENT_DIR = '/space/www/wofpy_deployments/cbi_deployment'
# CBI_CACHE_DIR = os.path.join(CBI_DEPLOYMENT_DIR,
#                              'cache/')
CBI_DEPLOYMENT_DIR = './'
CBI_CACHE_DIR = tempfile.gettempdir()

CBI_CONFIG_FILE = os.path.join(CBI_DEPLOYMENT_DIR,
                               'cbi_config.cfg')
CBI_CONFIG_FILE = 'cbi_config.cfg'

CBI_CACHE_DATABASE_URI = 'sqlite:////' + os.path.join(
    CBI_CACHE_DIR, 'cbi_dao_cache.db')

logging.basicConfig(level=logging.DEBUG)

cbi_dao = CbiDao(CBI_CONFIG_FILE, database_uri=CBI_CACHE_DATABASE_URI)
app = wof.create_wof_app(cbi_dao, CBI_CONFIG_FILE)

app.run()
