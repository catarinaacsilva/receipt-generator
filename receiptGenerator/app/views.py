import logging
import json
import uuid
import os
import base64
from django.shortcuts import render
from .forms import ReceiptForm
from django.http import JsonResponse
from datetime import datetime
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import rsa
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django.conf import settings
from .models import Receipt_Block

logger = logging.getLogger(__name__)

#cache

key = None

'''
    Initial page just to init the demo
'''
def index(request):
    return render(request, 'index.html')


'''
    Python Cryptography Generate Random Keys 
'''
def generate_keypair():
    if key is not None:
        return key
    else:
        return os.urandom(32)


'''
    Receipt Generator
        Returns a json with input parameters
'''
@csrf_exempt
@api_view(('GET',))
def receiptGenerator(request):
    version = request.GET['version']
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    idreceipt = str(uuid.uuid4())
    if 'language' not in request.GET.keys():
        language = 'English'
    else:
        language = request.GET['language']
    
    selfservicepoint = setting.SELF_SERVICE_POINT

    key = generate_keypair()
    
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(idreceipt.encode())
    selfservicetoken = h.finalize()

    policy = request.GET['policy']
    digest = hashes.Hash(hashes.SHA256())
    digest.update(policy.encode())
    policy_hash = digest.finalize() 
    
    consent = request.GET['consent']
    if consent != 'given' or consent != 'rejected':
        consent = 'rejected'
    
    
    if 'legalJurisdiction' not in request.GET.keys():
        legalJurisdiction = 'Europe'
    else:
        legalJurisdiction = request.GET['legalJurisdiction']
    
    controller = request.GET['controller']

    legalJustification = 'consent'
    methodCollection = 'online web action'
    
    receipt = {'Receipt  Version': int(version), 
    'Receipt Timestamp': timestamp, 
    'Receipt ID': idreceipt, 
    'Language': language, 
    'Self-service point': selfservicepoint,
    'Self-service token': base64.b64encode(selfservicetoken).decode('utf-8'), 
    'Privacy Policy fingerprint': policy, 
    'Consent Status': consent, 
    'Legal Jurisdiction': legalJurisdiction, 
    'Controller Identity': controller, 
    'Legal Justification': legalJustification, 
    'Method of Collection': methodCollection}

    receipt_json = json.dumps(receipt)
   
    digestjson = hashes.Hash(hashes.SHA256())
    digestjson.update(receipt_json.encode())
    receiptFingerprint = digestjson.finalize()
    receipt['Receipt Fingerprint'] = base64.b64encode(receiptFingerprint).decode('utf-8')

    logger.info(receipt)

    return JsonResponse(receipt, content_type='application/json')

'''
    Store receipt on the database and post data on data retention
'''
@csrf_exempt
@api_view(('POST',))
def reply_receipt(request):
    json_receipt = json.loads(request.body)
    logger.info(json_receipt)

    try:
        url = settings.DATA_RETENTION_RECEIPT
        receipt = {'id_receipt':json_receipt['Receipt ID'], 'receipt_timestamp':json_receipt['Receipt Timestamp']}
        x = requests.post(url, data=receipt)
        Receipt_Block.objects.create(json_receipt['Receipt ID'], json_receipt, json_receipt['Receipt Timestamp'])
    except:
        return Response('Cannot create the receipt record', status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_201_CREATED)




''' ########################################################################
                                BlockChain API
########################################################################'''

class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(nonce = 1, previous_hash = '0')

    '''
        Add new block to the chain
    '''
    def create_block(self, nonce, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': nonce,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    '''
        Return the previous block to the current block
    '''
    def get_previous_block(self):
        return self.chain[-1]


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

    '''
        Hash of the given block
    '''
    def hash(self, block):
        blockJson = json.dumps(block)
        digest = hashes.Hash(hashes.SHA256())
        digest.update(blockJson.encode())
        return digest.finalize()
    
    '''
        Validate chain
    '''
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            #hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            digest = hashes.Hash(hashes.SHA256())
            digest.update(str(nonce**2 - previous_nonce**2).encode())
            hash_operation = digest.finalize().encode('hex').upper()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True


blockchain = Blockchain()

'''
    Mining a new block
'''
def mine_block(request):
    if request.method == 'GET':
        previous_block = blockchain.get_previous_block()
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        previous_hash = blockchain.hash(previous_block)
        block = blockchain.create_block(nonce, previous_hash)
        response = {'message': 'Congratulations, you just mined a block!',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'nonce': block['nonce'],
                    'previous_hash': block['previous_hash']}
    return JsonResponse(response)


'''
    Getting the full Blockchain
'''
def get_chain(request):
    if request.method == 'GET':
        response = {'chain': blockchain.chain,
                    'length': len(blockchain.chain)}
    return JsonResponse(response)

'''
    Checking if the Blockchain is valid
'''
def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'All good. The Blockchain is valid.'}
        else:
            response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return JsonResponse(response)