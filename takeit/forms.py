from django import forms
 
 
class SubinfoForm(forms.Form):
    Name    = forms.CharField(max_length=100)
    Age     = forms.CharField(max_length=100)
    Gender  = forms.CharField(max_length=100)
    UHID    = forms.CharField(max_length=100)

