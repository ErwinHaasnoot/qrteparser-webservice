from django.db import models
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import Template
from multiprocessing import Process
from django.core.urlresolvers import reverse

from django.template.loader import get_template
from qrte_parser_python import QRTEParserException
import uuid


def upload_to_fn(instance, old_filename):
    return settings.FILES_IN + DataFile.generate_filename(
            instance.name_system,
            file_type=instance.file_type)


def generate_uuid():
    return str(uuid.uuid4())

class DataFile(models.Model):
    """
        Contains reference to unprocessed files
    """
    ERR_CHOICES = (
        (QRTEParserException.ERR_UNKNOWN, 'ERR_UNKNOWN'),
        (QRTEParserException.ERR_NONE, 'OK'),
    )
    name_in = models.TextField(help_text="Name of file as it was uploaded")
    name_out = models.TextField(help_text="Name of file as it will be downloaded")
    name_system = models.TextField(help_text="Name of file as it is known in system. RFC 4122 UUID",
                                   default=generate_uuid)

    name_log = models.TextField(help_text="Location of log file as it is known in system")

    download_uuid = models.UUIDField(help_text="Name of file as it can be downloaded", db_index=True,
                                     default=uuid.uuid4)

    file_type = models.TextField(help_text="Filetype of file", default="csv")

    datafile = models.FileField(upload_to=upload_to_fn)

    email = models.TextField(help_text="Email address to do which notification should be sent about finished File")

    processed = models.BooleanField(help_text="Processed yes/no", default=None)
    succeeded = models.NullBooleanField(help_text="Processing Successful yes/no", default=None)

    opt_skip_error = models.BooleanField(help_text="Skip QRTEParser exceptions if thrown", default=True)

    send_log = models.BooleanField(help_text="Send log with e-mail true/false", default=None)

    parse_start = models.DateTimeField(help_text="Parse started at this time", null=True, default=None)
    parse_end = models.DateTimeField(help_text="Parse ended at this time", null=True, default=None)
    parse_duration = models.DateTimeField(help_text="Parse duration", null=True, default=None)

    error_code = models.IntegerField(help_text="Error code if Process unsuccessful", null=True, choices=ERR_CHOICES,
                                     default=None)
    error_msg = models.TextField(help_text="Short error msg if Process unsuccessful", null=True, default=None)
    error_msg_verbose = models.TextField(help_text="Verbose error message if Process unsuccessful, log dump", null=True,
                                         default=None)

    host_name = models.TextField(default=None)


    def __unicode__(self):
        """
        Output unicode filetype
        :return:
        """
        return "DataFile: %s" % self.name_in

    @classmethod
    def generate_filename(cls, filename, postfix=None, file_type=None):
        """
        Generates out name based on input name and given options.
        :param filename: base filename
        :param postfix: Intended postfix to the string
        :param file_type: Output type of filename, if left empty will not change
        :return: intended output filename
        """

        # Sanitize input
        assert isinstance(filename, basestring), "filename must be string"
        assert postfix is None or isinstance(postfix, basestring), "postfix must be string or None"
        assert file_type is None or isinstance(file_type, basestring), "file_type must be string or None"

        tokens = filename.split('.')

        if len(tokens) == 1 and file_type is not None:
            tokens.append(file_type)
        assert len(tokens) >= 2, "%s must be valid filename with filetype indicator (<name>.<type>)" % filename

        if file_type is not None:
            tokens[-1] = file_type
        if postfix is not None:
            tokens[-2] += postfix

        return '.'.join(tokens)

