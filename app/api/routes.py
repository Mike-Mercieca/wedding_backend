from flask import Flask, jsonify, request, current_app
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.api import api
from functools import wraps
from guests import guests_schema
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
    
# Get one guest information
@api.route('/guests/<guest_id>', methods=['GET'])
def guests(guest_id):
    guest = doc2json(db.guests.find_one({ '_id': ObjectId(guest_id)}))
    print(guest)

    return jsonify(guest), 200


# Create a new guest
@api.route('/guests/register', methods=['POST'])
def new_guest():
    data = request.get_json()

    try:
        username = data['username']
        password = data['password']
    except:
        return jsonify({'error': 'Missing gields.'}), 400
    
    if db.guests.find_one({'username': username}):
        return jsonify({'error': 'Username already exists.'}), 400

    guests_schema['username'] = username
    guests_schema['password'] = generate_password_hash(password)
    db.guests.update_one(guests_schema,{ '$set':guests_schema}, upsert=True)

    return jsonify(doc2json(guests_schema)), 200


# Login a guest
@api.route('/guests/login', methods=['POST'])
def login():
    data = request.get_json()

    try:
        username = data['username']
        password = data['password']
    except:
        return jsonify({'error': 'Missing fields.'}), 400

    guest = db.guests.find_one({'username': username})

    if not guest:
        return jsonify({'error': 'Username does not exist.'}), 400
    
    if check_password_hash(guest['password'], password):
        token = jwt.encode({
            '_id': str(guest['_id'])
        }, current_app.config.get('SECRET_KEY'))

        db.guests.update_one({'_id': guest['_id']}, {'$set': {
            'token': token
        }})
        
        return jsonify({'token': token, '_id': str(guest['_id'])}), 200

    return jsonify({'error': 'Password is incorrect.'}), 400


# Logout a guest
@api.route('/guests/logout', methods=['POST'])
def logout():
    auth = request.headers.get('Authorization')

    try:
        token = auth.split(' ')[1]
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms =['HS256'])
        print(payload)
        user = db.guests.find_one({'_id': ObjectId(payload['_id'])})

        print(user)

        assert user
        assert user['token'] == token 

        db.guests.update_one({'_id': ObjectId(payload['_id'])}, {'$set': {
            'token': ''
        }})
    except:
        return jsonify({'error': 'Invalid credentials.'}), 401

    return jsonify(), 200


# Add additional guests to username
@api.route('/guests/<guest_id>/plusone', methods=['PUT'])
def plusone(guest_id):
    data = request.get_json()
    db.guests.update_one({'_id': ObjectId(guest_id)}, {'$set': data})

    guest = db.guests.find_one({'_id': ObjectId(guest_id)})
    return jsonify(doc2json(guest)), 200






