from django.conf.urls import patterns, url

from api import views

urlpatterns = patterns('',
    url(r'bid', views.BidView.as_view(), name='api_bid_auction'),
    url(r'search', views.SearchView.as_view(), name='api_search_auction'),
)