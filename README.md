Tidely
======

Source code for http://winds.leverich.org/tidely/.

Can be hosted as a standalone web app or as a WSGI application.

Setup
=====

Ubuntu
------

    git clone https://github.com/leverich/tidely.git
    cd tidely
    sudo apt-get install python-pip python-devel xtide
    sudo pip install -r requirements.txt
    python -m unittest discover

OS X
----

    git clone https://github.com/leverich/tidely.git
    cd tidely
    sudo port install xtide
    sudo pip install -r requirements.txt
    python -m unittest discover

Run as standalone service
-------------------------

    python main.py [[host:]port]

Defaults to http://0.0.0.0:8080/

Host with Apache
----------------

Add the following to /etc/apache2/sites-enabled/tidely.conf:

    <Directory /path/to/tidely>
        Order allow,deny
        Allow from all
    </Directory>
    
    <IfModule mod_wsgi.c>
        RedirectMatch ^/tidely$ /tidely/
        WSGIScriptAlias /tidely /path/to/tidely/main.py
        Alias /tidely/static /path/to/tidely/static/
        AddType text/html .py
    </IfModule>

Then reload apache:

    apache2ctl graceful
