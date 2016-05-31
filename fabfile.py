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

os.environ[
    "DJANGO_SETTINGS_MODULE"] = "kpcc_backroom_handshakes.settings_production"

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
data functions
"""


def dump_ballot_box():
    """
    shortcut to dump data from ballot box as fixtures
    """
    local("python manage.py dumpdata ballot_box.ResultSource > ballot_box/fixtures/data.json")


def load_ballot_box():
    """
    shortcut to load ballot box data fixtures
    """
    local("python manage.py loaddata ballot_box/fixtures/data.json")


def fetch_sos():
    """
    shortcut for running the management command to fetch sos results
    """
    local("python manage.py fetch_sos_results")


def fetch_lac():
    """
    shortcut for running the management command to fetch sos results
    """
    local("python manage.py fetch_lac_results")


def fetch_all():
    """
    shortcut for running all management commands to fetch results
    """
    local("python manage.py fetch_sos_results")
    local("python manage.py fetch_lac_results")


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


def superuser():
    """
    shortcut for base manage.py function to create a superuser
    """
    local("python manage.py createsuperuser")


def test():
    """
    shortcut for base manage.py function to create a superuser
    """
    local("python manage.py test")

"""
bootstrapping functions
"""


def rename_files():
    """
    shortcut to install requirements from repository's requirements.txt
    """
    os.rename("kpcc_backroom_handshakes/settings_common.py.template",
              "kpcc_backroom_handshakes/settings_common.py")
    os.rename("kpcc_backroom_handshakes/settings_production.py.template",
              "kpcc_backroom_handshakes/settings_production.py")


def requirements():
    """
    shortcut to install requirements from repository's requirements.txt
    """
    local("pip install -r requirements.txt")


def create_db():
    connection = None
    db_config = CONFIG["database"]
    logger.debug("Creating %s database for %s django project" %
                 (db_config["database"], env.project_name))
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
    print 'SECRET_KEY = "%s"' % key


def build():
    local("python manage.py build")


def buildserver():
    local("python manage.py buildserver")


def commit(message='updates'):
    with lcd(settings.DEPLOY_DIR):
        try:
            message = raw_input("Enter a git commit message:  ")
            local("git add -A && git commit -m \"%s\"" % message)
        except:
            print(green("Nothing new to commit.", bold=False))
        local("git push")


def deploy():
    with cd(env.code_dir):
        run("git co %s" % env.local_branch)
        run("git pull")
        with prefix("WORKON_HOME=$HOME/.virtualenvs"):
            with prefix("source /usr/local/bin/virtualenvwrapper.sh"):
                with prefix("workon %s" % (env.project_name)):
                    run("pip install -r %s" % (env.requirements_file))
                    run("python manage.py makemigration")
                    run("python manage.py migrate")


def bootstrap():
    with prefix("WORKON_HOME=$HOME/.virtualenvs"):
        with prefix("source /usr/local/bin/virtualenvwrapper.sh"):
            local("mkvirtualenv %s" % (env.project_name))
            with prefix("workon %s" % (env.project_name)):
                requirements()
                time.sleep(2)
                create_db()
                time.sleep(2)
                migrate()
                time.sleep(2)
                local("python manage.py createsuperuser")


def syncstart():
    # check if requirements need update
    requirements()
    # try migrate
    migrate()
    # load data fixtures
    load_ballot_box()
    # any new dependencies/apps the rest of the team may need?


def __env_cmd(cmd):
    return env.bin_root + cmd
