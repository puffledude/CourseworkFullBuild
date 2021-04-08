from . import app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///site.db"
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
db = SQLAlchemy(app)

