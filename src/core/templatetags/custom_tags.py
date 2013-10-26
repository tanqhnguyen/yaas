from django import template
register = template.Library()

@register.inclusion_tag('common/auction_list_entry.html')
def auction_list_entry(auction):
    return {'auction': auction}

@register.filter(name="format_bid_amount")
def format_bid_amount(value):
    return "{:.2f}".format(value)

@register.filter(name="format_date")
def format_date(value):
    return value.strftime("%Y-%m-%d %H:%M:%S")