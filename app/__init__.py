from flask import Flask
from flask_cors import CORS
import os

spassword = os.getenv('spassword')


def create_app():
	app = Flask(__name__)
	app.secret_key = spassword
	
	CORS(app)

	from app.api import api

	app.register_blueprint(api)

	return app