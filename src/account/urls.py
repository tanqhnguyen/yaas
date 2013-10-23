from django.conf.urls import patterns, url

from account import views

urlpatterns = patterns('',
    url(r'profile', views.ProfileView.as_view()),
    url(r'update', views.UpdateView.as_view(), name='update_profile')
)