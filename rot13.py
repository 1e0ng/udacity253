#encoding:utf-8
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class Rot13(BaseHandler):
    def get(self):
        self.render('rot13-form.html')

    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            for c in text:
                if ord(c) >= ord('a') and ord(c) <= ord('z'):
                    rot13 += chr((ord(c) - ord('a') + 13) % 26 + ord('a'))
                elif ord(c) >= ord('A') and ord(c) <= ord('Z'):
                    rot13 += chr((ord(c) - ord('A') + 13) % 26 + ord('A'))
                else:
                    rot13 += c

        self.render('rot13-form.html', text=rot13)


            
app = webapp2.WSGIApplication([('/unit2/rot13', Rot13)],
                              debug=True)
