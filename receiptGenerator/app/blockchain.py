import logging
import hashlib
import json
from datetime import datetime
from cryptography.hazmat.primitives import hashes, hmac

from .models import Chain

logger = logging.getLogger(__name__)

class Blockchain:
    def create_block(self, nonce, previous_hash, data):
        now = datetime.now()
        block = {'timestamp': datetime.timestamp(now),
                 'nonce': nonce,
                 'previous_hash': previous_hash,
                 'data': data
                 #'transactions': self.transactions #New
                }
        #self.transactions = [] #New
        #self.chain.append(block)
        #Chain.objects.create(json_block=block, json_receipt=data)
        return block

   
    def get_last_block(self):
        last_entry_table = Chain.objects.latest('id_chain')
        return last_entry_table.json_block 
        #return self.chain[-1]

    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce

   
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self):
        #previous_block = Chain.objects.earliest()
        #previous_block = chain[0]
        chain = Chain.objects.all()
        is_first = True
        for o in chain:
            block = o.json_block
            if is_first:
                is_first = False
                if block['nonce'] != 1 or block['previous_hash'] != '0':
                    return False
            else:
                if block['previous_hash'] != self.hash(previous_block):
                    return False
                previous_nonce = previous_block['nonce']
                nonce = block['nonce']
                hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
                if hash_operation[:4] != '0000':
                    return False
            previous_block = block
        return True

    '''
        #block_index = 1
        #TODO: Query all lines in a table...
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    '''

    #TODO: this was used to have rapid access to the data
    #TODO: you did not had to query the blocks to find the data
    '''
    def add_transaction(self, sender, receiver, amount, time): #New
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount,
                                  'time': str(datetime.datetime.now())})
        previous_block = self.get_last_block()
        return previous_block['index'] + 1
    '''

    #TODO: do not understand this...
    def add_node(self, address): 
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    #TODO: do not understand this...
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False