import logging
import os
import socket

import wof

from pyhis_dao import PyhisDao

logging.basicConfig(level=logging.DEBUG)

if socket.gethostname() == 'Midgewater':
    DEPLOYED = True
else:
    DEPLOYED = False

APP_NAME = 'tceq'

if DEPLOYED:
    DEPLOYMENT_DIR = '/space/www/wofpy_deployments/%s_deployment' % APP_NAME
else:
    DEPLOYMENT_DIR = os.path.abspath('../')

CACHE_DIR = os.path.join(DEPLOYMENT_DIR,
                         'cache/')
CONFIG_FILE = os.path.join(DEPLOYMENT_DIR,
                           APP_NAME + '_config.cfg')

DATABASE_URI = 'sqlite:////' + os.path.join(
    CACHE_DIR, APP_NAME + '_pyhis_cache.db')

app_dao = PyhisDao(DATABASE_URI,
                   CONFIG_FILE)
app = wof.create_wof_app(app_dao, CONFIG_FILE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
