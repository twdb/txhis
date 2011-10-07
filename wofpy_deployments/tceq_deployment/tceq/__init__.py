import logging
import os

import wof

from pyhis_dao import PyhisDao

logging.basicConfig(level=logging.DEBUG)

DEPLOYED = True

if DEPLOYED:
    TCEQ_DEPLOYMENT_DIR = '/space/www/wofpy_deployments/tceq_deployment'
else:
    TCEQ_DEPLOYMENT_DIR = './'

TCEQ_CACHE_DIR = os.path.join(TCEQ_DEPLOYMENT_DIR,
                              'cache/')
TCEQ_CONFIG_FILE = os.path.join(TCEQ_DEPLOYMENT_DIR,
                                'tceq_config.cfg')

TCEQ_DATABASE_URI = 'sqlite:////' + os.path.join(
    TCEQ_CACHE_DIR, 'tceq_pyhis_cache.db')

tceq_dao = PyhisDao(TCEQ_DATABASE_URI,
                    'tceq_config.cfg')
app = wof.create_wof_app(tceq_dao, TCEQ_CONFIG_FILE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
