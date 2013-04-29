#encoding:utf-8
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)


class Auth(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = self.request.cookies.get('visits', 0)
        if visits.isdigit():
            visits = int(visits) + 1
        else:
            visits = 0

        self.response.headers.add_header('Set-Cookie', 'visits=%d' % visits)
        if visits > 100:
            self.write("You are the best ever!")
        else:
            self.write("You've been here %d times!" % visits)

app = webapp2.WSGIApplication([('/unit4/auth', Auth)],
                              debug=True)
