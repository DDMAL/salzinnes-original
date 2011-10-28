#!/usr/bin/python

import sys
import solr
import csv

import conf

solr_h = solr.SolrConnection(conf.SOLR_URL)

def main():
    cantusIds = []
    salzinnes = []
    salzcsv = csv.reader(open(sys.argv[2], "rU"))
    salzhead = salzcsv.next()
    salzhead = [unicode("%s_txt" % s.lower()) for s in salzhead]
    for l in salzcsv:
        cid = l[10]
        cantusIds.append(cid)
        salzinnes.append(l)
    
    cantus = []
    cantuscsv = csv.reader(open(sys.argv[1], "rU"))
    cantushead = cantuscsv.next()
    cantushead = [unicode("%s_txt" % c.lower()) for c in cantushead]
    count = 0
    for l in cantuscsv:
        count += 1
        cid = l[5]
        if cid in cantusIds:
            cantus.append(l)
    print "total len cantus",count
    print "salzinnes",len(salzinnes)
    print "cantus",len(cantus)

    id = 1
    all_docs = []
    for s in salzinnes:
        s = [unicode(t.strip(), encoding="UTF-8") for t in s]
        doc = dict(zip(salzhead, s))
        doc["source_s"] = "salzinnes"
        doc["id"] = "%04d" % id
        id += 1
        all_docs.append(doc)

    for c in cantus:
        try:
            c = [unicode(t.strip(), encoding="UTF-8", errors="ignore") for t in c]
        except UnicodeDecodeError:
            print c
        doc = dict(zip(cantushead, c))
        doc["source_s"] = "cantus"
        doc["id"] = "%04d" % id
        id += 1
        all_docs.append(doc)

    solr_h.add_many(all_docs)
    solr_h.commit()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print >>sys.stderr, "Usage: {0} <masterchant> <cantussalzinnes>".format(sys.argv[0])
        sys.exit(1)
    main()
