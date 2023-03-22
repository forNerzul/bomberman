# from flask import Flask
# from config import Config, db

# app = Flask(__name__)
# app.config.from_object(Config)
# db.init_app(app)

# # change template folder
# app.template_folder = 'views'

# with app.app_context():
#     db.create_all()
# # run the app
# if __name__ == '__main__':
#     app.run( debug=True, port='3000')
