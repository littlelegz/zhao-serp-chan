# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_talisman import Talisman
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# stdlib
from datetime import datetime
import os

# local
from .client import PicClient

SECRET_KEY = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'
SERP_API_KEY= '78191b018b0d92c5359b5f3e94ce3ee722ad51e395bb32b8dafa0b55ebf92066'
MONGODB_HOST = "mongodb+srv://admin_user:ipg5Gnc1rcdiQUVO@cluster0.66sc1.mongodb.net/Cluster0?retryWrites=true&w=majority"

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
pic_client = PicClient(SERP_API_KEY)

from .movies.routes import movies
from .users.routes import users


def page_not_found(e):
    return render_template("404.html"), 404

app = Flask(__name__)

db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)

app.config["MONGODB_HOST"] = MONGODB_HOST
app.config["SECRET_KEY"] = SECRET_KEY
app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(movies, url_prefix='/')
app.register_error_handler(404, page_not_found)

login_manager.login_view = "users.login"

"""
def create_app(test_config=None):
    app = Flask(__name__)
    csp = {
        'default-src': [
            '\'self\'',
            'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',
            'https://code.jquery.com/jquery-3.4.1.slim.min.js',
            'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
            'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',
        ],
        'img-src': '*'
    }
    #Talisman(
    #    app, 
    #    content_security_policy=csp
    #)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")
    app.config["SECRET_KEY"] = SECRET_KEY
    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(movies, url_prefix='/')
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app 
"""