What is this?
=============

A project of loosely coupled applications that force aspects of the political process to give each other a clean handshake ... with gloves on.

But seriously...


Table of Contents
=================

* [Assumptions](#assumptions)
* [Quickstart](#quickstart-to-get-up-and-running)
* [Ingesting And Baking Election Data](#ingesting-and-baking-election-data)
* [Config and Settings](#config-and-settings)
* [Available Fabric Commands](#available-fabric-commands)
* [Building A Mac OS Python Dev Environment](#building-a-mac-os-python-dev-environment)


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
        * Create the directory structure for the ballot_box application: ```fab build_data_dirs```
        * Creating the Django superuser: ```python manage.py createsuperuser```
        * Running the Django development server: ```fab lrun```

* Navigate to ```http://127.0.0.1:8000/``` and you should arrive at the homepage that shows the elections we have processed using the application so far.

----

Ingesting And Baking Election Data
==================================

Assuming you're up and running successfully, let's attempt to see if we can access data from the most recent election...

* In ```development.yml``` add the Slack Auth token and API key at line 80 and line 81. KPCC'ers can find this in our password manager program.

* Now you should be able to now run ```fab fetch_lac``` from the command line. If everything runs appropriately you should see the following output...

    [] Executing task 'fetch_lac'
    [localhost] local: python manage.py fetch_lac_results
    INFO: manager_lac_results.py (def get_results_file 61):
    *** Beginning Request ***
        * Success! http://rrcc.co.la.ca.us/results/2619mar17.ets responded with a file
        * Success! _2017_03_21_15_04_19_lac_2619mar17.ets downloaded
        * Success! _2017_03_21_15_04_19_lac_2619mar17.ets is a valid file
        * Skipping because lac_latest exists
        * Success! los-angeles-county-2017-municipal-primary.txt is ready to parse
        * Success! _2017_03_21_15_04_19_lac_2619mar17.ets is archived
        * Success: los-angeles-county-2017-municipal-primary.txt exists
    *** Ending Request ***

    INFO: manager_lac_results.py (def parse_results_file 101):
    *****
    we have new data to save and we'll update timestamps in the database
    *****
    INFO: manager_lac_results.py (def parse_results_file 119):  we've finished processing lac results

    Task finished at 2017-03-21 15:04:27.048844

    Done.

* Once the script has finished processing, run ```fab build``` to bake out views as flat HTML pages that will be pushed to a S3 bucket and used to display results and charts to the people of the world.

----

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

We started to add some variables to ```development.yml```. Here's what all of the variables in that file stand for.

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

* ```installed_apps```: Django applications that we've enabled by default out of the box.
    - ```massadmin```: [Docs and code](https://github.com/burke-software/django-mass-edit)
    - ```slacker_log_handler```: [Docs and code](https://github.com/mathiasose/slacker_log_handler)
    - ```bakery```: [Docs and code](https://django-bakery.readthedocs.io/en/latest/index.html)
    - ```election_registrar```: [Docs and code](/election_registrar)
    - ```ballot_box```: [Docs and code](/ballot_box)
    - ```newscast```: [Docs and code](/newscast)
    - ```measure_finance```: [Docs and code](/measure_finance)

* ```deployment_env```: Variables to aid in automatic deployment of the project and its application.
    - ```hosts```: Default is ```""```.
    - ```project_name```: Default is ```""```.
    - ```local_branch```: Default is ```""```.
    - ```remote_ref```: Default is ```""```.
    - ```requirements_file```: Default is ```""```.
    - ```use_ssh_config```: Default is ```False```.
    - ```code_dir```: Default is ```""```.

* ```build```: Variabes for the django-bakery python library that allows us to serve up views as flat HTML files that are pushed to an Amazon S3 bucket. Docs on settings variables are [here](https://django-bakery.readthedocs.io/en/latest/settingsvariables.html).
    - ```aws_bucket_name```: Default is ```""```. The name of the [Amazon S3 "bucket"](http://aws.amazon.com/s3/) were you want to publish the flat files in your local BUILD_DIR. KPCC's is documented elsewhere.
    - ```aws_access_key_id```: Default is ```""```. A part of your secret Amazon Web Services credentials. Necessary to upload files to S3. KPCC's is documented elsewhere.
    - ```aws_secret_access_key```: Default is ```""```. A part of your secret Amazon Web Services credentials. Necessary to upload files to S3. KPCC's is documented elsewhere.
    - ```aws_s3_host```: Default is ```s3-accelerate.amazonaws.com```, Amazon's accelerated upload service
    - ```bakery_gzip```: Default is ```True``` Opt in to automatic gzipping of your files in the build method and addition of the required headers when deploying to Amazon S3.
    - ```build_dir```: Absolute path to the location of the ```kpcc_backroom_handshakes/latest_build``` directory which is the location of where you want the flat files to be built.
    - ```views```: The list of views you want to be built out as flat files when the build management command is executed. The following are the views we've enabled by default:
        - "election_registrar.views.ElectionDetailView"
        - "ballot_box.views.BakedHomepageIndex"
        - "ballot_box.views.BakedFeaturedIndex"
        - "ballot_box.views.BakedResultsIndex"
        - "ballot_box.views.BakedEmbeddedDetail"
        - "measure_finance.views.InitialDetailView"
    - ```bakery_cache_control```: Set cache-control headers based on content type. Headers are set using the max-age= format so the passed values should be in seconds ('text/html': 900 would result in a Cache-Control: max-age=900 header for all text/html files). By default we set for html and javascript.
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

**Functions That Fetch Our Election Data From Our Sources**

* ```election_night```: run this on election night to fetch data from live elections and build out pages...

        local("python manage.py election_night")

* ```fetch_sos```: shortcut for running the management command to fetch election results from the california secretary of state

        local("python manage.py fetch_sos_results")

* ```fetch_lac```: shortcut for running the management command to fetch election results from the los angeles county

        local("python manage.py fetch_lac_results")

* ```fetch_sbc```: shortcut for running the management command to fetch election results from the san bernardino county

        local("python manage.py fetch_sbc_results")

* ```fetch_oc```: shortcut for running the management command to fetch election results from the orange county

        local("python manage.py fetch_oc_results")

* ```fetch_all```: shortcut for fetch results from all four primary sources

        local("python manage.py fetch_sos_results")
        local("python manage.py fetch_oc_results")
        local("python manage.py fetch_lac_results")
        local("python manage.py fetch_sbc_results")

* ```fetch_maplight```: shortcut for fetch data from the maplight campaign finance api but it's specific to the general-2016-11-08 election.

        local("python manage.py fetch_measure_finance")

**Dump And Load Existing Election Data**

* ```dump_ballot_box```: shortcut to dump data from ballot box as fixtures

        local("python manage.py dumpdata ballot_box > ballot_box/fixtures/ballot_box.json")

* ```load_ballot_box```: shortcut to load ballot box data fixtures

        local("python manage.py loaddata ballot_box/fixtures/ballot_box.json")

* ```dump_registrar```: shortcut to dump data from ballot box as fixtures

        local("python manage.py dumpdata election_registrar > election_registrar/fixtures/election_registrar.json")

* ```load_registrar```: shortcut to load ballot box data fixtures

        local("python manage.py loaddata election_registrar/fixtures/election_registrar.json")

* ```dump_playlist```: shortcut to dump data from ballot box as fixtures

        local("python manage.py dumpdata newscast > newscast/fixtures/newscast-playlist.json")

* ```load_playlist```: shortcut to dump data from ballot box as fixtures

        local("python manage.py loaddata newscast/fixtures/newscast-playlist.json")

* ```dump_maplight```: shortcut to dump data from ballot box as fixtures

        local("python manage.py dumpdata measure_finance > measure_finance/fixtures/measure_finance.json")

* ```load_maplight```:shortcut to dump data from ballot box as fixtures

        local("python manage.py loaddata measure_finance/fixtures/measure_finance.json")

* ```dump_fixtures```: shortcut to dump all data fixtures with logging

        dump_registrar()
        dump_ballot_box()
        dump_playlist()
        dump_maplight()

* ```load_fixtures```: shortcut to load all data fixtures with logging

        load_registrar()
        load_ballot_box()
        load_playlist()
        load_maplight()

**django-bakery functions**

* ```build```: Activates the django-bakery script to build the views specified in ```config.yml``` or ```development.yml```

        local("python manage.py build")

* ```buildserver```: Activates the django-bakery development server

        local("python manage.py buildserver")

* ```publish```: Publishes views and static files in the build directory to Amazon S3

        local("python manage.py publish")

**Development Functions**

* ```lrun```: shortcut for base manage.py function to run the dev server

        local("python manage.py runserver")

* ```make```: shortcut for base manage.py function to sync the dev database

        local("python manage.py makemigrations")

* ```migrate```: shortcut for base manage.py function to apply db migrations

        local("python manage.py migrate")

* ```test```: shortcut for base manage.py function to create a superuser

        local("python manage.py test")

* ```set_featured```:

        local("python manage.py set_featured_contests")

* ```zero_it```:

        local("python manage.py zero_out_data")

**Bootstrapping Functions**

* ```requirements()```:  shortcut to install requirements from repository's ```requirements.txt```

        local("pip install -r requirements.txt")

* ```superuser```: shortcut for base manage.py function to create a superuser

        local("python manage.py createsuperuser")

* ```create_db```:

* ```makesecret```: generates secret key for use in django settings

* ```bootstrap```: run tasks to setup the base project

* ```syncstart```: get in sync quickly when collaborating

        requirements()
        migrate()
        load_fixtures()

* ```syncend```: end a working session and dump out potential changes to requirements and data

        local("pip freeze > requirements.txt")
        make()
        dump_fixtures()

----

Building A Mac OS Python Dev Environment
========================================

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
