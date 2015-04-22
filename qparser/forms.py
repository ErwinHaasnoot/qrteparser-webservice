from django import forms

class UploadFileForm(forms.Form):
    email = forms.CharField(label='Your email address', max_length=200)
    file = forms.FileField()