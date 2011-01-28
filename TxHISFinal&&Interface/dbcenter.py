#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web, os, datetime
from web.utils import Storage

from config import MEDIA_PATH, MC, MCKEY, ENGINE
from DatabaseModel.model import *

day = 60*60*24     #seconds in a day
week = day * 7     #seconds in a week
month  = day * 30  #seconds in a month

"""
Memcached table as of 09/22/2010:
    settings
potential cache list:
   
"""
###################################################
# These are databases accessor class with Django 
# query style
###################################################

class dbsetting:
    @classmethod
    def one(cls):
        """
        get the first record object from cached memory if it is there,
        or from database. This should be called after a
        sqlalchemy session has been bounded to web context
        """
        query = web.ctx.orm.query(Setting)
        key = MCKEY.setting
        data = MC.get(key)
        if data is not None:
            return data
        data = query.filter_by(pk=1).first()
        MC.set(key,data)
        return data
    @classmethod
    def dbone(cls):
        """
        get the first record object from database. 
        This should be called after a sqlalchemy session 
        has been bounded to web context
        """
        query = web.ctx.orm.query(Setting)
        data = query.filter_by(pk=1).first()
        return data 

class dbuser:
    @classmethod
    def who(cls,**kwargs):
        user = web.ctx.orm.query(User).filter_by(**kwargs).first()
        return user
    @classmethod
    def all(cls):
        return web.ctx.orm.query(User).all()
        
        
        
