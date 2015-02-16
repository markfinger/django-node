from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'djangosite.views.hello_world', name='hello_world'),

    url(r'^admin/', include(admin.site.urls)),
)
