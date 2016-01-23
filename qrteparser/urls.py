from django.conf.urls import patterns, include, url
from django.contrib import admin
from qparser.views import index, download, download_file, download_log

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^download/file/', download_file, name='download_file'),
    url(r'^download/log/', download_log, name='download_log'),
    url(r'^download/', download, name='download'),
    url(r'', index, name='index'),

]
