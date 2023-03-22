#Project Flask MVC
from bomberman_app.config import Config, db
from bomberman_app import app
from bomberman_app.controllers import app_views

__author__ = "forNerzul"
__version__ = "1"
__email__ = "sbeardman92@gmail.com"


app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(app_views)

# change template folder
app.template_folder = 'views'


with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run( port=3000, debug=True)