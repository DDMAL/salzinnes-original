#!/usr/bin/python

import sys
import solr
import csv

import conf

solr_h = solr.SolrConnection(conf.SOLR_URL)

def main():
    salzinnes = []
    salzcsv = csv.reader(open(sys.argv[1], "rU"))
    salzhead = salzcsv.next()
    salzhead = [unicode("%s_t" % s.lower()) for s in salzhead]
    for l in salzcsv:
        salzinnes.append(l)

    id = 1
    all_docs = []
    for s in salzinnes:
        s = [unicode(t.strip(), encoding="UTF-8") for t in s]
        doc = dict(zip(salzhead, s))
        doc["id"] = "%04d" % id
        id += 1
        all_docs.append(doc)

    solr_h.add_many(all_docs)
    solr_h.commit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: {0} <cantussalzinnes>".format(sys.argv[0])
        sys.exit(1)
    main()
