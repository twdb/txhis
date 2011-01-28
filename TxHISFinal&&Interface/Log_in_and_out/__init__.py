'''
Created on Sep 21, 2010

This module is for User login/logout

@author: tony
'''
import web


from views import *
from urls import urls

Log_in_and_out_app = web.application(urls, locals(), autoreload = True)