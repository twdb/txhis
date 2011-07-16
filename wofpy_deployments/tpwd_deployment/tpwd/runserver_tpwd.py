import logging

import soaplib
from soaplib.core.server import wsgi
from werkzeug.wsgi import DispatcherMiddleware

from wof import WOF
from wof.soap import create_wof_service_class
from wof.flask import create_app, config

from pyhis_dao import PyhisDao

logging.basicConfig(level=logging.DEBUG)


TPWD_DATABASE_URI = 'sqlite:////home/wilsaj/txhis/import_data/cache_files/tpwd_pyhis_cache.db'

dao = PyhisDao(TPWD_DATABASE_URI,
               'tpwd_config.cfg')

tpwd_wof = WOF(dao)
tpwd_wof.config_from_file('tpwd_config.cfg')

app = create_app(tpwd_wof)
app.config.from_object(config.DevConfig)

TPWDWOFService = create_wof_service_class(tpwd_wof)

soap_app = soaplib.core.Application(services=[TPWDWOFService],
                                    tns='http://www.cuahsi.org/his/1.0/ws/',
                                    name='WaterOneFlow')

soap_wsgi_app = soaplib.core.server.wsgi.Application(soap_app)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/soap/tpwd': soap_wsgi_app
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
