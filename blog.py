#encoding:utf-8
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(**kw)

    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class Article(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(BaseHandler):
    def get(self):
        articles = db.GqlQuery("select * from Article order by created desc")
        self.render("blog-front.html", articles=articles)

class NewPage(BaseHandler):
    def render_front(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_front()
    
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get('content')
        if subject and content:
            a = Article(subject = subject, content = content)
            a.put()

            self.redirect("/unit3/blog/%d" % a.key().id())
        else:
            error = "We need both a subject and some content!"
            self.render_front(subject=subject, content=content, error=error)

class ArticlePage(BaseHandler):
    def get(self, article_id):
        article = Article.get_by_id(int(article_id))
        self.render("article.html", article=article)
            
app = webapp2.WSGIApplication([
    (r'/unit3/blog', MainPage),
    (r'/unit3/blog/newpost', NewPage),
    (r'/unit3/blog/(\d+)', ArticlePage)],
                              debug=True)
