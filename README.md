What is this?
=============

A project of loosely coupled applications that force aspects of the political process to give each other a clean handshake ... with gloves on.

But seriously...


Table of Contents
=================

* [Assumptions](#assumptions)
* [Quickstart](#quickstart-to-get-up-and-running)
* [Config and Settings](#config-and-settings)
* ~~[How We Process And Update Data Each Month](#how-we-process-and-update-data-each-month)~~
* ~~[How We Build The Project Each Month](#how-we-build-the-project-each-month)~~
* ~~[How We Deploy The Project Each Month](#how-we-deploy-the-project-each-month)~~
* ~~[Available Fabric Commands](#available-fabric-commands)~~
* ~~[Building a Mac OS Python dev environment](#building-a-mac-os-python-dev-environment)~~


Assumptions
===========

* You are running OSX.
* You are using Python 2.x
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.
* You have MySQL installed

If any of these are not true, please skip ahead to [Building a Mac OS Python dev environment](#building-a-mac-os-python-dev-environment)


Quickstart To Get Up And Running
================================

* Clone this repo to wherever it is on your machine that you work on your projects

        git clone git@github.com:SCPR/kpcc_backroom_handshakes.git

* Change into that directory

        cd kpcc_backroom_handshakes

* Create your virtualenv and install the project/application requirements using pip

        mkvirtualenv kpcc_backroom_handshakes
        pip install -r requirements.txt

* Make a copy of ```TEMPLATE_development.yml``` and rename it to ```development.yml```

        cp TEMPLATE_development.yml development.yml

* Run ```fab makesecret``` and add the output on line 5 of ```development.yml```

        secret_key: "1=5avBguTW ... "

* Assuming MySQL is installed in ```development.yml``` add username and password for your MySQL install.

        database:
          host: "127.0.0.1"
          port: 3306
          database: "kpcc_backroom_handshakes"
          username: "root"
          password: ""

* Assuming you have virtualenv and pip installed run ```fab bootstrap```

    * This single fabric command uses several functions to scaffold the project by:
        * Creating the database: ```fab create_db```
        * Applying initial Django migrations: ```fab migrate```
        * Load initial data fixtures: ```fab load_fixtures```
        * Creating the Django superuser: ```python manage.py createsuperuser```
        * Running the Django development server: ```fab run```

* Navigate to ```http://127.0.0.1:8000/``` and you should arrive at the homepage that shows the elections we have processed using the application so far.


Config and Settings
===================

Still very much learning how to configure a collaborative project in different environments, I feel this is a good start to a path that allows for experimentation among collaborators without having to keep too many settings files in sync. Of course, like with all things, we'll learn something new that makes all of this seem silly.

**The Files**

* ```settings_common.py``` contains middlware classes and installed apps common to the project.

* ```settings_production.py``` contains references to Installed Apps, API, database and other configuration variables. ```config.yml``` holds configuration variables used in production. ```development.yml``` holds configuration variables used in development.

* ```config.yml``` contains installed apps, API, database and other configuration variables for production

* ```development.yml``` contains installed apps, API, database and other configuration variables for development

* ```TEMPLATE_development.yml``` is the template for either ```config.yml``` or ```development.yml``` configuration variables.

**The Variables**

* ```debug```: Default is ```True```. Set to ```False``` when in a production environment. Is echoed and used in variables contained in ```settings_common.py```.

* ```secret_key```: Default is ```""```. Use ```fab makesecret``` to create value to plug in here. Is used to provide cryptographic signing, and should be set to a unique, unpredictable value. Django will refuse to start if is not set.

* ```internal_ips```: Default is an empty list. [Stands for a list of IP addresses](https://docs.djangoproject.com/en/dev/ref/settings/#internal-ips), as strings, that:
    * Allow the debug() context processor to add some variables to the template context.
    * Can use the admindocs bookmarklets even if not logged in as a staff user.
    * Are marked as "internal" (as opposed to "EXTERNAL") in AdminEmailHandler emails.

* ```site_url```: Default is ```""```.

* ```database```: [A dictionary containing the settings for all databases to be used with Django](https://docs.djangoproject.com/en/dev/ref/settings/#databases). It is a nested dictionary whose contents map a database alias to a dictionary containing the options for an individual database. Default engine is mysql.
    - ```host```: Default is ```""```. Which host to use when connecting to the database. An empty string means localhost. Not used with SQLite.
    - ```port```: Default is ```""```. The port to use when connecting to the database. An empty string means the default port. Not used with SQLite.
    - ```database```: Default is ```""```. The name of the database to use. For SQLite, it’s the full path to the database file.
    - ```username```: Default is ```""```. The username to use when connecting to the database. Not used with SQLite.
    - ```password```: Default is ```""```. The password to use when connecting to the database. Not used with SQLite.

* ```email```: optional if you intend to generate emails from an application
    - ```host```: Default is ```localhost```. The host to use for sending email.
    - ```user```: Default is ```""```. Username to use for the SMTP server defined in EMAIL_HOST. If empty, Django won’t attempt authentication.
    - ```password```: Default is ```""```. Password to use for the SMTP server defined in ```EMAIL_HOST```. This setting is used in conjunction with ```EMAIL_HOST_USER``` when authenticating to the SMTP server. If either of these settings is empty, Django won’t attempt authentication.
    - ```port```: Default is ```25```. Port to use for the SMTP server defined in EMAIL_HOST.
    - ```use_tls```: Default is ```True```. Whether to use a TLS (secure) connection when talking to the SMTP server. This is used for explicit TLS connections, generally on port 587.

* ```installed_apps```:
    - ```massadmin```:
    - ```slacker_log_handler```:
    - ```bakery```:
    - ```election_registrar```:
    - ```ballot_box```:
    - ```newscast```:
    - ```measure_finance```:

* ```deployment_env```:
    - ```hosts```:
    - ```project_name```:
    - ```local_branch```:
    - ```remote_ref```:
    - ```requirements_file```:
    - ```use_ssh_config```:
    - ```code_dir```:

* ```build```: django-bakery & deployment
    - ```aws_bucket_name```: Default is ```""```.
    - ```aws_access_key_id```: Default is ```""```.
    - ```aws_secret_access_key```: Default is ```""```.
    - ```aws_s3_host```: "s3-accelerate.amazonaws.com"
    - ```bakery_gzip```: True
    - ```staging```: False
    - ```staging_prefix```: Default is ```None```.
    - ```live_prefix```: Default is ```None```.
    - ```deploy_dir```: Default is ```None```.
    - ```build_dir```: Default is ```""```.
    - ```views```:
        - "election_registrar.views.ElectionDetailView"
        - "ballot_box.views.BakedHomepageIndex"
        - "ballot_box.views.BakedFeaturedIndex"
        - "ballot_box.views.BakedResultsIndex"
        - "ballot_box.views.BakedEmbeddedDetail"
        - "measure_finance.views.InitialDetailView"
    - ```bakery_cache_control```:
        - ```html```: 300
        - ```javascript```: 86400
    - ```static_to_ignore```: Default are "admin", "bootstrap", "bootstrap-rtl", "yaml"













* ```api```: api settings and keys for applications housed in the project.
    * ```slack```: Used for the [slacker_log_handler](https://github.com/mathiasose/slacker_log_handler) module that posts data from project jobs to a specific channel in KPCC's Slack account.
        - ```token```: Default is ```""```. KPCC's token is documented elsewhere.
        - ```api_key```: Default is ```""```. KPCC's api key is documented elsewhere.
    * ```propublica```: Optional api key is using [propublica's data api](https://propublica.github.io/congress-api-docs/)
        - ```api_key```: Default is ```""```.
    * ```maplight```:  Optional api key is using [maplight's data api](http://maplight.org/us-congress/guide/tools/apis-and-widgets)
        - ```api_key```: Default is ```""```. KPCC's api key from the 2016 election cycle is documented elsewhere.
    * ```headers```: HTTP headers [added to a request](http://docs.python-requests.org/en/master/user/quickstart/#custom-headers)
        - ```from```: String that is passed through URL requests made using the Requests library.
        - ```user_agent```: String that is passed through URL requests made using the Requests library. Default is "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19"



----






















Available Fabric Commands
=========================

**Data Functions**

* Coming soon...













**Development Functions**

* ```lrun```: shortcut for base manage.py function to launch the Django development server

        local("python manage.py runserver")

* ```make```: shortcut for base manage.py function to make Django database migrations to sync the dev database

        local("python manage.py makemigrations")

* ```migrate```: shortcut for base manage.py function to apply Django database migrations

        local("python manage.py migrate")

* ```superuser```: shortcut for base manage.py function to create a superuser

        local("python manage.py createsuperuser")


**Bootstrapping Functions**

* ```requirements```:  shortcut to install requirements from repository's ```requirements.txt```

        local("pip install -r requirements.txt")

* ```create_db```: Creates a database based on DATABASE variables in ```settings_development.py``` file

        connection = None
        db_config = CONFIG["database"]
        logger.debug("Creating %s database for %s django project" % (db_config["database"], env.project_name))
        create_statement = "CREATE DATABASE %s" % (db_config["database"])
        try:
            connection = MySQLdb.connect(
                host = db_config["host"],
                user = db_config["username"],
                passwd = db_config["password"]
            )
            cursor = connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(create_statement)
            connection.commit()
        except MySQLdb.DatabaseError, e:
            print "Error %s" % (e)
            sys.exit(1)
        finally:
            if connection:
                connection.close()

* ```makesecret```: generates secret key for use in [django settings](https://github.com/datadesk/django-project-template/blob/master/fabfile/makesecret.py)

        key = ''.join(random.choice(allowed_chars) for i in range(length))
        print 'SECRET_KEY = "%s"' % key

* ```build```: Activates the django-bakery script to build the views specified in ```settings_development.py```

        local("python manage.py build")

* ```buildserver```: Activates the django-bakery development server

        local("python manage.py buildserver")

* ```bootstrap```: Attempts to scaffold the project by:
        * Creating the database
        * Applying initial Django migrations
        * Ingesting the initial data fixtures
        * Creating the Django superuser
        * Running the Django development server


Mac OS Python development environment
=====================================

* Assumming [homebrew](https://brew.sh/) is installed...

    * Install homebrew python

            cd /System/Library/Frameworks/Python.framework/Versions
            sudo rm Current
            brew install python
            brew doctor
            which python
            which pip
            pip install --upgrade setuptools
            pip install --upgrade distribute
            pip install virtualenv
            pip install virtualenvwrapper
            python --version
            source /usr/local/bin/virtualenvwrapper.sh
            sudo ln -s /usr/local/Cellar/python/2.7.8_2 /System/Library/Frameworks/Python.framework/Versions/Current

    * Configure $PATH variables for python, virtualenv

            # homebrew path
            export PATH="/usr/local/bin:$PATH"

            # virtualenvwrapper settings
            export WORKON_HOME=$HOME/.virtualenvs
            export PIP_VIRTUALENV_BASE=$WORKON_HOME
            export PIP_RESPECT_VIRTUALENV=true
            source /usr/local/bin/virtualenvwrapper.sh

    * Install MySQL via homebrew

            brew remove mysql
            brew cleanup
            launchctl unload -w ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist
            rm ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist
            sudo rm -rf /usr/local/var/mysql
            brew install mysql
            ln -sfv /usr/local/opt/mysql/*.plist ~/Library/LaunchAgents

    * Getting mysql up and running

            mysql.server start
            mysql_secure_installation
            mysql -u root -p
            SHOW DATABASES;
            SET default_storage_engine=MYISAM;
