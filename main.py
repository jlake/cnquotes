#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import cgi
import random
import re
import urllib

from datetime import datetime, date, timedelta

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from django.core.paginator import ObjectPaginator, InvalidPage
from django.utils import simplejson

import gqljson

#=================== GLOBAL ===================#
PAGESIZE = 20
PAGERANGE = 10

#if sys.getdefaultencoding() != 'utf8':
#    reload(sys) 
#    sys.setdefaultencoding('utf8')

#=================== MODELS ===================#
# table: Quotes 
class Quotes(db.Model):
    quotes = db.TextProperty()
    dynasty = db.StringProperty()
    category = db.StringProperty()
    author = db.StringProperty()
    book = db.StringProperty()
    vote_cnt = db.IntegerProperty(default = 0)
    user = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

# table: Dynasty 
class Dynasty(db.Model):
    name = db.StringProperty()
    quotes_cnt = db.IntegerProperty(default = 0)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

# table: Category 
class Category(db.Model):
    name = db.StringProperty()
    quotes_cnt = db.IntegerProperty(default = 0)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

# table: Author 
class Author(db.Model):
    name = db.StringProperty()
    quotes_cnt = db.IntegerProperty(default = 0)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

# table: Book 
class Book(db.Model):
    name = db.StringProperty()
    quotes_cnt = db.IntegerProperty(default = 0)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

#=================== FUNCTIONS ===================#
# function: render view
def _renderView(page, file, params={}):
    if not page.template_values:
        page.template_values = {}
    page.template_values.update(params)
    path = os.path.join(os.path.dirname(__file__), file)
    page.response.out.write(template.render(path, page.template_values))

# function: send data in json
def _sendJson(self, outData):
    text = simplejson.dumps(outData, ensure_ascii=False) 
    self.response.content_type = 'application/json' 
    self.response.out.write(text)

# function: send Gql data in json
def _sendGqlJson(self, outData):
    text = gqljson.encode(outData);
    self.response.content_type = 'application/json' 
    self.response.out.write(text)

# function: convert array to csv text
def _arrayToCsv(outData):
    csv = ''
    for row in outData:
        csv += '"' + '","'.join(row) + '"\n'
    return csv

# function: get page data from selection
def _getPagenator(selection, page):
    try:
        current = int(page)
    except:
        current = 1

    paginator = ObjectPaginator(selection, PAGESIZE)
    maxpage = paginator.pages + 1
    if current >= maxpage:
        current = maxpage - 1
    elif current <= 0:
        current = 1

    if(current > PAGERANGE):
        start = current - round(PAGERANGE / 2)
    else:
        start = 1

    end = start + PAGERANGE
    if end > maxpage:
        end = maxpage

    paginator.items = paginator.get_page(current - 1)
    paginator.range = range(start, end)
    paginator.current = current
    paginator.previous = current - 1
    paginator.next = current + 1

    return paginator


# function: get input helper data
def _getHelperData(key):
    data = []
    if key == 'dynasty': 
        for row in Dynasty.all():
            data.append(row.name)
    elif key == 'category':
        for row in Category.all():
            data.append(row.name)
    elif key == 'author':
        for row in Author.all().order('-quotes_cnt').fetch(40):
            data.append(row.name)
    elif key == 'book':
        for row in Book.all().order('-quotes_cnt').fetch(40):
            data.append(row.name)

    return data

# function: update master data
def _updateMstData(quotes):
    selection = Dynasty.all().filter('name =', quotes.dynasty)
    if not selection.count(1):
        dynasty = Dynasty(name = quotes.dynasty)
        dynasty.put()

    selection = Category.all().filter('name =', quotes.category)
    if not selection.count(1):
        category = Category(name = quotes.category)
        category.put()

    selection = Author.all().filter('name =', quotes.author)
    if not selection.count(1):
        author = Author(name = quotes.author)
        author.put()

    selection = Book.all().filter('name =', quotes.book)
    if not selection.count(1):
        book = Book(name = quotes.book)
        book.put()

