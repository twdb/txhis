'''
Created on Oct 7, 2010

@author: CTtan
'''
from ZSI.ServiceContainer import AsServer
from ZSI import dispatch
from TxHISCentralRegistryImp import TxHISCentralRegistryImp
import sys

sys.path.append('..')

from sqlalchemy import orm

from DatabaseModel.model import *
from DatabaseModel.syncdb import DBENGINE


if __name__ == "__main__":
    port = 9080
    ServiceInstance = TxHISCentralRegistryImp('TXHISCentralService')
    ServiceInstance.dbsession = orm.scoped_session(orm.sessionmaker(bind=DBENGINE))
    AsServer(port,(ServiceInstance,))