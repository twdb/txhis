'''
Created on Dec 3, 2010

This module is for Admin (Django-Style database CUID module)

@author: tony
'''
import web


from views import *
from urls import urls

Admin_app = web.application(urls, locals(), autoreload = True)