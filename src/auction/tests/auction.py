from django.core.urlresolvers import reverse
from django.test import TestCase
from core.models import User, Auction
from datetime import datetime, timedelta

class AuctionTest(TestCase):
    fixtures = ['fixtures.json']

    def setUp(self):
        self.seller = User.objects.order_by('-id')[0]
        self.seller_password = "test_password_%s" % self.seller.email.split("@")[0].split('email')[1]
        self.client.login(username=self.seller.username, password=self.seller_password)

    def test_create_auction_without_login(self):
        self.client.logout()
        response = self.client.get(reverse('create_auction'))
        self.assertEquals(response.status_code, 302)

    def test_view_create_auction_after_login(self):
        response = self.client.get(reverse('create_auction'))
        self.assertEquals(response.status_code, 200)

    def test_normal_create_auction(self):
        initial_auction_count = Auction.objects.count()
        now = datetime.now()
        next_five_days = timedelta(days=5)
        deadline = now + next_five_days
        data = {
            'title': 'test_normal_create_auction',
            'deadline': deadline.strftime("%Y-%m-%d %H:%M:%S"),
            'description': 'Description',
            'min_price': 10.0
        }
        response = self.client.post(reverse('create_auction'), data)
        self.assertContains(response, u'Please confirm that you want to create this auction')
        self.assertEquals(initial_auction_count, Auction.objects.count())

    def test_invalid_create_auction(self):
        now = datetime.now()
        next_two_days = timedelta(days=2)
        deadline = now + next_two_days
        data = {
            'title': 'test_invalid_create_auction',
            'deadline': deadline.strftime("%Y-%m-%d %H:%M:%S"),
            'description': 'Description',
            'min_price': 0
        }
        response = self.client.post(reverse('create_auction'), data)
        self.assertContains(response, u'Must be greater than 0')
        self.assertContains(response, u'Deadline must be at least 72 hours from now')

    def test_confirm_create_auction(self):
        initial_auction_count = Auction.objects.count()
        now = datetime.now()
        next_five_days = timedelta(days=5)
        deadline = now + next_five_days
        data = {
            'title': 'test_confirm_create_auction',
            'deadline': deadline.strftime("%Y-%m-%d %H:%M:%S"),
            'description': 'Description',
            'min_price': 100,
            'confirm': 'yes'
        }
        response = self.client.post(reverse('confirm_auction'), data, follow=True)
        self.assertContains(response, u'Your auction has been created succesfully')
        self.assertEquals(initial_auction_count + 1, Auction.objects.count())
        new_auction = Auction.objects.filter(title__exact=data['title']).all()[0]
        self.assertEquals(new_auction.seller_id, self.seller.id)
        self.assertEquals(new_auction.min_next_bid_amount(), data['min_price'] + 0.01)

    def test_not_confirm_create_auction(self):
        initial_auction_count = Auction.objects.count()
        now = datetime.now()
        next_five_days = timedelta(days=5)
        deadline = now + next_five_days
        data = {
            'title': 'test_not_confirm_create_auction',
            'deadline': deadline.strftime("%Y-%m-%d %H:%M:%S"),
            'description': 'Description',
            'min_price': 100,
            'confirm': 'no'
        }
        response = self.client.post(reverse('confirm_auction'), data, follow=True)
        self.assertNotContains(response, u'Your auction has been created succesfully')
        self.assertEquals(initial_auction_count, Auction.objects.count())