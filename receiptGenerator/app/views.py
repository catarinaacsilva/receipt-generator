from django.shortcuts import render
from .forms import ReceiptForm
from django.http import JsonResponse

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
    firstName = request.GET['firstName']
    receipt = {'firstName': firstName}
    return JsonResponse(receipt, content_type='application/json')