# function: update quotes count
def _updateQuotesCount():
    count = {
        'dynasty': {},
        'category': {},
        'author': {},
        'book': {},
    }
    for quotes in Quotes.all():
        key = quotes.dynasty
        if count['dynasty'].has_key(key):
            count['dynasty'][key] += 1
        else:
            count['dynasty'][key] = 1

        key = quotes.category
        if count['category'].has_key(key):
            count['category'][key] += 1
        else:
            count['category'][key] = 1

        key = quotes.author
        if count['author'].has_key(key):
            count['author'][key] += 1
        else:
            count['author'][key] = 1

        key = quotes.book
        if count['book'].has_key(key):
            count['book'][key] += 1
        else:
            count['book'][key] = 1

    for name in count['dynasty']:
        selection = Dynasty.all().filter('name =', name)
        for dynasty in selection:
            dynasty.quotes_cnt = count['dynasty'][name]
            dynasty.put()

    for name in count['category']:
        selection = Category.all().filter('name =', name)
        for category in selection:
            category.quotes_cnt = count['category'][name]
            category.put()

    for name in count['author']:
        selection = Author.all().filter('name =', name)
        for author in selection:
            author.quotes_cnt = count['author'][name]
            author.put()

    for name in count['book']:
        selection = Book.all().filter('name =', name)
        for book in selection:
            book.quotes_cnt = count['book'][name]
            book.put()

    return '更新完成！'

# function: get template values for main page
def _getTemplateValues(request):
    outData = {
        'dynasties': Dynasty.all(),
        'categories': Category.all(),
        'authors': Author.all().order('-quotes_cnt').fetch(PAGESIZE),
        'books': Book.all().order('-quotes_cnt').fetch(PAGESIZE),
    }
    outData['user'] = users.get_current_user()
    if outData['user']:
        outData['logout_url'] = users.create_logout_url(request.uri)
        outData['edit_mode'] = True
    else:
        outData['login_url'] = users.create_login_url(request.uri)
        outData['edit_mode'] = False

    selection = Quotes.all().order('-created')

    outData['dynasty'] = urllib.unquote(request.get('dynasty'))
    outData['category'] = urllib.unquote(request.get('category'))
    outData['author'] = urllib.unquote(request.get('author'))
    outData['book'] = urllib.unquote(request.get('book'))

    outData['search_author'] = urllib.unquote(request.get('search_author'))
    outData['search_book'] = urllib.unquote(request.get('search_book'))

    if outData['search_author'] != '':
        outData['author'] = outData['search_author']
        selection.filter('author =', outData['search_author'])
    elif outData['search_book'] != '':
        outData['book'] = outData['search_book']
        selection.filter('book =', outData['search_book'])
    else:
        if outData['dynasty'] != '':
            selection.filter('dynasty =', outData['dynasty'])
        if outData['category'] != '':
            selection.filter('category =', outData['category'])
        if outData['author'] != '':
            selection.filter('author =', outData['author'])
        if outData['book'] != '':
            selection.filter('book =', outData['book'])

    outData['paginator'] = _getPagenator(selection, request.get('page'))
    outData['page_url'] = re.sub('(\/page\/\d*)|([&\?]page=\d*)', '', request.uri)
    if '?' in outData['page_url']:
        outData['page_url'] += '&';
    else:
        outData['page_url'] += '?';

    return outData


#=================== CONTROLLERS ===================#
# class: index page
class MainPage(webapp.RequestHandler):
    def get(self):
        self.template_values = _getTemplateValues(self.request)
        _renderView(self, 'views/index.html')

# class: send quotes data for edit
class EditQuotes(webapp.RequestHandler):
    def get(self, key):
        try:
            outData = {
                'key': key,
                'data': Quotes.get(key)
            }
        except:
            outData = {
                'error': '无法取得数据'
            }
        _sendGqlJson(self, outData)

