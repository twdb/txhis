#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import web
from web.utils import Storage

from dbcenter import *
from config import VERSION, MC, MCKEY


class BasicInfo:
    version = VERSION
    now = datetime.datetime.now()
    def __init__(self):
        #self.setting = dbsetting.one()
        self.user = web.ctx.session.user
        self.db_message = web.ctx.session.db_opinfo
        #self.god = dbgod.who(pk=1)

class Widget:
    def __init__(self):
        self.entries = self.pub_entries()[:13]
        self.tag_cloud = dbtag.cloud()
        self.categories = dbcategory.total()
        self.links = dblink.total() #TODO limit
        self.pages = dbpage.total()
        self.user_widgets = dbwidget.total()
        self.nav_pages = self.pages[:5]
        self.archive_dates = self.entry_dates()

    def pub_entries(self):
        data = dbentry.total('public')
        return data
    def entry_dates(self):
        yms = dbentry.year_month()
        data = []
        for ym in yms:
            year = ym[:4]
            month = ym[5:]
            data.append((year,month))
        return data
