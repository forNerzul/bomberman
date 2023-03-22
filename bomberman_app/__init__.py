from flask import Flask
from bomberman_app.controllers import app_views

app = Flask(__name__)
app.register_blueprint(app_views)