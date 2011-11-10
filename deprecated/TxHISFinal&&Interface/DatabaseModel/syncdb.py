'''
Created on Oct 5, 2010

@author: CTtan
'''
import os
import model
from sqlalchemy.engine import create_engine

dbType = 'sqlite'
#dbType = 'mssql'
dbName = "HisCentralRegisterFinalDBFile.db"
#dbName = '@localhost:3108/TXHISDB'
user = ''
password = ''


if user or password:
    idString = ':'.join([user, password])
else:
    idString = ''


if dbType == "sqlite":
    # in case of sqlite, we need to use the absolute path of database file
    DBDIRPATH = os.path.abspath(os.path.dirname(__file__))
    dbName = "".join(['/', os.path.join(DBDIRPATH, dbName)])


DBENGINE = create_engine("%s://%s%s" % (dbType, idString, dbName))


def main_syncdb(dbType, user, password, dbName):
    #create database from the model's schema. This is a little bit
    #fuzzy because sqlite doesn't really have user/pw login
    model.metadata.bind = DBENGINE
    model.metadata.create_all(checkfirst=True)

if __name__ == "__main__":
    print "Creating HIS Central Registry Database tables......"
    main_syncdb(dbType, user, password, dbName)
    print "HIS Central Registry Database create complete......"
