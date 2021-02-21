from django.shortcuts import render
from .forms import ReceiptForm
from django.http import JsonResponse


def index(request):
    return render(request, 'index.html')

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


def receiptGenerator(request):
    firstName = request.GET['firstName']
    receipt = {'firstName': firstName}
    return JsonResponse(receipt, content_type='application/json')