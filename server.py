#!/usr/bin/python

import tornado.httpserver
import tornado.ioloop
import tornado.web

import json
import os
import solr
from operator import itemgetter

import divaserve
import conf

solr_h = solr.SolrConnection(conf.SOLR_URL)
diva_s = divaserve.DivaServe(conf.IMAGE_DIRECTORY)

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        q = self.get_argument("q")
        response = solr_h.query("fullmanuscripttext_t:%s AND fullstandardtext_t:%s" % (q, q), score=False)
        pages = []
        for d in response:
            p = {}
            for k,v in d.iteritems():
                p[k.replace("_t", "")] = v
            pages.append(p)
        pages.sort(key=itemgetter("folio"))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(pages))       

class PageHandler(tornado.web.RequestHandler):
    def get(self, pgno):
        response = solr_h.query("folio_t:%s" % pgno, score=False)
        pages = []
        for d in response:
            p = {}
            for k,v in d.iteritems():
                p[k.replace("_t", "")] = v
            pages.append(p)
        pages.sort(key=itemgetter("sequence"))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(pages))

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")

class DivaHandler(tornado.web.RequestHandler):
    def get(self):
        z = self.get_argument("z")
        info = diva_s.get(int(z))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(info))

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug": True,
    "cookie_secret": "mysecret"
}

application = tornado.web.Application([
    (r"/", RootHandler),
    (r"/divaserve/?", DivaHandler),
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
