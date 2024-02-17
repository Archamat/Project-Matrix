# profiles/forms.py
 
from django import forms
 
# creating a form 
class InputForm(forms.Form):
 
    Name = forms.CharField(max_length = 100)
    Age = forms.IntegerField()
    Job = forms.CharField(max_length = 100)

   # password = forms.CharField(widget = forms.PasswordInput())