# class: save quotes
class SaveQuotes(webapp.RequestHandler):
    def post(self):
        key = self.request.get('key')
        if key:
            quotes = Quotes.get(key)
        else:
            quotes = Quotes()
            quotes.vote_cnt = 0

        quotes.quotes = self.request.get('quotes')
        quotes.dynasty = self.request.get('dynasty')
        quotes.category = self.request.get('category')
        quotes.author = self.request.get('author')
        quotes.book = self.request.get('book')
        quotes.user = users.get_current_user()
        quotes.put()

        _updateMstData(quotes)
        if key:
            self.redirect(self.request.referer)
        else:
            self.redirect('/')

# class: delete quotes
class DeleteQuotes(webapp.RequestHandler):
    def get(self, key):
        try:
            quotes = Quotes.get(key)
            if quotes:
                quotes.delete()
        except:
            pass
        self.redirect(self.request.referer)

# class: vote quotes
class VoteQuotes(webapp.RequestHandler):
    def post(self):
        try:
            key = self.request.get('key')
            quotes = Quotes.get(key)
            if quotes:
                quotes.vote_cnt += 1
                quotes.put()
                outData = {'vote_cnt': quotes.vote_cnt}
            else:
                outData = {'vote_cnt': 0}
        except:
            outData = {'error': '投票失败'}

        _sendJson(self, outData)

# class: send helper data
class HelperData(webapp.RequestHandler):
    def get(self, key):
        outData = _getHelperData(key)
        _sendGqlJson(self, outData)

# class: initialize Master Data
class InitApplication(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if(users.is_current_user_admin() or (user and user.email == 'ouzhiwei@gmail.com')):
            selection = Quotes.all()
            for a in selection:
                a.delete()

            selection = Dynasty.all()
            for a in selection:
                a.delete()
            for name in ['先秦', '秦', '前汉', '后汉', '三国', '西晋', '东晋', '南朝', '北朝', '隋', '唐', '五代', '北宋', '南宋', '元', '明', '清', '近代']:
                dynasty = Dynasty(name = name)
                dynasty.put()

            selection = Category.all()
            for a in selection:
                a.delete()
            for name in ['自然', '世态', '人生', '婚恋', '家庭', '社会', '政治', '经济', '学问', '修养', '伦理', '道德', '哲理', '观念', '宗教', '信仰', '文化', '艺术']:
                category = Category(name = name)
                category.put()

            selection = Author.all()
            for a in selection:
                a.delete()

            selection = Book.all()
            for a in selection:
                a.delete()

        self.redirect('/')

# class: update quotes count
class UpdateQuotesCount(webapp.RequestHandler):
    def get(self):
        result = _updateQuotesCount()
        self.response.out.write(result)

# class: export quotes in csv format
class ExportCsv(webapp.RequestHandler):
    def get(self):
        csv = '"quotes", "dynasty", "category", "author", "book", "vote_cnt"';
        for row in Quotes.all().order('created'):
            csv += '"' + row.quotes + '"'
            csv += ',"' + row.dynasty + '"'
            csv += ',"' + row.author + '"'
            csv += ',"' + row.book + '"'
            csv += ',"' + str(row.vote_cnt) + '"'
            csv += '\n'

        self.response.content_type = 'text/csv; charset=UTF-8' 
        self.response.headers['Content-Disposition'] = 'attachment; filename=' + 'quotes_' + datetime.today().strftime('%Y-%m-%d') + '.csv'
        self.response.out.write(csv)

#=================== BOOTSTRAP ===================#
application = webapp.WSGIApplication([
        (r'/edit/([\w-]+)', EditQuotes),
        (r'/save', SaveQuotes),
        (r'/vote', VoteQuotes),
        (r'/delete/([\w-]+)', DeleteQuotes),
        (r'/helper/([\w-]+)', HelperData),
        (r'/initapp', InitApplication),
        (r'/updatecount', UpdateQuotesCount),
        (r'/exportcsv', ExportCsv),
        (r'/.*', MainPage),
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()