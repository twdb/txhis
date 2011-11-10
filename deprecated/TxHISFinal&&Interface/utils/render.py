#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Sep 22, 2010

@author: tony
'''
from jinja2 import Environment, FileSystemLoader

class render_jinja:
    """
    modified from web.contrib.template render module.
    for rendering to jinja2 template
    """
    def __init__(self, *arg, **kwargs):
        extensions = kwargs.pop('extensions', [])
        filters = kwargs.pop('filters', [])
        gvars   = kwargs.pop('gvars', {})       #global vars
        
        self._lookup = Environment(loader=FileSystemLoader(*arg, **kwargs),
                                    extensions = extensions)
        self._lookup.globals.update(gvars)
        self._lookup.filters.update(filters)
        
    def render_template(self, name, **kwargs):
        t = self._lookup.get_template(name)
        return t.render(**kwargs)
    
def render_json(value):
    """
    this is for render JSON variables/objects. 
    For javascript enhancement 
    """
    pass