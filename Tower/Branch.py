from . import app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# This file was created to initialise part of the site in order avoid circular imports

app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///site.db"
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
db = SQLAlchemy(app)

