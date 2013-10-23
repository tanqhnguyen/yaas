from celery import task

@task()
def auction_end(auction):
    auction.end()