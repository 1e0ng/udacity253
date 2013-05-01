#encoding:utf-8
import os
import random
import hmac
import string

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty(required=False)

def make_uid_str(uid, password, salt='hVseqI'):
    if salt is None:
        salt = ''.join([random.choice(string.letters) for _ in xrange(5)])
    salt = str(salt)
    #return '%s|%s|%s' % (uid, hmac.new(salt, str(uid)+password).hexdigest(), salt)
    return '%s|%s' % (uid, hmac.new(salt, str(uid)+password).hexdigest())

class Signup(BaseHandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        if not username:
            self.render('signup.html', username_error='Username is required.',
                    username=username, email=email)
            return
        if not password:
            self.render('signup.html', password_error='Password is required.',
                    username=username, email=email)
            return
        if password != verify:
            self.render('signup.html', verify_error='Your passwords do not'
                    ' match', username=username, email=email)
            return

        if db.GqlQuery('select * from User where username=:username',
                username=username).get():
            self.render('signup.html', username_error='The user already'
                    ' exists.', username=username, email=email)
            return
        user = User(username=username, password=password, email=email)
        user.put()

        uid_str = make_uid_str(user.key().id(), user.password)
        self.response.headers.add_header('Set-Cookie', 'user_id=%s' % uid_str)
        self.redirect('/unit4/welcome')
        

class Welcome(BaseHandler):
    def check_uid(self, uid_str):
        strs = uid_str.split('|')
        if len(strs) != 2:
            return False
        uid, hmac = strs
        user = User.get_by_id(int(uid))
        if not user:
            return False
        if make_uid_str(uid, user.password) == uid_str:
            return user

    def get(self):
        uid_str = self.request.cookies.get('user_id')
        user = self.check_uid(uid_str)
        if not user:
            self.redirect('/unit4/signup')
            return
 
        self.write('Welcome, ' + user.username)

app = webapp2.WSGIApplication([
    ('/unit4/signup', Signup),
    ('/unit4/welcome', Welcome),
    ],
    debug=True)
