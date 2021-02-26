import random
import logging
from django.shortcuts import render
from .forms import ReceiptForm
from django.http import JsonResponse
from datetime import datetime


'''
    Initial page just to init the demo
'''
def index(request):
    return render(request, 'index.html')

'''
    Simple form (it can be used to authentication)
'''
def receiptForm(request):
    submitbutton= request.POST.get("submit")

    firstname=''
    lastname=''

    form= ReceiptForm(request.POST or None)
    if form.is_valid():
        firstname= form.cleaned_data.get("firstname")
        lastname= form.cleaned_data.get("lastname")


    context= {'form': form, 'firstname': firstname, 'lastname':lastname,
              'submitbutton': submitbutton}
        
    return render(request, 'form.html', context)

'''
    Receipt Generator
        Returns a json with input parameters
        (missing the final structure)
'''
def receiptGenerator(request):
    version = request.GET['firstName']
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    randomid = random.randint(0, 1000)
    idreceipt = randomid+timestamp
    if request.GET['language'] == Null:
        language = 'English'
    else:
        language = request.GET['language']
    #self-service point
    #self-service token
    #privacy policy fingerprint

    consent = request.GET['consent']
    if consent != 'given' || consent =! 'rejected':
        return logging.error('wrong status for consent. Consent should be given or rejected')
    else:
        return logging.info('It is all right with consent!')
    
    legalJurisdiction = request.GET['legalJurisdiction']
    if request.GET['legalJurisdiction'] == Null:
        legalJurisdiction = 'Europe'
    else:
        legalJurisdiction = request.GET['legalJurisdiction']
    
    controller = request.GET['controller']

    legalJustification = 'consent'
    methodCollection = 'online web action'
    
    receipt = {'version': version, 'timestamp': timestamp, 'id': idreceipt, 'language': language, 'consent': consent, 'legalJurisdiction': legalJurisdiction, 
    'controller': controller, 'legalJustification': legalJustification, 'methodCollection': methodCollection}
    return JsonResponse(receipt, content_type='application/json')