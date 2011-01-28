'''
Created on Dec 3, 2010

urls controller for Admin(Database CUID) module

@author: tony
'''
urls = [
    '(/)?',   'admin',
    '/([^/]*)/',  'generic_model_list',
    '/([^/]*)/edit/(\d+)',  'generic_model_edit',
    '/([^/]*)/add',  'generic_model_add',
    '/([^/]*)/delete/(\d+)',  'generic_model_delete'   
    #'/add_user','add_user'
]

