from datetime import datetime


class Transaction:
    def __init__(self, amount, transaction_type, date=None):
        self.amount = amount
        self.transaction_type = transaction_type
        self.date = date if date else datetime.now()

    def __repr__(self):
        return f"Transaction(amount= {self.amount}, transaction_type={self.transaction_type}, date={self.date})"

    def to_dict(self):
        return {
            "amount": self.amount,
            "transaction": self.transaction_type,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S")
        }
