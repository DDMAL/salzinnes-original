#!/usr/bin/python

import tornado.httpserver
import tornado.ioloop
import tornado.web

import json
import uuid
import os

sessions = {}

class SearchHandler(tornado.web.RequestHandler):
    def post(self):
        pass

    def get(self):
        pass

class PageHandler(tornado.web.RequestHandler):
    def post(self):
        pass

    def get(self):
        pass

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug": True,
    "cookie_secret": "mysecret"
}

application = tornado.web.Application([
    (r"/", RootHandler),
    (r"/search", SearchHandler),
    (r"/page/(.*)", PageHandler),
    ], **settings)

def main(port):
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
    main(port)
