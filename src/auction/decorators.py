from core.models import Auction
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from core.utils import json_response

def json_error(error):
    return json_response({'error': error})

def handle_error(error, request, is_json):
    if (is_json):
        return json_error(error)
    else:
        messages.error(request, error)
        return redirect("/")

def pre_process_auction(only_seller = False, not_seller = False, only_admin = False, not_finished=False, is_json=False):
    def decorator(function):
        def inner(request, *args, **kwargs):
            auction_id = kwargs.get('auction_id')
            if not auction_id:
                auction_id = request.POST.get('auction_id')
            if not auction_id:
                auction_id = request.GET.get('auction_id')
            try:
                auction = Auction.objects.get(pk=auction_id)
                if auction.status == Auction.INACTIVE:
                    return handle_error(_('The auction is inactive'), request, is_json)

                if auction.status == Auction.BANNED:
                    return handle_error(_('The auction has been banned'), request, is_json)

                if not_finished and auction.status == Auction.FINISHED:
                    return handle_error(_('The auction has been ended'), request, is_json)

                if only_seller and not auction.is_seller(request.user):
                    return handle_error(_('Invalid request'), request, is_json)

                if not_seller and auction.is_seller(request.user):
                    return handle_error(_('Seller can not do this action'), request, is_json)

                if only_admin and not request.user.is_superuser:
                    return handle_error(_('Only admin can do this action'), request, is_json)

                request.auction = auction
            except ObjectDoesNotExist:
                return handle_error(_('Invalid auction'), request, is_json)
            return function(request, *args, **kwargs)
        return inner
    return decorator