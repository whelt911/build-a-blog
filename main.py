#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)


def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class Entry(db.Model):
	title = db.StringProperty(required = True)
	body = db.TextProperty(required = True)
	created = db. DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
	def render_front(self, title="", body="",error=""):
		#pull last 5 entries from database
		entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created desc limit 5")

		self.render("blog.html", Entry = entries)


	def get(self):
		self.render_front()

	def post(self):
		self.redirect("/add")



class Add(Handler):
	#contains fields to add new blog entry
	def get(self):
		self.render("add.html")

	def post(self):
		title = self.request.get("title")
		body = self.request.get("body")

		if title and body:
			a = Entry(parent = blog_key(), title = title, body = body)
			a.put()
			self.redirect('/blog/%s' % str(a.key().id()))
		else:
			error = "Please enter a title and content!"
			self.render_front(title, body, error)



class Add_confirm(Handler):
	def get(self):
		key = db.Key.from_path('Entry', int(post_id), parent=blog_key())
		post = db.get(key)
		self.render("add_confirm.html", post = post)

class ViewPostHandler(webapp2.RequestHandler):
	def render_entry(self, id, title="",body="",error=""):
		single_entry = Entry.get_by_id(int(id),parent=None)
		self.render("add_confirm.html", title=title, body=body, error=error, single_entry=single_entry)

	def get(self, id):
		self.render_entry(id)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
	('/add', Add),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
