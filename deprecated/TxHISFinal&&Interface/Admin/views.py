'''
Created on Dec 3, 2010

views for admin module

@author: tony
'''
import sys
sys.path.append("..")
from sqlalchemy.orm import object_session

from utils.LoginStatusCheck import *
from DatabaseModel.model import *
from admin_utils import *
from config import SECRET_KEY

from webhelpers.paginate import Page
import web,hashlib

from module_render import render

all_available_models = [Setting, User, Sources, VariableMapping, Variables, Units, UnitConversionFormula] 

#====================================================================#
# user classes
#====================================================================#
class admin:
    """
    Admin module views. List available models/tables for this user to 
    perform CUID
    """
    @is_login
    def GET(self, slash):
        #Here could add model screening logic based on the user's role
        swmis_var = { }
        swmis_var['available_models'] = all_available_models
        return render("admin_index.html",**swmis_var)
    
class generic_model_list:
    _paginate = dict()
    @is_login
    def GET(self, model_name):
        model_params = web.input(page=1)
        model_class = eval(model_name)
        query = web.ctx.orm.query(model_class)
        currentURL = web.ctx.homepath + web.ctx.path
        def get_page_url(page, partial=None):
            url = "%s?page=%s" % (currentURL, page)
            if partial:
                url += "&partial=1"
            return url
        self._paginate['url'] = get_page_url
        page = Page(query, page=int(model_params.page), items_per_page=15, **self._paginate)
        m_grid = get_forms(model_class, currentURL, user_flag = 'add')['grids']
        m_grid = m_grid.bind(instances=page, session=None)
        clsnames = [f.relation_type().__name__ for f in m_grid._fields.itervalues() if f.is_relation]
        #remove duplicates
        clsnames = list(set(clsnames))
        swmis_var = {}
        swmis_var['model_name'] = model_name
        swmis_var['clsnames'] = clsnames
        swmis_var['page'] = page
        swmis_var['grid'] = m_grid
        return render("admin_list.html",**swmis_var)
    
class generic_model_edit:
    @is_login
    def GET(self, model_name, item_pk):
        model_class = eval(model_name)
        m_fieldset = get_forms(model_class, (web.ctx.homepath + web.ctx.path), user_flag = 'edit' )['fieldsets']
        instance =  web.ctx.orm.query(model_class).get(item_pk)
        m_fieldset = m_fieldset.bind(instance)
        swmis_var = {}
        swmis_var['model_name'] = model_name
        swmis_var['fs'] = m_fieldset
        swmis_var['item_pk'] = item_pk         
        return render("admin_edit.html",**swmis_var)
    def POST(self,model_name, item_pk):
        model_class = eval(model_name)
        m_fieldset = get_forms(model_class, (web.ctx.homepath + web.ctx.path), user_flag = 'edit')['fieldsets']
        instance =  web.ctx.orm.query(model_class).get(item_pk)
        post_data, password_changed = web.input(), False
        if post_data.has_key("User--passwd1") and post_data.has_key("User--passwd2") \
             and post_data.has_key("User--passwd1") != instance.password:
            password_changed = True
            password = hashlib.sha1(SECRET_KEY+post_data["User--passwd1"]).hexdigest()
        m_fieldset = m_fieldset.bind(instance,data = post_data)
        if m_fieldset.validate():
            m_fieldset.sync()
            web.ctx.orm.flush()
            if password_changed:
                m_fieldset.model.password = password
            if not object_session(m_fieldset.model):
                web.ctx.orm.add(m_fieldset.model)
                web.ctx.session.db_opinfo = 'The Record already exists... (table: %s)' % model_name
                return web.seeother('/%s/'% model_name) 
            try:
                web.ctx.orm.commit() 
                web.ctx.session.db_opinfo = 'The record is updated successfully... (table: %s)' % model_name   
            except Exception,e:
                web.ctx.session.db_opinfo = str(e)
        else:
            web.ctx.session.db_opinfo = 'Validation error for new record... (table: %s)' % model_name
            return web.seeother('/%s/add'% model_name)
        
        return web.seeother('/%s/'% model_name)
    
class generic_model_add:
    @is_login
    def GET(self, model_name):
        model_class = eval(model_name)
        m_fieldset = get_forms(model_class, (web.ctx.homepath + web.ctx.path), user_flag = 'add')['fieldsets']
        instance = m_fieldset.model.__class__
        m_fieldset = m_fieldset.bind(instance,session = web.ctx.orm)
        swmis_var = {}
        swmis_var['model_name'] = model_name
        swmis_var['fs'] = m_fieldset         
        return render("admin_add.html",**swmis_var)
        #return "Hello World\n Edit:  %s... %s" % (model_name, m_fieldset._fields)
    def POST(self,model_name):
        model_class = eval(model_name)
        m_fieldset = get_forms(model_class, (web.ctx.homepath + web.ctx.path), user_flag = 'add')['fieldsets']
        instance = m_fieldset.model.__class__
        post_data = web.input()
        if post_data.has_key("User--passwd1") and post_data.has_key("User--passwd2"):
            password = hashlib.sha1(SECRET_KEY+post_data["User--passwd1"]).hexdigest()
        m_fieldset = m_fieldset.bind(instance,session = web.ctx.orm,data = post_data)   
        if m_fieldset.validate():
            m_fieldset.sync()
            web.ctx.orm.flush()
            if model_name == 'User':
                m_fieldset.model.password = password
            if not object_session(m_fieldset.model):
                web.ctx.orm.add(m_fieldset.model)
                web.ctx.session.db_opinfo = 'The Record already exists... (table: %s)' % model_name
                return web.seeother('/%s/'% model_name) 
            try:
                web.ctx.orm.commit() 
                web.ctx.session.db_opinfo = 'New record created... (table: %s)' % model_name   
            except Exception,e:
                web.ctx.session.db_opinfo = str(e)
        else:
            web.ctx.session.db_opinfo = 'Validation error for new record... (table: %s)' % model_name
            return web.seeother('/%s/add'% model_name)

        return web.seeother('/%s/'% model_name)

class generic_model_delete:
    def POST(self,model_name,item_pk):
        model_class = eval(model_name)
        try:
            instance =  web.ctx.orm.query(model_class).get(item_pk)
            web.ctx.orm.delete(instance)
            web.ctx.orm.commit()
            web.ctx.session.db_opinfo = 'A record has been deleted... (table: %s)' % model_name   
        except Exception, e:
            str(e)
        return web.seeother('/%s/'% model_name)
        

if __name__ == "__main__":
    pass
    