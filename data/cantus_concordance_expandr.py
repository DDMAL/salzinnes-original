# -*- coding: utf-8 -*-

import sys
import os
import couchdb
from optparse import OptionParser
import csv
import logging
import cStringIO
import codecs

logging.basicConfig(filename='errors.log', format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
lg = logging.getLogger('cantus')
lg.setLevel(logging.DEBUG)

def UnicodeDictReader(str_data, encoding, **kwargs):
    csv_reader = csv.DictReader(str_data, **kwargs)
    # Decode the keys once
    keymap = dict((k, k.decode(encoding)) for k in csv_reader.fieldnames)
    for row in csv_reader:
        yield dict((keymap[k], v.decode(encoding)) for k, v in row.iteritems())

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

if __name__ == "__main__":
    opts = OptionParser()
    (options, args) = opts.parse_args()

    csvfile = UnicodeDictReader(open('salzinnes_with_full_text.csv', 'rU'), 'iso-8859-1')

    csvoutfile = UnicodeWriter(open('salzinnes_concordance_expanded.csv', 'wb'))
    k = None

    for record in csvfile:
        if not k:
            k = True
            csvoutfile.writerow(record.keys())
        # print record['Concordances']
        r = record["Concordances"]
        output_string = []
        if "C" in r:
            output_string.append(u"Paris: Bibliothèque nationale de France (F-Pn lat. 17436)")
        if "G" in r:
            output_string.append(u"Durham: Cathedral Library (GB-DRc B. III. 11)")
        if "B" in r:
            output_string.append(u"Bamberg: Staatsbibliothek (D-BAs lit. 23)")
        if "E" in r:
            output_string.append(u"Ivrea: Biblioteca Capitolare (I-IV 106)")
        if "M" in r:
            output_string.append(u"Monza: Basilica di S. Giovanni Battista-Biblioteca Capitolare e Tesoro (I-MZ C. 12/75)")
        if "V" in r:
            output_string.append(u"Verona: Biblioteca Capitolare (I-VEcap XCVIII)")
        if "H" in r:
            output_string.append(u"Sankt Gallen: Stiftsbibliothek (CH-SGs 390-391)")
        if "R" in r:
            output_string.append(u"Zürich: Zentralbibliothek (CH-Zz Rh. 28)")
        if "D" in r:
            output_string.append(u"Paris: Bibliothèque nationale de France (F-Pn lat. 17296)")
        if "F" in r:
            output_string.append(u"Paris: Bibliothèque nationale de France (F-Pn lat. 12584)")
        if "S" in r:
            output_string.append(u"London: The British Library (GB-Lbl add. 30850)")
        if "L" in r:
            output_string.append(u"Benevento: Biblioteca Capitolare (I-BV V. 21)")
        
        record['Concordances'] = ", ".join(output_string)
        print record

        recordout = [unicode(s) for s in record.values()]

        csvoutfile.writerow(recordout)
