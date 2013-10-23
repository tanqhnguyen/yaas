from django.core.mail import EmailMessage

def send(**kwargs):
    _kwargs = kwargs
    _kwargs['from_email'] = "admin@yaas.local"

    email = EmailMessage(**_kwargs)
    email.send()