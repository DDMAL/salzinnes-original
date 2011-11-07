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

# If we wanted to sort by score, we could try a query like this (boosts results where
#  the word only occurs in 1 of the texts)
# (fullmanuscripttext_t:accipe AND fullstandardtext_t:accipe) OR
#  (-fullmanuscripttext_t:accipe AND fullstandardtext_t:accipe^2) OR
#  (fullmanuscripttext_t:accipe^2 AND -fullstandardtext_t:accipe)
class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        q = self.get_argument("q")
        response = solr_h.query("fullmanuscripttext_t:*%s* OR fullstandardtext_t:*%s* OR feastname_t:*%s* OR feastnameeng_strm:*%s*" % (q, q, q, q), score=False, highlight="*")
        pages = []
        for d in response:
            p = {}
            for k,v in d.iteritems():
                p[k.replace("_t", "")] = v
            hl=response.highlighting[p["id"]]
            p["hl"]={}
            for k,v in hl.iteritems():
                p["hl"][k.replace("_t", "")] = v
            pages.append(p)
        pages.sort(key=lambda d: (d["folio"], d["sequence"]))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(pages))       

class PageHandler(tornado.web.RequestHandler):
    def get(self, pgno):
        q = self.get_argument("q", None)
        if q:
            query = "folio_t:%s OR (folio_t:%s AND (fullmanuscripttext_t:%s OR fullstandardtext_t:%s))" % (pgno, pgno, q, q)
        else:
            query = "folio_t:%s" % pgno
        response = solr_h.query(query, score=False, highlight="*")
        pages = []
        for d in response:
            p = {}
            for k,v in d.iteritems():
                p[k.replace("_t", "")] = v
            hl=response.highlighting.get(p["id"], {})
            p["hl"]={}
            for k,v in hl.iteritems():
                p["hl"][k.replace("_t", "")] = v
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
