from django.forms import ModelForm
from core.models import Auction

class CreateForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'min_price', 'deadline']