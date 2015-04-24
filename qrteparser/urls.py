from django.conf.urls import patterns, include, url
from django.contrib import admin
from qparser.views import upload_file

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'qrteparser.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload_file',upload_file),
)
