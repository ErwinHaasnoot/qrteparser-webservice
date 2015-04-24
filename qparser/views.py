from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from .models import DataFile
from .forms import UploadFileForm
# Create your views here.

# Imaginary function to handle an uploaded file.

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render_to_response('datafile/upload.html', {'form': form})
    
    
def handle_uploaded_file(file):

    datafile = DataFile(
        name_in = 'Blaat',
        name_out = 'Bloot',
        email='erwinhaasnoot@gmail.com',

    )
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
