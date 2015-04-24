from django.db import models
from django.conf import settings
from multiprocessing import Pool
from qrte_parser_python import QRTEParser, QRTEParserException
import uuid

# Create your models here.

class DataFile(models.Model):
    """
        Contains reference to unprocessed files
    """
    ERR_CHOICES = (
        (QRTEParserException.ERR_UNKNOWN, 'ERR_UNKNOWN'),
        (QRTEParserException.ERR_NONE,'OK'),
    )
    
    name_in = models.TextField(help_text="Name of file as it was uploaded")
    name_out = models.TextField(help_text="Name of file as it will be downloaded")
    name_system = models.TextField(help_text="Name of file as it is known in system. RFC 4122 UUID", default=uuid.uuid4)
    
    email = models.TextField(help_text="Email address to which notification should be sent about finished File")
    
    processed = models.BooleanField(help_text="Processed yes/no",default=None)
    succeeded = models.NullBooleanField(help_text="Processing Successful yes/no",default=None)
    zipped_up = models.BooleanField(help_text="Uploaded file was zipped",default=None)
    zipped_down = models.BooleanField(help_text="Downloaded file should be zipped", default=None)
    
    send_log = models.BooleanField(help_text="Send log with e-mail true/false",default=True)

    parse_start = models.DateTimeField(null=True)
    parse_end = models.DateTimeField(null=True)
    
    error_code = models.IntegerField(help_text="Error code if Process unsuccesful",null=True, choices=ERR_CHOICES)
    error_msg = models.TextField(help_text="Short error msg if Process unsuccessful", null=True)
    eror_msg_verbose = models.TextField(help_text="Verbose error message if Process unsuccessful, log dump", null=True)

    def process(self):
        wp = settings['WORKER_POOL']

        assert isinstance(wp, Pool), "Incorrect settings"

        wp.apply_async(func=ParseUploadedFile, args=(self.pk,))

    def __unicode__(self):
        return "DataFile: "


def ParseUploadedFile(datafile_pk):
    datafile = DataFile.objects.get(pk=datafile_pk)

    pass
