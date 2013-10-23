from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
import math

def validate_auction_deadline(value):
    deadline = value
    deadline = deadline.replace(tzinfo=None)
    now = datetime.utcnow()
    delta = deadline - now
    min_duration = 259200 # 72 hours
    if not math.ceil(delta.total_seconds()) > 0:
        raise  ValidationError(_('Deadline must be in the future'))

    if math.floor(delta.total_seconds()) < min_duration:
        raise  ValidationError(_('Deadline must be at least 72 hours from now'))        

def validate_positive_number(value):
    if not value > 0:
        raise  ValidationError(_('Must be greater than 0'))        