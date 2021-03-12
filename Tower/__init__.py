from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app= Flask(__name__)
app.config["SECRET_KEY"] = '800d270989386fa829183328fd42b69a'

bcrypt = Bcrypt(app)



from . import routes