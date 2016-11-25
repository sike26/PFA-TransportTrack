from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import session, abort, request
from flask import json
from celery import Celery
from libraries.celeryLib.celery_server import make_celery
from datetime import timedelta
from flask import Flask, current_app, request, session
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed
from collections import namedtuple
from functools import partial
from flask.ext.login import current_user
from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed
from flask_pushjack import FlaskGCM
from flask_pushjack import FlaskAPNS
from libraries.graphLib.graphe_tbc import GraphTBC



#Create Flask app
server = Flask(__name__)

# Import Config
server.config.from_pyfile('../server.config')

# SQLAlchemy
db = SQLAlchemy(server)

# Celery
celery = make_celery(server)

# Graphe
G = GraphTBC()

from project.libraries.celeryLib.tasks import *

# FlaskLogin
login_manager = LoginManager(server)

# FlaskPrincipal
Principal(server)

# FlaskGCM
clientGCM = FlaskGCM(server)

# FlaskAPNS
clientAPNS = FlaskAPNS(server)
