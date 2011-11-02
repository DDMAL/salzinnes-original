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

        c = doc['concordances_t']

        if c:
            doc['concordances_strm'] = c.split(", ")
        
        del doc['concordances_t']
        
        office = doc['office_t']
        if office:
            doc['office_strm'] = office
        
        del doc['office_t']
        
        mode = doc['mode_t']
        if mode:
            doc['mode_strm'] = mode
        
        del doc['mode_t']
        
        genre = doc['genre_t']
        if genre:
            doc['genre_strm'] = genre
        
        del doc['genre_t']
        
        position = doc['position_t']

        if position:
            doc['position_stored'] = position
        
        del doc['position_t']

        feastname_eng = doc['feastnameeng_t']
        if feastname_eng:
            doc['feastnameeng_strm'] = feastname_eng
        
        del doc['feastnameeng_t']


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
