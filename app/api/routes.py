from flask import Flask, jsonify, request, current_app
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.api import api
from functools import wraps
import os
import certifi
import jwt

mongopass = os.getenv('mongopass')
ca = certifi.where()

client = MongoClient(mongopass, tlsCAFile=ca)
db = client.wedding

app = Flask(__name__)


# needed functions
def doc2json(document):
	json = {}
	for k, v in document.items():
		if isinstance(v, ObjectId):
			json[k] = str(v)
		else:
			json[k] = v
	return json

def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		guest_id = kwargs['guest_id']
		auth = request.headers.get('Authorization')

		try:
			token = auth.split(' ')[1]
			payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
			guest = db.guests.find_one({'_id': ObjectId(guest_id)})

			assert guest
			assert guest_id == payload['_id']
			assert guest['token'] == token
		except:
			return jsonify({'error': 'Invalid credentials.'}), 401

		return f(*args, **kwargs)

	return wrapper







# Routes
@api.route('/', methods=['GET'])
def home():
    return 'Welcome to the wedding backend'
    

@api.route('/guests/<guest_id>', methods=['GET'])
def guests(guest_id):
    guest = doc2json(db.guests.find_one({ '_id': ObjectId(guest_id)}))
    print(guest)

    return jsonify(guest), 200
