from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from auction.tasks import auction_end
import validators
from datetime import datetime
import pytz
import math
from core import mails
from exceptions import InvalidBid
from celery.task.control import revoke
from django.core.exceptions import ObjectDoesNotExist

class Auction(models.Model):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    FINISHED = 'finished'
    BANNED = 'banned'

    title = models.CharField(_("Title"), max_length=100)
    description = models.TextField(_("Description"))
    seller = models.ForeignKey(User, related_name="auctions")
    min_price = models.FloatField(_("Start price"), validators=[validators.validate_positive_number])
    deadline = models.DateTimeField(validators=[validators.validate_auction_deadline])
    status = models.CharField(max_length=32, default=INACTIVE)
    version = models.IntegerField(default=0)
    bid_version = models.IntegerField(default=0)
    task_id = models.CharField(max_length=36, default='')

    def get_absolute_url(self):
        return reverse('view_auction', kwargs={'auction_id': self.id})

    def is_seller(self, user):
        return self.seller_id == user.id

    def send_create_mail(self):
        kwargs = {
            'subject': _("Auction created"),
            'body': _("Your auction has been created"),
            'to': [self.seller.email]
        }
        mails.send(**kwargs)
        return self

    def cancel_task(self):
        revoke(self.task_id, terminate=True)

    def start_timer(self):
        time_left = self.calculate_time_left()
        time_left = 30
        task = auction_end.apply_async((self,), countdown=time_left)
        self.task_id = task.id
        self.save()

    def end(self):
        if self.status != Auction.ACTIVE:
            return self
        
        current_highest_bid = self.current_highest_bid()
        if current_highest_bid:
            current_highest_bid.is_won = True
            current_highest_bid.save()

        self.status = Auction.FINISHED
        self.save()

        kwargs = {
            'subject': _("The auction has been resolved"),
            'body': _("The auction \"%(title)s\" has been resolved." % {'title': self.title})
        }
        emails = set([bid.user.email for bid in self.bids.all()])

        emails.add(self.seller.email)

        for email in emails:
            kwargs['to'] = [email]
            mails.send(**kwargs)

        return self

    def get_winner(self):
        if self.bids.count() == 0:
            return None

        filter_set = self.bids.filter(is_won=True)
        print filter_set.count()
        if filter_set.count() > 0:
            return filter_set.all()[0].user

        return None

    def calculate_time_left(self):
        deadline_in_s = self.deadline
        now = datetime.now(pytz.utc)
        deadline_in_s = deadline_in_s - now
        return int(math.floor(deadline_in_s.total_seconds()))

    def current_highest_bid(self):
        if self.bids.count() == 0:
            return None
        return Bid.objects.filter(auction_id=self.id).order_by('-amount')[0]

    def min_next_bid_amount(self):
        current_highest_bid = self.current_highest_bid()
        highest = self.min_price
        if current_highest_bid:
            highest = current_highest_bid.amount
        return highest + 0.01

    def bid(self, amount, user):
        kwargs = {
            'subject': _("New bid"),
            'body': _("New bid has been placed")
        }

        if self.status != Auction.ACTIVE:
            raise InvalidBid(reason='Auction is not available for bidding')

        # get the current highest bid
        current_highest_bid = self.current_highest_bid()
        amount = float(amount)
        if current_highest_bid and amount < current_highest_bid.amount:
            raise InvalidBid(amount=self.min_next_bid_amount())

        if self.min_price > amount:
            raise InvalidBid(amount=self.min_next_bid_amount())

        if current_highest_bid and round(amount - current_highest_bid.amount, 2)< 0.01:
            raise InvalidBid(amount=self.min_next_bid_amount())

        # gets the previous bidder if any
        try:
            previous_bid = Bid.objects.filter(amount__lt=amount).exclude(user=user).all()[:1].get()
            if previous_bid:
                kwargs['to'] = [previous_bid.user.email]
                mails.send(**kwargs)
        except ObjectDoesNotExist:
            pass

        bid = Bid()
        bid.auction_id = self.id
        bid.user_id = user.id
        bid.amount = amount
        self.bid_version += 1
        self.save()
        bid.save()

        kwargs['to'] = [self.seller.email]
        mails.send(**kwargs)
        kwargs['to'] = [bid.user.email]
        mails.send(**kwargs)

        return bid

    def ban(self):
        if self.statis == Auction.BANNED:
            return self

        self.status = Auction.BANNED
        self.cancel_task()
        self.save()

        kwargs = {
            'subject': _("Auction has been banned"),
            'body': _("Auction %(title)s has been banned" % {'title': self.title})
        }

        emails = [bid.user.email for bid in self.bids.all()]
        emails = set(emails)
        emails.add(self.seller.email)
        for email in emails:
            kwargs['to'] = [email]
            mails.send(**kwargs)

        return self

class Bid(models.Model):
    amount = models.FloatField(_("Amount"), validators=[validators.validate_positive_number])
    user = models.ForeignKey(User, related_name="bids")
    auction = models.ForeignKey(Auction, related_name="bids")
    is_won = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=datetime.now(pytz.utc))
