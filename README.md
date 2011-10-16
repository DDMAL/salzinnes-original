Salzinnes
---------

Requirements:

* tornado (easy_install tornado)
* vips (http://www.vips.ecs.soton.ac.uk/index.php?title=VIPS)
* solr (included)
* java

To run:

Set up configuration:

    $ cp conf.py{.dist,}
    .. edit conf.py

Start up the solr server:

    $ cd db; java -jar start.jar

If you haven't imported the data, do that:

    $ python csvtosolr.py tblMasterChants.csv CANTUS-salzinnes.csv

Start the server:

    $ python server.py [port]

Test:

* http://localhost:8080/page/048r
* http://localhost:8080/search?q=adorare
