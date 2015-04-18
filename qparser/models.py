from django.db import models

# Create your models here.

class DataFile(models.Model):
    """
        Contains reference to unprocessed files
    """
    
    ERR_UNKNOWN = -1
    ERR_NONE = 0
    
    ERR_CHOICES = (
        (ERR_UNKNOWN, 'ERR_UNKNOWN'),
        (ERR_NONE,'OK'),
    )
    
    name_in = models.TextField(help_text="Name of file as it was uploaded")
    name_out = models.TextField(help_text="Name of file as it will be downloaded")
    name_system = models.TextField(help_text="Name of file as it is known in system")
    
    email = models.TextField(help_text="Email address to which notification should be sent about finished File")
    
    processed = models.BooleanField(help_text="Processed yes/no",default=None)
    succeeded = models.NullBooleanField(help_text="Processing Successful yes/no",default=None)
    zipped = models.BooleanField(help_text="Uploaded file was zipped",default=None)
    
    error_code = models.IntegerField(help_text="Error code if Process unsuccesful",null=True, choices=ERR_CHOICES)
    error_msg = models.TextField(help_text="Short error msg if Process unsuccessful")
    eror_msg_verbose = models.TextField(help_text="Verbose error message if Process unsuccessful")