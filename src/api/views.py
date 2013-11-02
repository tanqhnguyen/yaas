from django.views.generic.base import View
from core.models import Auction
from auction.decorators import pre_process_auction
from django.utils.decorators import method_decorator
from decorators import api_authentication
from django.utils.translation import ugettext as _
from core.exceptions import InvalidBid
from core.utils import json_response
from django.views.decorators.csrf import csrf_exempt

class ApiView(View):
    def json(self, data):
        return json_response(data)

class SearchView(ApiView):
    def get(self, request):
        q = request.GET.get('query')
        if q is None:
            q = ''
        auctions = Auction.search(q)
        auctions = [auction.toJSON() for auction in auctions]
        json_data = {
            'data': auctions
        }
        return self.json(json_data)

class BidView(ApiView):
    @csrf_exempt
    @method_decorator(api_authentication())
    @method_decorator(pre_process_auction(not_seller=True, not_finished=True, is_json=True))
    def dispatch(self, *args, **kwargs):
        return super(BidView, self).dispatch(*args, **kwargs)

    def post(self, request):
        auction = self.request.auction
        amount = float(request.POST['amount'])

        if auction.status is Auction.FINISHED:
            return self.json({'error': _('The auction has been finished')})
        else:
            try:
                auction.bid(amount=amount, user=request.user)
                return self.json({'data': auction.toJSON()})
            except InvalidBid, e:
                if e.reason:
                    return self.json({'error': _(e.reason)})
                else:    
                    return self.json({'error': _('You must bid at least %(amount)s') % {'amount': e.amount}})