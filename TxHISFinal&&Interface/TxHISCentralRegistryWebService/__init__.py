'''
Created on Sep 21, 2010

This module is for HIS web service part

@author: tony
'''
import web

from urls import urls
from TxHISCentralView import *

WS_app = web.application(urls, locals(), autoreload = True)
