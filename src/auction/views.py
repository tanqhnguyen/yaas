from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from forms import CreateForm
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from core.models import Auction
from core.exceptions import InvalidBid
from decorators import pre_process_auction


class CreateView(View):
    template_name = 'auction/create.html'
    confirm_template_name = 'auction/confirm.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get(self, request):
        context = {}
        form = CreateForm()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        form = CreateForm(request.POST)
        context['form'] = form

        if not form.is_valid():
            return render(request, self.template_name, context)

        return render(request, self.confirm_template_name, context)

class ConfirmView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request):
        confirm = request.POST['confirm']

        if confirm == 'yes':
            form = CreateForm(request.POST)
            if not form.is_valid():
                return redirect('create_auction')

            auction = form.save(commit=False)
            auction.seller = request.user
            auction.status = Auction.ACTIVE
            auction.save()
            auction.start_timer()
            messages.success(request, _('Your auction has been created succesfully'))
            auction.send_create_mail()

        return redirect('/')

class DetailView(View):
    template_name = 'auction/view.html'

    @method_decorator(pre_process_auction(only_seller=False))
    def dispatch(self, *args, **kwargs):
        return super(DetailView, self).dispatch(*args, **kwargs)

    def get(self, request, auction_id):        
        auction = request.auction
        bids = auction.bids.order_by('-amount').all()

        context = {
            'auction': auction,
            'is_seller': auction.is_seller(request.user),
            'is_admin': request.user.is_superuser,
            'bids': bids,
            'is_finished': auction.status == Auction.FINISHED,
            'winner': auction.get_winner()
        }
        return render(request, self.template_name, context)

class UpdateView(View):
    template_name = 'auction/update.html'

    @method_decorator(login_required)
    @method_decorator(pre_process_auction(only_seller=True))
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    def get(self, request, auction_id):
        auction = self.request.auction
        context = {
            'auction': auction
        }
        return render(request, self.template_name, context)

    def post(self, request, auction_id):
        auction = self.request.auction

        description = request.POST.get('description')
        if len(description) == 0:
            description = auction.description
        auction.description = description
        auction.version += 1
        auction.save()

        return redirect(auction)

class SearchView(View):
    template_name = 'auction/search.html'

    def get(self, request):
        q = request.GET['q']
        auctions = Auction.objects.filter(title__contains=q).exclude(status=Auction.BANNED).exclude(status=Auction.INACTIVE).all()
        context = {
            'auctions': auctions,
            'q': q
        }
        return render(request, self.template_name, context)

class BidView(View):
    @method_decorator(login_required)
    @method_decorator(pre_process_auction(not_seller=True, not_finished=True))
    def dispatch(self, *args, **kwargs):
        return super(BidView, self).dispatch(*args, **kwargs)

    def get(self, request, auction_id):
        return redirect(request.auction)

    def post(self, request, auction_id):
        auction = self.request.auction
        amount = float(request.POST['amount'])
        version = int(request.POST['version'])
        bid_version = int(request.POST['bid_version'])

        if auction.status is Auction.FINISHED:
            messages.error(request, _('The auction has been finished'))
        elif version < auction.version:
            messages.warning(request, _('The auction description has been changed. Please review it'))
        elif bid_version < auction.bid_version:
            messages.warning(request, _('Someone has placed a bid before you. Please try again'))
        else:
            try:
                auction.bid(amount=amount, user=request.user)
                messages.success(request, _('Your bid has been placed successfully'))
            except InvalidBid, e:
                if e.reason:
                    messages.error(request, _(e.reason))
                else:    
                    messages.error(request, _('You must bid at least %(amount)s') % {'amount': e.amount})

        return redirect(auction)

class BanView(View):
    @method_decorator(login_required)
    @method_decorator(pre_process_auction(only_admin=True))
    def dispatch(self, *args, **kwargs):
        return super(BanView, self).dispatch(*args, **kwargs)

    def post(self, request, auction_id):
        auction = request.auction
        auction.ban()
        return redirect(auction)