from flask import Flask
from config import Config
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)

#Keep below line at the bottom
from application import routes
