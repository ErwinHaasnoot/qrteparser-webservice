# -*- coding: utf-8 -*-
from rexec import FileWrapper

import os
from uuid import UUID
from multiprocessing import Process

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpRequest, HttpResponse
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.utils.encoding import smart_str

from qparser.models import DataFile
from qparser.forms import DataFileForm
from qrte_parser_python import QRTEParserLogger, QRTEParser, QRTEParserException
from qrteparser import settings


def index(request):
    # Handle file upload
    if request.method == 'POST':
        form = DataFileForm(request.POST, request.FILES)
        if form.is_valid():

            name = request.FILES['datafile']._name
            print(HttpRequest.get_host(request))

            newdoc = DataFile(
                name_in=name,
                name_out = DataFile.generate_filename(name,postfix='_out',file_type='csv'),
                name_log = DataFile.generate_filename(name, file_type='log'),
                file_type = name.split('.')[-1],
                datafile=request.FILES['datafile'],
                processed=False,
                email=request.POST['email'],
                    send_log=False,
                    host_name=HttpRequest.get_host(request)
            )
            newdoc.save()
            p = Process(target=ParseUploadedFile, args=(newdoc.pk,))
            p.start()

            # Redirect to the document list after POST

            return render_to_response(
                    'qparser/thanks.html'
            )
    else:
        form = DataFileForm()  # A empty, unbound form

    # Render list page with the documents and the form
    return render_to_response(
            'qparser/index.html',
            context=RequestContext(request, {'form': form})
    )


def download(request):
    if 'uuid' not in request.GET:
        return render_to_response('qparser/couldnotfindfile.html', status=404)
    try:
        UUID(request.GET['uuid'])
    except ValueError as e:
        return render_to_response('qparser/couldnotfindfile.html', status=404)

    df = DataFile.objects.get(download_uuid=UUID(request.GET['uuid']))
    if df is not None:
        print(df.host_name)
        return HttpResponse(get_template('qparser/download.html').render({
            'download_file_url': reverse(download_file) + '?uuid=' + str(df.download_uuid)
        }))
    else:
        return render_to_response('qparser/couldnotfindfile.html', status=404)


def download_file(request):
    if 'uuid' not in request.GET:
        return render_to_response('qparser/couldnotfindfile.html', status=404)
    try:
        UUID(request.GET['uuid'])
    except ValueError as e:
        return render_to_response('qparser/couldnotfindfile.html', status=404)
    df = DataFile.objects.get(download_uuid=UUID(request.GET['uuid']))
    if df is not None:
        filepath = settings.FILES_OUT + df.name_system + '.csv.gz'
        print(filepath)
        wrapper = FileWrapper(file(filepath))
        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(df.name_out + '.gz')
        response['Content-Length'] = os.path.getsize(filepath)

        return response
    else:
        return render_to_response('qparser/couldnotfindfile.html', status=404)


def download_log(request):
    if 'uuid' not in request.GET:
        return render_to_response('qparser/couldnotfindfile.html', status=404)
    try:
        UUID(request.GET['uuid'])
    except ValueError as e:
        return render_to_response('qparser/couldnotfindfile.html', status=404)
    df = DataFile.objects.get(download_uuid=UUID(request.GET['uuid']))
    if df is not None:
        with open(settings.FILES_LOG + df.name_system + '.log') as f:

            return HttpResponse(f)
    else:
        return render_to_response('qparser/couldnotfindfile.html', status=404)


def ParseUploadedFile(datafile_pk):
    """
    Parses the file indicated by the primary key. Emails an error reporting as well.
    :param datafile_pk:
    :return:
    """
    datafile = DataFile.objects.get(pk=datafile_pk)
    QRTEParserLogger.LISTENING_THRESHOLD = 3

    input_file = "%s%s.%s" % (settings.FILES_IN, datafile.name_system, datafile.file_type)
    log_file = settings.FILES_LOG + datafile.name_system + '.log'

    print("Running parser on file: %s" % input_file)

    # Set stdout & err to log file
    f = open(log_file, 'w')
    QRTEParserLogger.OUT = f
    result = None
    try:
        # Try parsing the file
        input_file = "%s%s.%s" % (settings.FILES_IN, datafile.name_system, datafile.file_type)
        output_file = settings.FILES_OUT + datafile.name_system + '.csv'
        result = QRTEParser.parse(file=input_file, outfile=output_file, entrance='WEB')

        # Send out email notifying researcher that Parsing was completed.
        tpl = get_template('email/success.html')
        send_mail(datafile.email, '[QRTEParser] Successfully parsed %s' % datafile.name_in, tpl.render({
            'download_url': datafile.host_name + reverse(download) + '?uuid=' + str(datafile.download_uuid),
            'log_url': datafile.host_name + reverse(download_log) + '?uuid=' + str(datafile.download_uuid),
            'report_mail': settings.EMAIL_SENDER,
            'filename': datafile.name_in
        }
        ))

        # Update database with success/fail report.
        f.close()
    except QRTEParserException as e:
        # Handle caught QRTEParserException

        # Send email that QRTEParser ran into known exception.

        tpl = get_template('email/fail.html')
        send_mail(datafile.email, '[QRTEParser] Failed to parse %s' % datafile.name_in, tpl.render({
            'error_string': str(e),
            'log_url': datafile.host_name + reverse(download_log) + '?uuid=' + str(datafile.download_uuid),
            'report_mail': settings.EMAIL_SENDER,
            'filename': datafile.name_in
        }
        ))

        # Update database with fail report
        print(e)
        f.close()
        raise e
        pass
    except Exception as e:
        # Handle unknown exception

        # Send email that QRTEParser ran into unknown exception. Also send to support@qrtengine.com

        tpl = get_template('email/fail.html')
        send_mail(datafile.email, '[QRTEParser] Failed to parse %s' % datafile.name_in, tpl.render({
            'error_string': str(e),
            'log_url': datafile.host_name + reverse(download_log) + '?uuid=' + str(datafile.download_uuid),
            'report_mail': settings.EMAIL_SENDER,
            'filename': datafile.name_in
        }
        ))

        # Update database with fail report
        print(e)
        f.close()
        raise e
        pass

    print("Parsing finished with output file: %s" % output_file)
    f.close()

    pass


def send_mail(address, title, body):
    import sendgrid

    sg = sendgrid.SendGridClient(settings.EMAIL_API_KEY)

    message = sendgrid.Mail()
    message.add_to(address)
    message.set_subject(title)
    message.set_text(body)
    message.set_from('QRTEngine Support <support@qrtengine.com>')
    status, msg = sg.send(message)
    pass
