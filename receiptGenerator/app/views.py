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
from .blockchain import Blockchain

logger = logging.getLogger(__name__)

#cache

key = None

blockchain = Blockchain()

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
        block = mine_block(json_receipt)
        Receipt_Block.objects.create(json_receipt['Receipt ID'], block, json_receipt['Receipt Timestamp'])
        #Receipt_Block.objects.create(json_receipt['Receipt ID'], json_receipt, json_receipt['Receipt Timestamp'])
    except:
        return Response('Cannot create the receipt record', status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_201_CREATED)

'''
    Chech if the receipt chain is valid
'''
@csrf_exempt
@api_view(('GET',))
def receipt_valid(request):
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'The chain is valid', status=status.HTTP_200_OK}
    else:
        response = {'The chain is not valid', status=status.HTTP_400_BAD_REQUEST}
    return JsonResponse(response)



# Creating our Blockchain

# Creating an address for the node running our server
#node_address = str(uuid4()).replace('-', '') #New
#root_node = 'e36f0158f0aed45b3bc755dc52ed4560d' #New

# Mining a new block
#@csrf_exempt
#@api_view(('GET',))
#def mine_block(request):
def mine_block(data):
    previous_block = blockchain.get_last_block()
    previous_nonce = previous_block['nonce']
    nonce = blockchain.proof_of_work(previous_nonce)
    previous_hash = blockchain.hash(previous_block)
    #blockchain.add_transaction(sender = root_node, receiver = node_address, amount = 1.15, time=str(datetime.datetime.now()))
    block = blockchain.create_block(nonce, previous_hash, data)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'nonce': block['nonce'],
                'previous_hash': block['previous_hash'],
                'data': data
                #'transactions': block['transactions']}
    return JsonResponse(response)

# Getting the full Blockchain
def get_chain(request):
    if request.method == 'GET':
        response = {'chain': blockchain.chain,
                    'length': len(blockchain.chain)}
    return JsonResponse(response)

# Checking if the Blockchain is valid
'''
def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'All good. The Blockchain is valid.'}
        else:
            response = {'message': 'The Blockchain is not valid.'}
    return JsonResponse(response)
'''

'''
# Adding a new transaction to the Blockchain
@csrf_exempt
def add_transaction(request): #New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        transaction_keys = ['sender', 'receiver', 'amount','time']
        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)
        index = blockchain.add_transaction(received_json['sender'], received_json['receiver'], received_json['amount'],received_json['time'])
        response = {'message': f'This transaction will be added to Block {index}'}
    return JsonResponse(response)
'''

# Connecting new nodes
@csrf_exempt
def connect_node(request):
    if request.method == 'POST':
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=400)
        for node in nodes:
            blockchain.add_node(node)
        response = {'message': 'All the nodes are now connected. The Sudocoin Blockchain now contains the following nodes:',
                    'total_nodes': list(blockchain.nodes)}
    return JsonResponse(response)

# Replacing the chain by the longest chain if needed
def replace_chain(request): 
    if request.method == 'GET':
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                        'new_chain': blockchain.chain}
        else:
            response = {'message': 'All good. The chain is the largest one.',
                        'actual_chain': blockchain.chain}
    return JsonResponse(response)