import logging
import json
import uuid
import os
import base64
import requests
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

from django.conf import settings

from .models import Receipt

logger = logging.getLogger(__name__)


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
    try:
        version = request.GET['version']
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        idreceipt = str(uuid.uuid4())
        if 'language' not in request.GET.keys():
            language = 'English'
        else:
            language = request.GET['language']
        
        selfservicepoint = settings.SELF_SERVICE_POINT

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

    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'timestamp': timestamp, 'receipt': receipt}, status=status.HTTP_201_CREATED)


'''
    Remove receipts: for debug mode
'''

@csrf_exempt
@api_view(('POST',))
def removeReceipt(request):
    parameters = json.loads(request.body)
    email = parameters['email']

    try:
        with transaction.atomic():
            Receipt.objects.filter(email=email).delete()
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)

'''
    Return the most recent receipt id for the given email
'''
@csrf_exempt
@api_view(('GET',))
def getRecentReceipt(request):
    email = request.GET['email']

    try:
        receipt_info = Receipt.objects.filter(email=email).order_by('id_receipt')[0]
        id_receipt = receipt_info.id_receipt
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'email': email, 'Recent receipt':id_receipt})



'''
    Store sign receipt
'''
@csrf_exempt
@api_view(('POST',))
def storeReceipt(request):
    parameters = json.loads(request.body)
    json_receipt = parameters['json_receipt']
    email = parameters['email']
    state = parameters['state']

    try:
        r = Receipt.objects.create(email=email, json_receipt=json_receipt, state = state)
        id_receipt = r.id_receipt
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'email': email, 'id_receipt': id_receipt})



'''
    Return all the receipts id given the email
'''
@csrf_exempt
@api_view(('GET',))
def getReceipt(request):
    email = request.GET['email']

    try:
        receipt_info = Receipt.objects.filter(email=email)
        response = []
        for r in receipt_info:
            response.append({'receipt_id':r.id_receipt, 'timestamp': r.timestamp_now})
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'email': email, 'receipts':response})


'''
    Return the state for a given receipt
'''

@csrf_exempt
@api_view(('GET',))
def receiptState(request):
    email = request.GET['email']
    id_receipt = request.GET['id_receipt']
    
    try:
        receipt = Receipt.objects.get(email=email, id_receipt=id_receipt)
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'email': email, 'receipt id': id_receipt, 'state':receipt.state})


'''
    Return the state for all the receipts
'''
@csrf_exempt
@api_view(('GET',))
def receiptAllState(request):
    email = request.GET['email']

    try:
        receipt_state = Receipt.objects.filter(email=email)
        response = []
        for r in receipt_state:
            response.append({'Receipt id': r.id_receipt, 'state': r.state})
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'email': email, 'Receipt states':response}, status=status.HTTP_201_CREATED)


'''
    Get a complete information about receipts for a given email
'''
@csrf_exempt
@api_view(('GET',))
def infoReceipt(request):
    email = request.GET['email']

    try:
        receipt_info = Receipt.objects.filter(email=email)
        response = []
        for r in receipt_info:
            response.append({'receipt_id':r.id_receipt, 'timestamp': r.timestamp_now, 'Receipt': r.json_receipt, 'State': r.state})
    except Exception as e:
        return Response(f'Exception: {e}\n', status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'email': email, 'receipts':response}, status=status.HTTP_201_CREATED)
