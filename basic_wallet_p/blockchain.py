import hashlib
import json
import requests
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request, render_template

class Users:
    def __init__(self):
        self.ids = []

    def new_user(self, id):
        self.ids.append(id)
    
    def get_users(self):
        return self.ids

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
​
        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block
​
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'proof': proof,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash,
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the block to the chain
        self.chain.append(block)
        # Return the new block
        return block

    def new_transaction(self, sender, receiver, amount):

        new_transaction = {
            'timestamp': time(),
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        }

        self.current_transactions.append(new_transaction)

        # return index of block that will hold this transaction
        future_index = self.last_block['index'] + 1

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block
​
        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.

        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        block_string = json.dumps(block, sort_keys=True)
        string_in_bytes = block_string.encode()

        # TODO: Hash this string using sha256
        hash_object = hashlib.sha256(string_in_bytes)
        hash_string = hash_object.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        guess = f'{block_string}{proof}'.encode()

        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:3] == '000'

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()
users = Users()

@app.route('/mine', methods=['POST'])
def mine():
    """
    Modify the mine endpoint to instead receive and validate or reject a new proof sent by a client.
    It should accept a POST
    Use data = request.get_json() to pull the data out of the POST
    Note that request and requests both exist in this project
    Check that 'proof', and 'id' are present
    return a 400 error using jsonify(response) with a 'message'
    Return a message indicating success or failure. Remember, a valid proof should fail for all senders except the first.
    """
    data = request.get_json()

    if data["proof"] and data["id"]:
        miner_id = data['id']
        block = blockchain.last_block
        block_string = json.dumps(block, sort_keys=True)
        proof = data["proof"]
        
        if blockchain.valid_proof(block_string, proof):
        # Forge the new Block by adding it to the chain with the proof
            block_hash = blockchain.hash(block)
            new_block = blockchain.new_block(proof, block_hash)
            blockchain.new_transaction(sender='0', receiver=miner_id, amount=1)

            response = {
                'message': "New block forged successfully."
            }
        
        else:
            response = {
                'message': "Proof not validated."
            }

    else:
        response = {
                'message': "Missing proof or id."
            }

    return jsonify(response)


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'chain': blockchain.chain,
        'chain_length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.chain[-1]
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()

    required = ['sender', 'receiver', 'amount']

    if not all(k in data for k in required):
        response ={'message': "Missing values."}
        return jsonify(response), 400

    index = blockchain.new_transaction(sender=data['sender'], receiver=data['receiver'], amount=data['amount'])

    response = {
        'message': f'Your transaction will be in block {index}'
    }

    return jsonify(response), 200

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.values.get("user_name") 
    users.new_user(name)
    return render_template("base.html", title='Home')

@app.route('/user', methods=['POST'])
def user():
    # name = request.values.get("user_name") 
    requested_user = request.values.get("user_balance")
    list_users = users.get_users()

    # requested_user = 'nayomi-chibana'
    # list_users = ['nayomi-chibana', 'john-doe']
    r = requests.get(url="http://localhost:5000/chain")
    data = r.json()

    credit = [] #(sender, amount)
    debit = [] #(receiver, amount)

    for i in range(len(data['chain'])):
        for j in range(len(data['chain'][i]['transactions'])):
            if data['chain'][i]['transactions'][j]['receiver'] == requested_user:
                credit.append((data['chain'][i]['transactions'][j]['sender'], data['chain'][i]['transactions'][j]['amount'], data['chain'][i]['transactions'][j]['timestamp']))
            if data['chain'][i]['transactions'][j]['sender'] == requested_user:
                debit.append((data['chain'][i]['transactions'][j]['receiver'], data['chain'][i]['transactions'][j]['amount'], data['chain'][i]['transactions'][j]['timestamp']))
    
    balance = sum(lis[1] for lis in credit) - sum(lis[1] for lis in debit)

    return render_template("user.html", users=requested_user, balance=balance, credits=credit, debits=debit)
    


@app.route('/')
def root():
    return render_template("base.html", title='Home')

# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)