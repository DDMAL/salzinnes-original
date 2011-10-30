#!/usr/bin/python

import sys
import csv
import time
import requests

from BeautifulSoup import BeautifulSoup

"""
Scrapes http://bach.music.uwo.ca/cantus/ for chant text. Takes salziness csv 
    file as first arg and file to write to as second arg.
"""

def get_full_text(cao, incipit, siglum, location):
    """
    Gets full text of a chant from http://bach.music.uwo.ca/cantus/ given its 
        CAO number, incipit, siglum, and location.
    """
    
    # Check that cao is not an empty string
    if not cao:
        return ('', '')
        
    # Get search results for cao
    url = 'http://bach.music.uwo.ca/cantus/search.asp'
    data = {
                'searchType':'first',
                'txtIncipit':'',
                'Genre':'All',
                'allOrMasters':'all',
                'txtCAO': cao,
                'submitType':'search',
            }
    r = requests.post(url, data=data)
    
    # Parse request content
    try:
        soup = BeautifulSoup(r.content)
        table = soup.findAll('table')[0]
    except (AttributeError, IndexError):
        return ('', '')
    
    # Find links to correct chant according to incipit and siglum
    rows = [row for row in table.findChildren() if len(row.findChildren())==6]
    links = []
    for row in rows:
        cols = row.findChildren()
        this_incipit = cols[4].text
        this_siglum = cols[5].text
        if this_incipit==incipit.strip() and this_siglum==siglum:
            rel = row.find('a')['href']
            if rel:
                link = '%s%s' % ("http://bach.music.uwo.ca/cantus/", rel)
                links.append(link)
            
    # Follow links to find the right one by checking location
    for link in links:
        r = requests.get(link)
        soup = BeautifulSoup(r.content)
        try:
            table = soup.findAll('table')[0]
        except IndexError:
            return ('', '')
        this_location = table.find(text='Location').findParent().findNextSibling().text
        full_manuscript_text = table.find(text='Full Manuscript Text').findParent().findNextSibling().text
        full_standard_text = table.find(text='Standard Full Text').findParent().findNextSibling().text      
        if this_location==location:
            return (full_manuscript_text, full_standard_text)
    return ('', '')
                
def main():
    # Get file path of output for error log
    filepath = sys.argv[2].split('/')
    filepath = '/'.join(filepath[:-1]) + '/salzscrape_error_log.txt'
    errorlog = open(filepath, 'wb')
    salzreader = csv.reader(open(sys.argv[1], 'rU'))
    salzwriter = csv.writer(open(sys.argv[2], 'wb'), quoting=csv.QUOTE_ALL)
    salzwriter.writerow(salzreader.next()+['FullManuscriptText', 'FullStandardText'])
    
    for (i, l) in enumerate(salzreader):
        cao = l[9]
        incipit = l[7] 
        siglum = l[15]
        location = '%s %s' % (l[1], l[2])
        full_manuscript_text, full_standard_text = get_full_text(cao, incipit, siglum, location)
        if not full_manuscript_text:
            errorlog.write('Could not retrieve full manuscript text from cao %s.\n' % cao)
        if not full_standard_text:
            errorlog.write('Could not retrieve full standard text from cao %s.\n' % cao)
        salzwriter.writerow(l+[full_manuscript_text, full_standard_text])
        
        # Print progress
        if i%10==0:
            now = time.localtime()
            print '%s completed at time %s:%s:%s' % (i, now.tm_hour, now.tm_min, now.tm_sec)

if __name__=='__main__':
    if len(sys.argv) < 3:
        print >>sys.stderr, "Usage: {0} <cantussalzinnes> <csvout>".format(sys.argv[0])
        sys.exit(1)
    main()
