'''
Created on Dec 3, 2010

@author: tony
'''
from formalchemy import FieldSet,Field,Grid,validators,types
from formalchemy.i18n import _, get_translator
from formalchemy.fields import _pk
import sys
sys.path.append('..')

from DatabaseModel.model import User 

__all__ = ['get_forms']

def getExistingUserPW(userObj):
    return userObj.password
    

class UserFieldSet_edit(FieldSet):
    """Used to edit users"""
    def __init__(self):
        """Pre-configuration"""
        FieldSet.__init__(self, User)

        self.add(Field('passwd1',value = getExistingUserPW))
        self.add(Field('passwd2',value = getExistingUserPW))
        inc = [self.username,
               self.passwd1.password().label(u'Password'),
               self.passwd2.password().label(u'Confirm') \
                   .validate(validators.passwords_match('passwd1')),
               self.email,
               self.fullname
               ]
        self.configure(include=inc)
        #self.configure(options=[self.priority.dropdown(options=["Site/Variable Admin","DataiPublish/QAQC Supervisor","QAQC Staff","Data Upload Staff"])])

class UserFieldSet_add(FieldSet):
    """Used to edit users"""
    def __init__(self):
        """Pre-configuration"""
        FieldSet.__init__(self, User)

        self.add(Field('passwd1'))
        self.add(Field('passwd2'))
        inc = [self.username,
               self.passwd1.password().label(u'Password'),
               self.passwd2.password().label(u'Confirm') \
                   .validate(validators.passwords_match('passwd1')),
               self.email,
               self.fullname
               ]
        self.configure(include=inc)
        #self.configure(options=[self.priority.dropdown(options=["Site/Variable Admin","DataiPublish/QAQC Supervisor","QAQC Staff","Data Upload Staff"])])

def get_forms(model, model_URL, **kargs):
    """scan model and forms"""
    # generate missing forms, grids
    result_forms = dict()
    if model.__name__ == "User":
        try:
            if kargs['user_flag'] == "add": 
                result_forms['fieldsets'] = UserFieldSet_add()
            elif kargs['user_flag'] == "edit":
                result_forms['fieldsets'] = UserFieldSet_edit()
        except KeyError, e:
            raise NameError('No proper User flag (add/edit)')
    else:
        result_forms['fieldsets'] = FieldSet(model())
        if model.__name__ == "Sources":
            result_forms['fieldsets'].configure(exclude = [result_forms['fieldsets']['availableParameterInfo']])
    result_forms['grids'] = Grid(model)
    exclude_attrs = [result_forms['grids'][i] for i in result_forms['grids']._fields.keys() if 'name' not in i.lower()]
    result_forms['grids'].configure(exclude=exclude_attrs)
    # add Edit + Delete link to grids
    def edit_link():
        return lambda item: '<a href="%(url)sedit/%(id)s" title="%(label)s" class="icon edit">%(label)s</a>' % dict(
                    url=model_URL, id=_pk(item),
                    label=get_translator().gettext('edit'))
    def delete_link():
        return lambda item: '''<form action="%(url)sdelete/%(id)s" method="POST">
                                <input type="submit" class="icon delete" title="%(label)s" value="" />
                                <input type="hidden" name="_method" value="DELETE" />
                                </form>
                            ''' % dict(
                                    url=model_URL, id=_pk(item),
                                    label=get_translator().gettext('delete'))
    result_forms['grids'].append(Field('edit', types.String, edit_link()))
    result_forms['grids'].append(Field('delete', types.String, delete_link()))
    result_forms['grids'].readonly = True 

    return result_forms
