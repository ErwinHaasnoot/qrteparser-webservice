# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from qparser.models import DataFile
from qparser.forms import DataFileForm


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DataFileForm(request.POST, request.FILES)
        if form.is_valid():
            print request.FILES['datafile'].__dict__

            newdoc = DataFile(
                name_in='',
                datafile=request.FILES['datafile'],
                processed=False,
                email=request.POST['email'],
                send_log=request.POST['send_log']
            )
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('qparser.views.list'))
    else:
        form = DataFileForm()  # A empty, unbound form

    # Load documents for the list page
    documents = DataFile.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )