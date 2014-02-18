Setup
=====

Ubuntu:

    git clone https://github.com/leverich/tidely.git
    cd tidely
    sudo apt-get install python-pip libpython-dev xtide
    sudo pip install -r requirements.txt
    sudo pip install pytz
    python -m unittest discover

OS X:

    git clone https://github.com/leverich/tidely.git
    cd tidely
    sudo port install py-pip
    sudo port install xtide
    sudo pip install -r requirements.txt
    sudo pip install pytz
    python -m unittest discover

Run as standalone service on port 8080:

    python main.py

Host with Apache:

    Add the following to /etc/apache2/sites-enabled/tidely.conf:

      <IfModule mod_wsgi.c>
          WSGIScriptAlias /tidely/ /path/to/tidely/main.py/
          Alias /tidely/static /path/to/tidely/static/
          AddType text/html .py
      </IfModule>

    Reload apache:

      apache2ctl graceful
