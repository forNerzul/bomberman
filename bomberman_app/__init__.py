from flask import Flask

app = Flask(__name__)

# importar las rutas 
from bomberman_app.controllers import *