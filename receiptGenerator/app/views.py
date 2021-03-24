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
from django.db import transaction

from .models import Receipt_Block
from .models import Chain

from django.conf import settings
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
# TODO: send receipt to the data retention and test it
@csrf_exempt
@api_view(('POST',))
def reply_receipt(request):
    json_receipt = json.loads(request.body)
    logger.info(json_receipt)

    #TODO: Check receipt

    try:
        #url = settings.DATA_RETENTION_RECEIPT
        #receipt = {'id_receipt':json_receipt['Receipt ID'], 'receipt_timestamp':json_receipt['Receipt Timestamp']}
        #x = requests.post(url, data=json_receipt)
        with transaction.atomic():
            block = mine_block(json_receipt)
            Chain.objects.create(json_block=block, json_receipt=json_receipt)
    except Exception as e:
        handle_exception()
        print(e)
        return Response('Cannot create the receipt record', status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_201_CREATED)

'''
    Chech if the receipt chain is valid
'''
@csrf_exempt
@api_view(('GET',))
def receipt_valid(request):
    is_valid = blockchain.is_chain_valid()
    if is_valid:
        response = JsonResponse({'Message':'The chain is valid', 'Valid':True}, status=status.HTTP_201_CREATED)
    else:
        response = JsonResponse({'Message':'The chain is not valid', 'Valid': False}, status=status.HTTP_400_BAD_REQUEST)
    return response

'''
    Add new block
'''
def mine_block(data):
    if not Chain.objects.exists():
        block = blockchain.create_block(nonce = 1, previous_hash = '0', data=data)
    else:
        previous_block = blockchain.get_last_block()
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        previous_hash = blockchain.hash(previous_block)
        block = blockchain.create_block(nonce, previous_hash, data)
    response = {'timestamp': block['timestamp'],
    'nonce': block['nonce'],
    'previous_hash': block['previous_hash'],
    'data': data}
                   
    return response

