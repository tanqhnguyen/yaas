class InvalidBid(Exception):
    def __init__(self, amount):
        self.amount = amount
