Setup
=====

OS X:

    sudo port install py-pip
    sudo pip install -r requirements.txt
    sudo pip install pytz

Ubuntu:

    sudo apt-get install python-pip libpython-dev
    sudo pip install -r requirements.txt
    sudo pip install pytz

Apache:

    <IfModule mod_wsgi.c>
        WSGIScriptAlias /tidely/ /path/to/tidely/main.py/
        Alias /tidely/static /path/to/tidely/static/
        AddType text/html .py
    </IfModule>
