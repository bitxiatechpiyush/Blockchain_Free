from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from .blockchain import Blockchain
from . import mongo, w3
import json
from bson import json_util
import jwt
import datetime


main = Blueprint('main', __name__)

blockchain = Blockchain()
secret_key = "supersecretkey"  # Change this to a more secure key

@main.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=request.args.get('address'),
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(proof, previous_hash)

    mongo.db.blocks.insert_one(block)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@main.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400

    if not blockchain.verify_transaction(values):
        return 'Invalid transaction signature', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@main.route('/chain', methods=['GET'])
def full_chain():
    blocks = list(mongo.db.blocks.find())
    response = {
        'chain': json.loads(json_util.dumps(blocks)),
        'length': len(blocks),
    }
    return jsonify(response), 200

@main.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = w3.eth.get_balance(address)
    return jsonify({'balance': w3.from_wei(balance, 'ether')}), 200


@main.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400
    
    hashed_password = generate_password_hash(password)
    
    mongo.db.users.insert_one({
        "username": username,
        "password": hashed_password
    })
    
    return jsonify({"message": "User created successfully"}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = mongo.db.users.find_one({"username": username})
    
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, secret_key, algorithm="HS256")
        
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401