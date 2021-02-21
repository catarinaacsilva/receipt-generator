from django import forms

class ReceiptForm(forms.Form):
    firstname= forms.CharField(max_length=100)
    lastname= forms.CharField(max_length=100)