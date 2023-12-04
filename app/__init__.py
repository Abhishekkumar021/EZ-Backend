from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from app.config import Config

app = Flask(__name__)
app.config.from_object("app.config.Config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
app.config.from_object(Config)

from app import routes, models

