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
        q = q.lower()
        qstr = "fullmanuscripttext_t:*%s* OR fullstandardtext_t:*%s* OR feastname_t:*%s* OR feastnameeng_t:*%s*" % (q, q, q, q)

        rows = self.get_argument("rows", "10")
        start = self.get_argument("start", "0")
        start = int(start)
        if rows == "all":
            response = solr_h.query(qstr, fields=(), rows=0)
            rows = response.numFound
        else:
            rows = int(rows)
        response = solr_h.query(qstr, score=False, highlight="*", start=start, rows=rows)
        numFound = response.numFound
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
        ret = {"numFound": numFound, "results": pages}
        self.write(json.dumps(ret))

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
        path = self.request.path.rstrip("/")
        self.render("templates/index.html", iip_server=conf.IIP_SERVER, path=path)

class DivaHandler(tornado.web.RequestHandler):
    def get(self):
        z = self.get_argument("z")
        info = diva_s.get(int(z))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(info))

class FeastHandler(tornado.web.RequestHandler):
    def get(self):
        response = solr_h.query("*:*", score=False, rows=0, facet="true", facet_field="feastname_strm")
        fields = response.facet_counts.get("facet_fields", {}).get("feastname_strm", {})
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(fields))

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
    (r"/feasts", FeastHandler),
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
