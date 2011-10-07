import logging
import os

import wof

from pyhis_dao import PyhisDao

logging.basicConfig(level=logging.DEBUG)

DEPLOYED = True

if DEPLOYED:
    TPWD_DEPLOYMENT_DIR = '/space/www/wofpy_deployments/tpwd_deployment'
else:
    TPWD_DEPLOYMENT_DIR = './'

TPWD_CACHE_DIR = os.path.join(TPWD_DEPLOYMENT_DIR,
                              'cache/')
TPWD_CONFIG_FILE = os.path.join(TPWD_DEPLOYMENT_DIR,
                                'tpwd_config.cfg')

TPWD_DATABASE_URI = 'sqlite:////' + os.path.join(
    TPWD_CACHE_DIR, 'tpwd_pyhis_cache.db')

tpwd_dao = PyhisDao(TPWD_DATABASE_URI,
                    'tpwd_config.cfg')
app = wof.create_wof_app(tpwd_dao, TPWD_CONFIG_FILE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
