#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import os
#import gettext
import cgi
import memcache

from sqlalchemy import create_engine

# working directory
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

#URLPRIFIX
PREFIX = "/appsWS/"

# debug
#web.config.debug = False

# memcache
MC = memcache.Client(['127.0.0.1:11211'], debug=0) #Change this
MLEADING= 'appsWS' #change this
class MCKEY:
    setting = MLEADING + '$setting'
    cloud = MLEADING + '$cloud'

# send email
web.config.smtp_server = 'smtp.gmail.com' #Chang this
web.config.smtp_port = 587 #Change this (or stay the same if you want to use google smtp)
web.config.smtp_username = 'tonytan198211@gmail.com' #Change this
web.config.smtp_password = '12345678abc' #Change this
web.config.smtp_starttls = True

# max upload file size
cgi.maxlen = 20*1024*1024 #20MB (change it to your appropriate size)

# enable i18n 
#i18n_support = False

# if enable i18n , change language to your locale
# your should make your own translation
LANGUAGE = 'en_US'

# timezone list -- http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIMEZONE = 'America/Chicago'

# you can edit below

#Your google cse id, eg: 001122334455667788990:cp2tpvhrc34 

#Your google analytics UA ID, eg: UA-11223344-1

# secret key -- change it as you wish. once setup you should never rechange it
SECRET_KEY = '!$6&p2gt=!=h)aifebdq2ei$*)z0o!^czhz*461dpwke--kn66'

# media path to store 
MEDIA = 'media' # eg: you working path is path/www, then your media dir is path/www/media
MEDIA_URL = '/media/' # this need static server support

# database engine
# database type, change to your appropriate databatype 
# at this point, it supports all possible datatypes that sqlalchemy supports
dbType = 'sqlite'
# database connection string, including 2 parts: database name, path&&other
#if we use other type of DBMS (eg: mssql, sqlserver, the connection string will be fairly
#complicated)
dbName = "DatabaseModel/HisCentralRegisterFinalDBFile.db"
connectStr = "/".join([ROOT_PATH,dbName])
#connectStr = "/".join(['/' + os.getcwd(),dbName])
#module_name='pyodbc'
ENGINE = create_engine(":///".join([dbType,connectStr]), echo=True)
session_db = web.database(dbn='sqlite', db=connectStr)
STORE = web.session.DBStore(session_db, 'session')
#STORE = web.session.DiskStore('../session/')

# ==================== system configuration ================== #
# don't edit below ~~~ except you know what you are doing. yes, you know

MEDIA_PATH = os.path.join(ROOT_PATH, MEDIA).replace('\\','/')

#locale_path = os.path.join(path,'i18n').replace('\\','/')
#gettext.install('messages', locale_path, unicode=True)
#if i18n_support:
#    gettext.translation('messages', locale_path, languages = [language]).install(True)

# environment
os.environ['TZ'] = TIMEZONE
web.config.session_parameters['cookie_name'] = 'TXHIS_id'
#web.config.session_parameters['cookie_domain'] = 'http://example.com'
web.config.session_parameters['secret_key'] = 'TXHIS_ID3c8A9B2hhjqefa'
#web.config.session_parameters['timeout'] = 3600  # one hour
#web.config.session_parameters['ignore_expiry'] = False
#web.config.session_parameters['ignore_change_ip'] = False

VERSION = 1.0
