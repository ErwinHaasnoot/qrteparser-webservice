from django.conf.urls import patterns, include, url
from django.contrib import admin
from qparser.views import list

urlpatterns = patterns('qparser.views',
    # Examples:
    # url(r'^$', 'qrteparser.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^list/$', 'list', name='list'),
)
