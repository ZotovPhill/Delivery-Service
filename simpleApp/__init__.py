from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import configparser
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "a671a8bd80c79690a2800dd22d05aa95"

config = configparser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.ini"))
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://%s:%s@%s/%s" % (
    config["mysqlDB"]["user"],
    config["mysqlDB"]["password"],
    config["mysqlDB"]["host"],
    config["mysqlDB"]["database"],
)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "home"

from simpleApp import routes
