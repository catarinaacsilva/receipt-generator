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
    Store receipt on the database
'''
@csrf_exempt
@api_view(('POST',))
def reply_receipt(request):
    json_receipt = json.loads(request.body)
    logger.info(json_receipt)

    try:
        Receipt_Block.objects.create(json_receipt['Receipt ID'], json_receipt, json_receipt['Receipt Timestamp'])
    except:
        return Response('Cannot create the receipt record', status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_201_CREATED)