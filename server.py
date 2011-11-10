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

        if q.startswith("cao") or q.startswith("can") or q.startswith("slz"):
            q = "caonumber_t:%s" % q
        rows = self.get_argument("rows", "10")
        start = self.get_argument("start", "0")
        start = int(start)
        hl="fullmanuscripttext_t,fullstandardtext_t,feastnameeng_t,feastname_t,office_t,mode_t,genre_t,caonumber_t"
        qf = hl.replace(",", " ")
        if rows == "all":
            response = solr_h.query(q, qf=qf, fields=(), rows=0)
            rows = response.numFound
        else:
            rows = int(rows)
        response = solr_h.query(q, qf=qf, score=False, highlight=hl, start=start, rows=rows, sort="folio_t asc,sequence_t asc")
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
        pages.sort(key=lambda d: (d["folio"], int(d["sequence"])))
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
        response = solr_h.query(query, score=False, highlight="*", rows=20, sort="sequence_t asc")
        # Do 1 query and hope we get them all. If not, do another one
        if response.numFound > 20:
            response = solr_h.query(query, score=False, highlight="*", rows=response.numFound)
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
        pages.sort(key=lambda d: int(d["sequence"]))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(pages))

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        app_root = conf.APP_ROOT.rstrip("/")
        self.render("templates/index.html", app_root=app_root, iip_server=conf.IIP_SERVER)

class DivaHandler(tornado.web.RequestHandler):
    def get(self):
        z = self.get_argument("z")
        info = diva_s.get(int(z))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(info))

class FeastHandler(tornado.web.RequestHandler):
    def get(self):
        response = solr_h.query("*:*", score=False, rows=0, facet="true", facet_field="feastnameeng_s")
        fields = response.facet_counts.get("facet_fields", {}).get("feastnameeng_s", {})
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(fields))

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "debug": True,
    "cookie_secret": "mysecret"
}

def abs_path(relpath):
    root = conf.APP_ROOT.rstrip("/")
    return r"%s%s" % (root, relpath)

application = tornado.web.Application([
    (abs_path(r"/?"), RootHandler),
    (abs_path(r"/divaserve/?"), DivaHandler),
    (abs_path(r"/search"), SearchHandler),
    (abs_path(r"/page/(.*)"), PageHandler),
    (abs_path(r"/feasts"), FeastHandler),
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
