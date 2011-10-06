import logging

import wof

from pyhis_dao import PyhisDao

logging.basicConfig(level=logging.DEBUG)

TCEQ_DATABASE_URI = 'sqlite:////home/wilsaj/txhis/import_data/cache_files/tceq_pyhis_cache.db'
TCEQ_CONFIG_FILE ='tceq_config.cfg'

tceq_dao = PyhisDao(TCEQ_DATABASE_URI,
               'tceq_config.cfg')
app = wof.create_wof_app(tceq_dao, TCEQ_CONFIG_FILE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
