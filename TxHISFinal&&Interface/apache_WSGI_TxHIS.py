#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SWMIS: a TWDB data import/qaqc application supported by web.py"""

import web,os,sys

from sqlalchemy.orm import scoped_session, sessionmaker

from config import STORE, ENGINE, ROOT_PATH

from Log_in_and_out import Log_in_and_out_app
from Admin import Admin_app
from TxHISCentralRegistryWebService import WS_app

urls = (
    '/appsWS/Admin',Admin_app,
    '/appsWS/TXHISCentralService', WS_app,
    '/appsWS',Log_in_and_out_app
)

app = web.application(urls, globals(), autoreload=True)

if web.config.get('_session') is None:
    session = web.session.Session(
        app,
        STORE,
        initializer={'isAuth':False,
                     'user':{'username':'Anonymous','nickname':'Anonymous'},
                     'fs': None
                    },
    )
else:
    session = web.config._session

def sa_handler(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=ENGINE))
    try:
        return handler()
    except web.HTTPError:
        web.ctx.orm.commit()
        raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
app.add_processor(sa_handler)

def session_hook():
    web.ctx.session = session
    
app.add_processor(web.loadhook(session_hook))
application = app.wsgifunc()

#if '__main__' == __name__: 
#    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func,addr)
#    app.run()
