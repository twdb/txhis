'''
Created on Dec 3, 2010

@author: tony
'''
import web

#decorator for each function to validate if a client has been logged in
def is_login(func):
    def Function(*args):
        if not web.ctx.session.isAuth:
            raise web.seeother('/appsWS/login',absolute=True)
        else:
            return func(*args)
    return Function