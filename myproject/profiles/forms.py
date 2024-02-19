# profiles/forms.py
 
from django import forms
 
# creating a form 
class InputForm(forms.Form):

    CATEGORY_CHOICES = (
        ('0','AI'),
        ('1','WEB'),   
    )
    Name = forms.CharField(max_length = 100)
    Age = forms.IntegerField()
    Job = forms.CharField(max_length = 100)
    Category = forms.ChoiceField(choices=CATEGORY_CHOICES)

   # password = forms.CharField(widget = forms.PasswordInput())


class ProjectFilterForm(forms.Form):
    CATEGORY_CHOICES = (
        ('2','ALL'),
        ('0','AI'),
        ('1','WEB'),
          
    )
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)