from __future__ import absolute_import

import soaplib.core
from sqlalchemy.engine import create_engine
from sqlalchemy import orm
from soaplib.core.server import wsgi

import service


def create_app(database_uri):
    engine = create_engine(database_uri)
    db_session = orm.scoped_session(orm.sessionmaker(bind=engine))

    CentralRegistryService = service.create_registry_service(db_session)

    soap_application = soaplib.core.Application(
        [CentralRegistryService], 'tns')
    return wsgi.Application(soap_application)
