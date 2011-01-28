#!/usr/bin/env python
# -*- coding: utf-8 -*-
from web import form

re_email = form.regexp(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$','Invalid Email')
re_url = form.regexp(r'^https?:\/\/\S{3,100}$','Invalid URL')
re_username = form.regexp(r'.+_.+', 'Please enter a valid user name')

login_form = form.Form(
    form.Textbox('username',
            form.notnull, re_username,
            description = 'You username:',
            id = 'id_username'),
    form.Password('password',
            form.notnull,
            description = 'You password:'),
    description = "login form",
    id = "login-form"
)
