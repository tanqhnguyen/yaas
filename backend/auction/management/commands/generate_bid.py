from django.core.management.base import BaseCommand, CommandError
from core.models import User, Auction

class Command(BaseCommand):
    args = '<Number of bid>'
    help = 'Generate a bunch of bids'

    def handle(self, *args, **options):
        if len(args) == 0:
            count = 50
        else:
            count = args[0]

        for x in range(0, int(count)):
            auction = Auction.objects.order_by('?')[0]
            user = User.objects.order_by('?')[0]
            amount = auction.min_next_bid_amount()
            bid = auction.bid(amount=amount, user=user, skip_email=True)
            self.stdout.write("Create bid id %s" % bid.id)


