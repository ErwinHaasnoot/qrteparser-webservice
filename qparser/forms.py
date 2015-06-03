from django import forms


class DataFileForm(forms.Form):
    email = forms.CharField(label='Your email address',
                            help_text="We will send you a link to the parsed data file when it's done.", max_length=200)
    datafile = forms.FileField()

