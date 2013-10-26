from core.models import Auction
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

def pre_process_auction(only_seller = False, not_seller = False, only_admin = False, not_finished=False):
    def decorator(function):
        def inner(request, *args, **kwargs):
            auction_id = kwargs.get('auction_id')
            try:
                auction = Auction.objects.get(pk=auction_id)
                if auction.status == Auction.INACTIVE:
                    messages.error(request, _('The auction is inactive'))
                    return redirect("/")

                if auction.status == Auction.BANNED:
                    messages.error(request, _('The auction has been banned'))
                    return redirect("/")

                if not_finished and auction.status == Auction.FINISHED:
                    messages.error(request, _('The auction has been ended'))
                    return redirect("/")

                if only_seller and not auction.is_seller(request.user):
                    messages.error(request, _("Invalid request"))
                    return redirect("/")

                if not_seller and auction.is_seller(request.user):
                    messages.error(request, _("Seller can not do this"))
                    return redirect("/")

                if only_admin and not request.user.is_superuser:
                    messages.error(request, _("Only admin can do this action"))
                    return redirect("/")

                request.auction = auction
            except ObjectDoesNotExist:
                messages.error(request, _('Invalid auction'))
                return redirect("/")
            return function(request, *args, **kwargs)
        return inner
    return decorator