from flask import Flask, jsonify, request, current_app
import os
from pymongo import MongoClient
import certifi
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.api import api

mongopass = os.getenv('mongopass')
ca = certifi.where()

client = MongoClient(mongopass, tlsCAFile=ca)
db = client.wedding

app = Flask(__name__)

def doc2json(document):
	json = {}
	for k, v in document.items():
		if isinstance(v, ObjectId):
			json[k] = str(v)
		else:
			json[k] = v
	return json

@api.route('/', methods=['GET'])
def home():
    return 'Welcome to the wedding backend'
    

@api.route('/guests/<guest_id>', methods=['GET'])
def guests(guest_id):
    guest = doc2json(db.guests.find_one({ '_id': ObjectId(guest_id)}))
    print(guest)

    return jsonify(guest), 200
