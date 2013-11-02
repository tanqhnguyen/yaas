from django.core.urlresolvers import reverse
from django.test import TestCase
from core.models import User, Auction
import json

class ApiTest(TestCase):
    fixtures = ['fixtures.json']

    def setUp(self):
        self.user = User.objects.order_by('-id')[0]
        self.user_password = "test_password_%s" % self.user.email.split("@")[0].split('email')[1]
        self.auction = Auction.objects.exclude(seller_id=self.user.id).order_by('-id')[0]

    def test_success_bid_api(self):
        initial_count = self.auction.bids.count()
        data = {
            'auction_id': self.auction.id,
            'amount': 400
        }
        response = self.client.post(reverse('api_bid_auction'), data, YAAS_USER=self.user.username, YAAS_USER_PASS=self.user_password)
        self.assertEquals(self.auction.current_highest_bid().amount, data['amount'])
        self.assertEquals(self.auction.bids.count(), initial_count + 1)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEquals(json_response['data']['id'], self.auction.id)

    def test_invalid_account_bid_api(self):
        initial_count = self.auction.bids.count()
        data = {
            'auction_id': self.auction.id,
            'amount': 400,
            'username': self.user.username,
            'password': 'wrong_password'
        }
        response = self.client.post(reverse('api_bid_auction'), data)
        self.assertEquals(self.auction.bids.count(), initial_count)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEquals(json_response['error'], 'Invalid account')