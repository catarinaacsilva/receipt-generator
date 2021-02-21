from django.shortcuts import render
from .forms import ReceiptForm


def index(request):
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
