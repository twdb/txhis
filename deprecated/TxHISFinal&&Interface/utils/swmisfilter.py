#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib,re,datetime,cgi
from markdown import markdown

def truncate(value, length=50,killwords=False, end='...'):
    ''' from jinja '''
    if len(value) <= length:
        return value
    elif killwords:
        return value[:length] + end
    words = value.split(' ')
    result = []
    m = 0
    for word in words:
        m += len(word) + 1
        if m > length:
            break
        result.append(word)
    result.append(end)
    return u' '.join(result)

def gravatar(value, size=80):
    hash_email = hashlib.md5(value).hexdigest()
    avatar = 'http://www.gravatar.com/avatar/' + hash_email + '?s=%s' % size
    return avatar

def is_more(value):
    regex = r'(.*?)<!--\s+more\s+-->'
    m = re.findall(regex, value, re.U|re.S)
    if m:
        return True
    else:
        return False

def cut_more(value):
    regex = r'(.*?)<!--\s+more\s+-->'
    m = re.findall(regex, value, re.U|re.S)
    if m:
        return m[0]
    else:
        return value

def markcontent(value):
    content = markdown(value)
    regex = r'(<pre[^>]*?>)(.*?)(</pre>)'
    pattern = re.compile(regex, re.U|re.S)
    pres = pattern.findall(content)
    for pre in pres:
        old = ''.join(pre)
        new = pre[0] + cgi.escape(pre[1]) + pre[2]
        content = content.replace(old, new)
    return content

def linebreaks(value):
    value = re.sub(r'\r\n|\r|\n','\n', value)
    paras = re.split('\n{2,}', value)
    paras = [u'<p>%s</p>' % p for p in paras]
    return u'\n\n'.join(paras)

def filesize(value):
    value = float(value)
    if value < 1024:
        return '%s B' % value
    if value < 1048576:
        result = round(value/1024.0,2)
        return '%s K' % result
    result = round(value/1048576.0,2)
    return '%s M' % result

def humantime(value):
    num = int(value)
    if num < 60:
        return '%s s' % num
    if num < 3600:
        return '%s m' % (num/60)
    if num < 86400:
        return '%s h' % (num/3600)
    return '%s d' % (num/86400)

def safecomment(value):
    tags_re = u'(html|head|meta|title|link|script|body|div|frame|iframe|form|input|textarea|button|select|option|img|table|tbody|tfoot|thead|td|th|ul|ol|li|span|p|h1|h2|h3|h4|h5|h6|font)'
    start = re.compile(ur'<%s(/?>|(\s+[^>]*>))' % tags_re, re.U|re.S)
    end = re.compile(ur'</%s>' % tags_re)
    value = start.sub(u'', value)
    value = end.sub(u'', value)
    return value

def to_datetime(value):
    ''' 2010-06-15 9:50:23 ->  datetime.datetime(2010,6,15,9,50,23) '''
    parse_time = datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
    return parse_time

def strdate(value):
    ''' datetime to 2010-10-11 '''
    return value.strftime('%Y-%m-%d')

def strtime(value):
    ''' iso time '''
    return value.strftime('%Y-%m-%d %H:%M:%S')

def fashiondate(value):
    return value.strftime("%b %Y")

def ym_datetime(year,month):
    d = datetime.datetime(int(year),int(month),1)
    return d
