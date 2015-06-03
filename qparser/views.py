# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from qparser.models import DataFile
from qparser.forms import DataFileForm


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DataFileForm(request.POST, request.FILES)
        if form.is_valid():

            name = request.FILES['datafile']._name

            newdoc = DataFile(
                name_in=name,
                name_out = DataFile.generate_filename(name,postfix='_out',file_type='csv'),
                name_log = DataFile.generate_filename(name, file_type='log'),
                file_type = name.split('.')[-1],
                datafile=request.FILES['datafile'],
                processed=False,
                email=request.POST['email'],
                send_log=False
            )
            newdoc.save()

            newdoc.process()

            # Redirect to the document list after POST

            return HttpResponseRedirect(reverse('qparser.views.list'))
    else:
        form = DataFileForm()  # A empty, unbound form

    # Load documents for the list page
    documents = DataFile.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'qparser/list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )

def download_file(request, uuid = None):
    if file is None:
        return Http404()


    if file is None:
        return Http404()

def download_log(request, uuid = None):
    if file is None:
        return Http404()


    if file is None:
        return Http404()

