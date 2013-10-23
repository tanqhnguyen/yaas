from django.conf.urls import patterns, include, url

from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^backend/', include('backend.foo.urls')),
    url(r'^$', 'core.views.index', name='index'),
    url(r'^register$', 'authentication.views.register', name='register'),
    url(r'^login$', login, {'template_name': 'authentication/login.html'}),
    url(r'^logout$', logout, {'next_page': '/'}),
    url(r'^set-language/(?P<language>[a-z]{2,4})$', 'core.views.set_language', name='set_language'),

    url(r'^account/', include('account.urls')),
    url(r'^auction/', include('auction.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
