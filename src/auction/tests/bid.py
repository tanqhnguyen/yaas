from django.core.urlresolvers import reverse
from django.test import TestCase
from core.models import User, Auction
from datetime import datetime, timedelta

class BidTest(TestCase):
    fixtures = ['fixtures.json']

    def login_bidder(self, index):
        bidder = self.bidders[index]
        self.client.login(username=bidder['user'].username, password=bidder['password'])

    def setUp(self):
        self.seller = User.objects.order_by('-id')[0]
        self.seller_password = "test_password_%s" % self.seller.email.split("@")[0].split('email')[1]

        self.bidders = [
            {
                'user': User.objects.order_by('-id')[20],
                'password': "test_password_%s" % User.objects.order_by('-id')[20].email.split("@")[0].split('email')[1]
            },
            {
                'user': User.objects.order_by('-id')[10],
                'password': "test_password_%s" % User.objects.order_by('-id')[10].email.split("@")[0].split('email')[1]
            }
        ]

        now = datetime.now()
        next_five_days = timedelta(days=5)
        deadline = now + next_five_days
        data = {
            'title': 'test_bid_auction',
            'deadline': deadline.strftime("%Y-%m-%d %H:%M:%S"),
            'description': 'Description',
            'min_price': 100,
            'confirm': 'yes'
        }
        self.client.login(username=self.seller.username, password=self.seller_password)
        self.client.post(reverse('confirm_auction'), data, follow=True)
        self.auction = Auction.objects.filter(title__exact=data['title']).all()[0]

    def test_success_bid(self):
        bidder = self.bidders[0]
        self.client.login(username=bidder['user'].username, password=bidder['password'])
        data = {
            'auction_id': self.auction.id,
            'amount': 100.01,
            'version': self.auction.version,
            'bid_version': self.auction.bid_version
        }
        response = self.client.post(reverse('bid_auction', kwargs={'auction_id': data['auction_id']}), data, follow=True)
        self.assertContains(response, u'Your bid has been placed successfully')
        self.assertEquals(self.auction.bids.count(), 1)

    def test_invalid_bid_amount(self):
        self.login_bidder(0)
        data = {
            'auction_id': self.auction.id,
            'amount': 100.004,
            'version': self.auction.version,
            'bid_version': self.auction.bid_version
        }
        response = self.client.post(reverse('bid_auction', kwargs={'auction_id': data['auction_id']}), data, follow=True)
        self.assertContains(response, u'You must bid at least %(amount)s' % {'amount': self.auction.min_next_bid_amount()})
        self.assertEquals(self.auction.bids.count(), 0)

    def test_invalid_bidder(self):
        data = {
            'auction_id': self.auction.id,
            'amount': 100.10,
            'version': self.auction.version,
            'bid_version': self.auction.bid_version
        }
        response = self.client.post(reverse('bid_auction', kwargs={'auction_id': data['auction_id']}), data, follow=True)
        self.assertContains(response, u'Seller can not do this')
        self.assertEquals(self.auction.bids.count(), 0)

    def test_lower_bid_amount_than_previous_bidder(self):
        self.login_bidder(0)
        data = {
            'auction_id': self.auction.id,
            'amount': 110,
            'version': self.auction.version,
            'bid_version': self.auction.bid_version
        }
        self.client.post(reverse('bid_auction', kwargs={'auction_id': data['auction_id']}), data)
        self.login_bidder(1)
        data['bid_version'] = self.auction.bid_version+1
        data['amount'] = 100
        response = self.client.post(reverse('bid_auction', kwargs={'auction_id': data['auction_id']}), data, follow=True)
        self.assertContains(response, u'You must bid at least %(amount)s' % {'amount': self.auction.min_next_bid_amount()})
        self.assertEquals(self.auction.bids.count(), 1)

    def test_place_bid_finished_auction(self):
        self.login_bidder(0)

        data = {
            'auction_id': self.auction.id,
            'amount': 110,
            'version': self.auction.version,
            'bid_version': self.auction.bid_version
        }
        response = self.client.post(reverse('bid_auction', kwargs={'auction_id': data['auction_id']}), data, follow=True)

        self.auction.end()
        self.login_bidder(1)
        data['bid_version'] = self.auction.bid_version+1
        data['amount'] = 200
        response = self.client.post(reverse('bid_auction', kwargs={'auction_id': data['auction_id']}), data, follow=True)

        self.assertContains(response, u'The auction has been ended')
        self.assertEquals(self.auction.bids.count(), 1)