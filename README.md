Setup
=====

OS X:

    sudo port install py-pip
    sudo pip install -r requirements.txt

Ubuntu:

    sudo apt-get install python-pip
    sudo pip install -r requirements.txt

Apache:

    <IfModule mod_wsgi.c>
        WSGIScriptAlias /tidely /path/to/tidely/main.py
        Alias /tidely/static /path/to/tidely/static/
        AddType text/html .py
    </IfModule>
