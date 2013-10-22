from django.core.management.base import BaseCommand, CommandError
from auction.forms import CreateForm
from core.models import User, Auction
import random

class Command(BaseCommand):
    args = '<Number of auction>'
    help = 'Generate a bunch of auctions'

    def handle(self, *args, **options):
        if len(args) == 0:
            count = 50
        else:
            count = args[0]
        for x in range(0, int(count)):
            data = {
                'title': 'Test auction %s' % x,
                'description': 'This is a test description for auction %s' % x,
                'min_price': random.randint(10, 200),
                'deadline': '2014-01-31 23:25:17'
            }
            form = CreateForm(data)
            if form.is_valid():
                auction = form.save(commit=False)
                auction.seller = User.objects.order_by("?")[0]
                auction.status = Auction.ACTIVE
                auction.save()
                self.stdout.write("Create auction id %s" % auction.id)
            else:
                print form.errors
                self.stdout.write(form.errors)


