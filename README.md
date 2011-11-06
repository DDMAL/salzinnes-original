Salzinnes
---------

Requirements:

* tornado
* vips (http://www.vips.ecs.soton.ac.uk/index.php?title=VIPS)
  * PIL will be used if vips can't be found
* IIPImage (http://iipimage.sourceforge.net/)
* fcgi server for IIP (nginx is good)
* solr (included)
* java

To run:

Set up configuration:

    $ cp conf.py{.dist,}
    .. edit conf.py

Start up the solr server:

    $ cd db; java -jar start.jar

If you haven't imported the data, do that:

    $ python csvtosolr.py data/salzinnes_concordance_expanded.csv

Start the server:

    $ python server.py [port]

Test:

* http://localhost:8080/page/048r
* http://localhost:8080/search?q=adorare

To delete the solr database:

    python
    import conf, solr
    s = solr.SolrConnection(conf.SOLR_URL)
    s.delete_query("*:*")
    s.commit()

Linux installation:

    apt-get install solr-jetty supervisor python-vipscc openjdk-6-jdk python-pip
    pip install tornado

or on newer ubuntu, ```apt-get install python-tornado```

Setting up startup scripts on Mac (edit these files to change the paths):

    mkdir -p ~/Library/LaunchAgents
    cp ca.mcgill.music.ddmal.solr.plist ~/Library/LaunchAgents/
    cp ca.mcgill.music.ddmal.tornado.plist ~/Library/LaunchAgents/
    launchctl load -w ~/Library/LaunchAgents/ca.mcgill.music.ddmal.solr.plist
    launchctl load -w ~/Library/LaunchAgents/ca.mcgill.music.ddmal.tornado.plist

To stop loading:

    launchctl unload -w ~/Library/LaunchAgents/ca.mcgill.music.ddmal.solr.plist

Other things on Mac:

nginx brew install nginx. copy startup script
IIP brew install spawn-fcgi, startup script
Download & install IIP
Copy nginx config
