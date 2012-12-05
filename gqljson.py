#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time

from google.appengine.api import users
from google.appengine.ext import db
from django.utils import simplejson

class GqlEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return getattr(obj, '__json__')()

        if isinstance(obj, db.GqlQuery):
            return list(obj)
        elif isinstance(obj, db.Model):
            properties = obj.properties().items()
            output = {}
            for field, value in properties:
                output[field] = getattr(obj, field)
            return output
        elif isinstance(obj, datetime.datetime):
            output = {}
            fields = ['day', 'hour', 'microsecond', 'minute', 'month', 'second', 'year']
            #methods = ['ctime', 'isocalendar', 'isoformat', 'isoweekday', 'timetuple']
            for field in fields:
                output[field] = getattr(obj, field)
            #for method in methods:
            #    output[method] = getattr(obj, method)()
            output['epoch'] = time.mktime(obj.timetuple())
            return output
        elif isinstance(obj, time.struct_time):
            return list(obj)
        elif isinstance(obj, users.User):
            output = {}
            methods = ['nickname', 'email', 'auth_domain']
            for method in methods:
                output[method] = getattr(obj, method)()
            return output

        return simplejson.JSONEncoder.default(self, obj)

def encode(input):
    return GqlEncoder().encode(input)  