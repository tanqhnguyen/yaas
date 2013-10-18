from django.conf.urls import patterns, url

from auction import views

urlpatterns = patterns('',
    url(r'update/(?P<auction_id>\d+)', views.UpdateView.as_view(), name='update_auction'),
    url(r'bid/(?P<auction_id>\d+)', views.BidView.as_view(), name='bid_auction'),
    url(r'create', views.CreateView.as_view(), name='create_auction'),
    url(r'confirm', views.ConfirmView.as_view(), name='confirm_auction'),
    url(r'search', views.SearchView.as_view(), name='search_auction'),
    url(r'(?P<auction_id>\d+)', views.DetailView.as_view(), name='view_auction'),
)