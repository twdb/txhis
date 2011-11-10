import web,hashlib,datetime,codecs,sys
from formalchemy import Grid

sys.path.append('..')

from config import SECRET_KEY, MC, MCKEY
from utils.LoginStatusCheck import *

from dbcenter import dbuser

from module_render import render
from forms import *



#====================================================================#
# user classes
#====================================================================#
class webActions:
    def __init__(self,name,url):
        self.name, self.url = name, url

class index:
    def GET(self, slash):
        if slash:
            raise web.seeother(web.ctx.home)
        swmis_var = { }
        if web.ctx.session.isAuth: 
            available_actions = [webActions("Admin",'/appsWS/Admin'), 
                             webActions("WSDL", '/appsWS/TXHISCentralService?wsdl')]
        else:
            available_actions = [webActions("WSDL", '/appsWS/TXHISCentralService?wsdl')] 
        swmis_var['available_actions'] = available_actions 
        return render("index.html",**swmis_var)
    
class login:
    def GET(self):
        if web.ctx.session.isAuth:
            raise web.seeother(web.ctx.home)
        form = login_form()
        swmis_var = { }
        swmis_var['form'] = form
        return render("login.html", **swmis_var)
    def POST(self):
        swmis_var = { }
        form = login_form()
        if form.validates():
            username = form.d.username
            passwd = form.d.password
            user = dbuser.who(username=username)
            if user:
                passwd = hashlib.sha1(SECRET_KEY+passwd).hexdigest()
                if passwd == user.password:
                    web.ctx.session.isAuth = True
                    #needs to modify here to add 'roles'
                    sdict = { 'username': user.username, 'fullname': user.fullname}
                    web.ctx.session.user = sdict
                    raise web.seeother(web.ctx.home)
                else:
                    swmis_var['error'] = 'Invalid Password'
                    #return passwd, user.password
            else:
                swmis_var['error'] = 'Can\'t find this username...'
        else:
            swmis_var['error'] = 'Malformed username...'
        swmis_var['form'] = form
        return render('login.html', **swmis_var)
    
class logout:
    @is_login
    def GET(self):
        web.ctx.session.kill()
        raise web.redirect('/')
    

