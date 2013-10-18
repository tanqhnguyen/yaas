class InvalidBid(Exception):
    def __init__(self, amount=0, reason=None):
        self.amount = amount
        self.reason = reason
