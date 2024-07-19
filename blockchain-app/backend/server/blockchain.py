import hashlib
import json
from time import time
from web3 import Web3
import base64
from eth_account.messages import encode_defunct

w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_block(previous_hash='1', proof=100)

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.encode_data(self.current_transactions),
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount, message=None):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'message': message,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def verify_transaction(self, transaction):
        try:
            message = f"{transaction['sender']}{transaction['recipient']}{transaction['amount']}"
            message_encoded = encode_defunct(text=message)
            recovered_address = w3.eth.account.recover_message(message_encoded, signature=transaction['signature'])
            return recovered_address.lower() == transaction['sender'].lower()
        except Exception as e:
            print(f"Error verifying transaction: {e}")
            return False

    def encode_data(self, data):
        return base64.b64encode(json.dumps(data).encode()).decode('utf-8')

    def decode_data(self, encoded_data):
        return json.loads(base64.b64decode(encoded_data).decode('utf-8'))

    def get_decoded_chain(self):
        decoded_chain = []
        for block in self.chain:
            decoded_block = block.copy()
            decoded_block['transactions'] = self.decode_data(block['transactions'])
            decoded_chain.append(decoded_block)
        return decoded_chain