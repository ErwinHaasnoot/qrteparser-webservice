__author__ = 'erwin'

from django.conf import settings

def builSuccessReport(self, traceback=None):

    from django.template import Context
    from django.template.loader import get_template
    from django.core import urlresolvers


    scenario_url = '/admin/scenario/%s/' % self.pk
    message = get_template('emails/success.html').render(
        Context({
            'traceback': traceback or 'No traceback',
            'scenario': self.__class__.__name__,
            'scenario_url': settings.ADMIN_HOST + scenario_url,
            'message': self.message or 'No message',
        })
    )
    subject = '[QRTEParser][Finished][Success] %s' % (self.message)
    return {
        'subject': subject,
        'message': message
    }