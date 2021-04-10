from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail

#Initialisation file used to initialise the system

app= Flask(__name__)
app.config["SECRET_KEY"] = '800d270989386fa829183328fd42b69a'
bcrypt = Bcrypt(app)
app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "courseworkemail2021@gmail.com"
app.config["MAIL_PASSWORD"] = "T0werTesting"
mail = Mail(app)

from . import routes