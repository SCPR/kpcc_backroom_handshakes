from __future__ import with_statement
from fabric.api import task, env, run, local, roles, cd, execute, hide, puts, sudo, prefix
import re
import os
import sys
import time
import datetime
import logging
import shutil
import MySQLdb
import random
import yaml
from subprocess import Popen, PIPE
from fabric.operations import prompt
from fabric.contrib.console import confirm
from fabric.context_managers import lcd
from fabric.colors import green
from fabric.contrib import django

os.environ["DJANGO_SETTINGS_MODULE"] = "kpcc_backroom_handshakes.settings_production"

from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))

CONFIG_PATH = "%s_CONFIG_PATH" % ("kpcc_backroom_handshakes".upper())

CONFIG_FILE = os.environ.setdefault(CONFIG_PATH, "./development.yml")

CONFIG_YML = os.path.join(PROJECT_PATH, "development.yml")

CONFIG = yaml.load(open(CONFIG_YML))

env.hosts = CONFIG["deployment_env"]["hosts"]

env.project_name = CONFIG["deployment_env"]["project_name"]

env.local_branch = CONFIG["deployment_env"]["local_branch"]

env.remote_ref = CONFIG["deployment_env"]["remote_ref"]

env.requirements_file = CONFIG["deployment_env"]["requirements_file"]

env.use_ssh_config = CONFIG["deployment_env"]["use_ssh_config"]

env.code_dir = CONFIG["deployment_env"]["code_dir"]

logger = logging.getLogger("root")
logging.basicConfig(
    format="\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)


"""
functions that fetch our election data from our sources
"""

def election_night():
    """
    run this on election night to fetch data
    from live elections and build out pages...
    """
    local("python manage.py election_night")

def fetch_sos():
    """
    shortcut for running the management command to fetch
    election results from the california secretary of state
    """
    local("python manage.py fetch_sos_results")

def fetch_lac():
    """
    shortcut for running the management command to fetch
    election results from the los angeles county
    """
    local("python manage.py fetch_lac_results")

def fetch_sbc():
    """
    shortcut for running the management command to fetch
    election results from the san bernardino county
    """
    local("python manage.py fetch_sbc_results")

def fetch_oc():
    """
    shortcut for running the management command to fetch
    election results from the orange county
    """
    local("python manage.py fetch_oc_results")

def fetch_all():
    """
    shortcut for fetch results from all four primary sources
    """
    local("python manage.py fetch_sos_results")
    local("python manage.py fetch_oc_results")
    local("python manage.py fetch_lac_results")
    local("python manage.py fetch_sbc_results")

def fetch_maplight():
    """
    shortcut for fetch data from the maplight campaign finance api
    but it's specific to the general-2016-11-08 election.
    """
    local("python manage.py fetch_measure_finance")


"""
functions that dump and load existing election data from our applications
"""

def dump_ballot_box():
    """
    shortcut to dump data from ballot box as fixtures
    """
    local("python manage.py dumpdata ballot_box > ballot_box/fixtures/ballot_box.json")

def load_ballot_box():
    """
    shortcut to load ballot box data fixtures
    """
    local("python manage.py loaddata ballot_box/fixtures/ballot_box.json")

def dump_registrar():
    """
    shortcut to dump data from ballot box as fixtures
    """
    local("python manage.py dumpdata election_registrar > election_registrar/fixtures/election_registrar.json")

def load_registrar():
    """
    shortcut to load ballot box data fixtures
    """
    local("python manage.py loaddata election_registrar/fixtures/election_registrar.json")

def dump_playlist():
    """
    shortcut to dump data from ballot box as fixtures
    """
    local("python manage.py dumpdata newscast > newscast/fixtures/newscast-playlist.json")

def load_playlist():
    """
    shortcut to dump data from ballot box as fixtures
    """
    local("python manage.py loaddata newscast/fixtures/newscast-playlist.json")

def dump_maplight():
    """
    shortcut to dump data from ballot box as fixtures
    """
    local("python manage.py dumpdata measure_finance > measure_finance/fixtures/measure_finance.json")

def load_maplight():
    """
    shortcut to dump data from ballot box as fixtures
    """
    local("python manage.py loaddata measure_finance/fixtures/measure_finance.json")

def dump_fixtures():
    """
    shortcut to dump all data fixtures with logging
    """
    logger.debug("Dumping data fixtures for %s django project" % (CONFIG["database"]["database"]))
    dump_registrar()
    logger.debug("Election data dumped")
    dump_ballot_box()
    logger.debug("Election results data dumped")
    dump_playlist()
    logger.debug("Newscast playlists data dumped")
    dump_maplight()
    logger.debug("Maplight measure finance data dumped")

def load_fixtures():
    """
    shortcut to load all data fixtures with logging
    """
    logger.debug("Loading data fixtures for %s django project" % (CONFIG["database"]["database"]))
    load_registrar()
    logger.debug("Election data loaded")
    load_ballot_box()
    logger.debug("Election results data loaded")
    load_playlist()
    logger.debug("Newscast playlists data loaded")
    load_maplight()
    logger.debug("Maplight measure finance data loaded")


"""
django-bakery functions
"""

def build():
    """
    """
    local("python manage.py build")


def buildserver():
    """
    """
    local("python manage.py buildserver")


def publish():
    """
    """
    local("python manage.py publish")


"""
development functions
"""

def lrun():
    """
    shortcut for base manage.py function to run the dev server
    """
    local("python manage.py runserver")

def make():
    """
    shortcut for base manage.py function to sync the dev database
    """
    local("python manage.py makemigrations")

def migrate():
    """
    shortcut for base manage.py function to apply db migrations
    """
    local("python manage.py migrate")

def test():
    """
    shortcut for base manage.py function to create a superuser
    """
    local("python manage.py test")


def set_featured():
    """
    """
    local("python manage.py set_featured_contests")

def zero_it():
    """
    """
    local("python manage.py zero_out_data")


"""
bootstrapping functions
"""

def requirements():
    """
    shortcut to install requirements from repository's requirements.txt
    """
    local("pip install -r requirements.txt")

def superuser():
    """
    shortcut for base manage.py function to create a superuser
    """
    local("python manage.py createsuperuser")

def create_db():
    connection = None
    db_config = CONFIG["database"]
    logger.debug("Creating %s database for django project" % (db_config["database"]))
    create_statement = "CREATE DATABASE %s" % (db_config["database"])
    try:
        connection = MySQLdb.connect(
            host=db_config["host"],
            user=db_config["username"],
            passwd=db_config["password"]
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

def makesecret(length=50, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'):
    """
    generates secret key for use in django settings
    https://github.com/datadesk/django-project-template/blob/master/fabfile/makesecret.py
    """
    key = ''.join(random.choice(allowed_chars) for i in range(length))
    print 'SECRET_KEY: "%s"' % key

def bootstrap():
    """
    run tasks to setup the base project
    """
    create_db()
    time.sleep(2)
    migrate()
    time.sleep(2)
    load_fixtures()
    time.sleep(2)
    superuser()
    lrun()

def syncstart():
    """
    get in sync quickly when collaborating
    """
    requirements()
    migrate()
    load_fixtures()

def syncend():
    """
    end a working session and dump out
    potential changes to requirements and data
    """
    local("pip freeze > requirements.txt")
    make()
    dump_fixtures()

def __env_cmd(cmd):
    return env.bin_root + cmd
