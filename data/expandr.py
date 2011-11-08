# -*- coding: utf-8 -*-

import sys
import os
from optparse import OptionParser
import csv
import logging
import cStringIO
import codecs

logging.basicConfig(filename='errors.log', format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
lg = logging.getLogger('cantus')
lg.setLevel(logging.DEBUG)

def ordinal(value):
    """
    Converts zero or a *postive* integer (or their string 
    representations) to an ordinal value.

    >>> for i in range(1,13):
    ...     ordinal(i)
    ...     
    u'1st'
    u'2nd'
    u'3rd'
    u'4th'
    u'5th'
    u'6th'
    u'7th'
    u'8th'
    u'9th'
    u'10th'
    u'11th'
    u'12th'

    >>> for i in (100, '111', '112',1011):
    ...     ordinal(i)
    ...     
    u'100th'
    u'111th'
    u'112th'
    u'1011th'

    """
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval


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

    feastfile = UnicodeDictReader(open('feasts.csv', 'rU'), 'UTF-8')

    # def feastcodelookup(feastcode):
    #     lg.debug("Feastcode: {0}".format(feastcode))
    #     # f = [r for r in feastfile if r['FeastCode'] == feastcode]
    #     for record in feastfile:
    #         if not record["FeastCode"]:
    #             continue
    #         lg.debug(record["FeastCode"])
    #         if len(record["FeastCode"]) == 7:
    #             record["FeastCode"] = "0{0}".format(record["FeastCode"])
    #         lg.debug("Output: {0}".format(record['FeastCode']))

    #         if str(record["FeastCode"]) == str(feastcode):
    #             return record["EnglishName"]
    #     return None

    feasts = {}
    for feast in feastfile:
        if len(feast['FeastCode']) == 7:
            feast['FeastCode'] = u"0{0}".format(feast['FeastCode'])
        feasts[feast['FeastCode']] = feast["EnglishName"]
    
    lg.debug(feasts)

    csvoutfile = UnicodeWriter(open('salzinnes_concordance_expanded.csv', 'wb'))
    k = None

    for record in csvfile:

        if not k:
            # add extra fields:
            record['FeastNameEng'] = None
            k = True
            csvoutfile.writerow(record.keys())
        # print record['Concordances']

        fea = unicode(record["FeastCode"])
        if len(fea) == 7:
            fea = u"0{0}".format(fea)

        
        if fea in feasts.keys():
            record["FeastNameEng"] = feasts[fea]
            print "Found {0}".format(feasts[fea])
        else:
            record["FeastNameEng"] = ""

        r = record["Concordances"]
        output_string = []
        if "C" in r:
            output_string.append(u"F-Pn lat. 17436 (Paris-Bibliothèque nationale de France)")
        if "G" in r:
            output_string.append(u"GB-DRc B. III. 11 (Durham: Cathedral Library)")
        if "B" in r:
            output_string.append(u"D-BAs lit. 23 (Bamberg: Staatsbibliothek)")
        if "E" in r:
            output_string.append(u"I-IV 106 (Ivrea: Biblioteca Capitolare)")
        if "M" in r:
            output_string.append(u"I-MZ C. 12/75 (Monza: Basilica di S. Giovanni Battista-Biblioteca Capitolare e Tesoro)")
        if "V" in r:
            output_string.append(u"I-VEcap XCVIII (Verona: Biblioteca Capitolare)")
        if "H" in r:
            output_string.append(u"CH-SGs 390-391 (Sankt Gallen: Stiftsbibliothek)")
        if "R" in r:
            output_string.append(u"CH-Zz Rh. 28 (Zürich: Zentralbibliothek)")
        if "D" in r:
            output_string.append(u"F-Pn lat. 17296 (Paris: Bibliothèque nationale de France)")
        if "F" in r:
            output_string.append(u"F-Pn lat. 12584 (Paris: Bibliothèque nationale de France)")
        if "S" in r:
            output_string.append(u"GB-Lbl add. 30850 (London: The British Library)")
        if "L" in r:
            output_string.append(u"I-BV V. 21 (Benevento: Biblioteca Capitolare)")
        
        record['Concordances'] = ", ".join(output_string)

        genres = {"A":"Antiphon",
            "AV": "Antiphon Verse",
            "R": "Responsory",
            "V": "Responsory Verse",
            "W": "Versicle",
            "H": "Hymn",
            "I": "Invitatory antiphon",
            "P": "Invitatory Psalm",
            "M": "Miscellaneous",
            "G": "Mass chants"
        }

        if record['Genre']:
            record['Genre'] = genres[record['Genre']]

        office = {
            "V": "First Vespers",
            "C": "Compline",
            "M": "Matins",
            "L": "Lauds",
            "P": "Prime",
            "T": "Terce",
            "S": "Sext",
            "N": "None",
            "V2": "Second Vespers",
            "D": "Day Hours",
            "R": "Memorial",
            "E": "Antiphons for the Magnificat or Benedictus",
            "H": "Antiphons based on texts from the Historia",
            "CA": "Chapter",
            "X": "Supplementary"
        }

        if record['Office']:
            record["Office"] = office[record["Office"]]

        pos = record["Position"].strip()
        off = record["Office"]
        gen = record["Genre"]

        if pos.isdigit():
            if gen == "Hymn" or gen == "Responsory Verse":
                tmpstr = "Hymn Verse" if gen == "Hymn" else "Verse"
                record["Position"] = "{0} {1}".format(tmpstr, pos.lstrip("0"))
            elif gen == "Versicle":
                record["Position"] = "{0} {1}".format(ordinal(int(pos)), gen)
            elif off in ("Lauds", "First Vespers", "Second Vespers", "Terce") and gen != "Hymn":
                record["Position"] = "{0} for the {1} Psalm".format("Antiphon", ordinal(int(pos)))
            elif off == "Matins" and gen in ("Responsory", "Antiphon"):
                tmpstr = "Lessons" if gen == "Responsory" else "Psalms"
                record["Position"] = "{0} for all {1} of Nocturn {2}".format(pos.lstrip("0"), tmpstr, pos)
            elif off == "Matins" and gen == "Antiphon Verse":
                record["Position"] = "{0} {1}".format(gen, pos.lstrip("0"))
        else:
            if pos == "p":
                record["Position"] = "Antiphon for all Psalms/Canticles"
            elif "." in pos:
                if len(pos) == 3:
                    noc, les = pos.split(".")
                    tmpstr = "Psalm" if gen == "Antiphon" else "Lesson"
                    record["Position"] = "{0} for Nocturn {1}, {2} {3}".format(gen, noc, tmpstr, les)
                else:
                    noc, nul = pos.split(".")
                    record["Position"] = "Antiphon for all Psalms of Nocturn {0}".format(noc)
            elif pos == "M":
                record["Position"] = "Antiphon for the Magnificat"
            elif pos == "B":
                record["Position"] = "Antiphon for the Benedictus"
            elif pos == "N":
                record["Position"] = "Antiphon for the Nunc Dimittis"
            elif pos == "R":
                record["Position"] = "Antiphon sung as a memorial"
            elif len(pos) == 2:
                if pos[1] == "B":
                    record["Position"] = "{0} Antiphon for the Benedictus".format(ordinal(int(pos[0])))
                elif pos[1] == "M":
                    record["Position"] = "{0} Antiphon for the Magnificat".format(ordinal(int(pos[0])))


        # mode = {
        #     "1": "First mode",
        #     "2": "Second mode",
        #     "3": "Third mode",
        #     "4": "Fourth mode",
        #     "5": "Fifth mode",
        #     "6": "Sixth mode",
        #     "7": "Seventh mode",
        #     "8": "Eighth mode",
        #     "*": "No music",
        #     "r": "Responsory (Simple)",
        #     "?": "Uncertain",
        #     "S": "Responsory (Special)",
        #     "T": "Chant in Transposition"
        # }

        # record["Mode"] = mod[record["Mode"]]
        m = list(record["Mode"])
        mode_output = []
        if "1" in m:
            mode_output.append("Mode 1")
        if "2" in m:
            mode_output.append("Mode 2")
        if "3" in m:
            mode_output.append("Mode 3")
        if "4" in m:
            mode_output.append("Mode 4")
        if "5" in m:
            mode_output.append("Mode 5")
        if "6" in m:
            mode_output.append("Mode 6")
        if "7" in m:
            mode_output.append("Mode 7")
        if "8" in m:
            mode_output.append("Mode 8")
        
        if "*" in m:
            mode_output.append("No music")
        if "r" in m:
            mode_output.append("Responsory (simple)")
        if "?" in m:
            mode_output.append("Uncertain")
        if "S" in m:
            mode_output.append("Responsory (special)")
        if "T" in m:
            mode_output.append("in Transposition")
        
        if mode_output:
            outstring = " ".join(mode_output)
            record['Mode'] = outstring
        



        recordout = [unicode(s) for s in record.values()]

        csvoutfile.writerow(recordout)
