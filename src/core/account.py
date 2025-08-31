from datetime import datetime
from src.core.transaction import Transaction


class Account:
    def __init__(self, account_type, balance=0, overdraft_limit=0, nickname=None):
        self.account_type = account_type
        self.balance = balance
        self.overdraft_limit = overdraft_limit
        self.nickname = nickname
        self.transactions = []
        self.created_date = datetime.now()
        self.last_activity = datetime.now()

    def update_nickname(self, nickname):
        """Update the account nickname"""
        self.nickname = nickname
        self.update_activity()

    def get_display_name(self):
        """Get display name for the account (nickname if available, otherwise account type)"""
        if self.nickname:
            return f"{self.nickname} ({self.account_type})"
        return self.account_type.capitalize()

    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = datetime.now()

    def deposit(self, amount):
        if amount <= 0:
            print("Error: Deposit amount must be positive.")
            return
        self.balance += amount
        self.transactions.append(Transaction(amount, 'deposit'))
        self.update_activity()
        print(f"Deposit of ${amount} successful. New balance: ${self.balance}")

    def withdraw(self, amount):
        if amount <= 0:
            print("Error: Withdrawal amount must be positive.")
            return
        if self.account_type == 'current' and (self.balance - amount) < -self.overdraft_limit:
            print(f"Error: Overdraft limit exceeded. Withdrawal of ${amount} failed.")
        elif self.balance < amount:
            print(f"Error: Insufficient funds. Withdrawal of ${amount} failed.")
        else:
            self.balance -= amount
            self.transactions.append(Transaction(amount, 'withdrawal'))
            self.update_activity()
            print(f"Withdrawal of ${amount} successful. New balance: ${self.balance}")

    def add_interest(self, rate):
        if rate < 0:
            print(f"Error: Interest rate must be non-negative.")
            return
        if self.account_type in ['savings', 'salary']:
            interest = self.balance * rate
            self.balance += interest
            self.transactions.append(Transaction(interest, 'interest'))
            self.update_activity()
            print(f"Interest of ${interest} added successfully. New balance: ${self.balance}")

    def filter_transactions(self, transaction_type=None, start_date=None, end_date=None):
        filtered = self.transactions
        if transaction_type:
            filtered = [t for t in filtered if t.transaction_type == transaction_type]
        if start_date:
            filtered = [t for t in filtered if t.date >= start_date]
        if end_date:
            filtered = [t for t in filtered if t.date >= end_date]
        return filtered

    def sort_transactions(self, key, reverse=False):
        valid_keys = {"date": lambda t: t.date, "amount": lambda t: t.amount, "type": lambda t: t.transaction_type}
        if key not in valid_keys:
            print(f"Invalid sort key: {key}. Valid keys are 'date', 'amount', 'type'.")
            return self.transactions
        return sorted(self.transactions, key=valid_keys[key], reverse=reverse)

    def get_balance(self):
        return self.balance


class AccountManager:
    """Centralized account management operations"""
    
    def __init__(self, user):
        self.user = user

    def create_account_with_nickname(self, account_type, balance=0, overdraft_limit=0, nickname=None):
        """Create a new account with optional nickname"""
        # Validate account type
        valid_types = ['savings', 'current', 'salary']
        if account_type not in valid_types:
            raise ValueError(f"Invalid account type. Must be one of: {valid_types}")
        
        # Check if account type already exists
        existing_account = self.get_account_by_type(account_type)
        if existing_account:
            raise ValueError(f"Account of type '{account_type}' already exists")
        
        # Create new account
        account = Account(account_type, balance, overdraft_limit, nickname)
        self.user.add_account(account)
        return account

    def update_account_nickname(self, account_identifier, nickname):
        """Update account nickname by account type or existing nickname"""
        account = self.get_account_by_identifier(account_identifier)
        if not account:
            raise ValueError(f"Account '{account_identifier}' not found")
        
        account.update_nickname(nickname)
        return True

    def get_account_by_nickname(self, nickname):
        """Get account by nickname"""
        for account in self.user.accounts:
            if account.nickname and account.nickname.lower() == nickname.lower():
                return account
        return None

    def get_account_by_type(self, account_type):
        """Get account by type"""
        for account in self.user.accounts:
            if account.account_type == account_type:
                return account
        return None

    def get_account_by_identifier(self, identifier):
        """Get account by type or nickname"""
        # First try by nickname
        account = self.get_account_by_nickname(identifier)
        if account:
            return account
        
        # Then try by account type
        return self.get_account_by_type(identifier)

    def generate_account_summary(self):
        """Generate comprehensive account summary"""
        summary = {
            'total_accounts': len(self.user.accounts),
            'accounts': [],
            'total_balance': 0
        }
        
        for account in self.user.accounts:
            account_info = {
                'type': account.account_type,
                'nickname': account.nickname,
                'display_name': account.get_display_name(),
                'balance': account.balance,
                'overdraft_limit': account.overdraft_limit,
                'available_balance': account.balance + (account.overdraft_limit if account.account_type == 'current' else 0),
                'transaction_count': len(account.transactions),
                'created_date': account.created_date.strftime("%Y-%m-%d"),
                'last_activity': account.last_activity.strftime("%Y-%m-%d %H:%M:%S")
            }
            summary['accounts'].append(account_info)
            summary['total_balance'] += account.balance
        
        return summary

    def get_financial_overview(self):
        """Get financial overview across all accounts"""
        overview = {
            'total_balance': 0,
            'total_available': 0,
            'account_breakdown': {},
            'recent_activity': []
        }
        
        all_transactions = []
        
        for account in self.user.accounts:
            overview['total_balance'] += account.balance
            
            # Calculate available balance (including overdraft for current accounts)
            available = account.balance
            if account.account_type == 'current':
                available += account.overdraft_limit
            overview['total_available'] += available
            
            # Account breakdown
            overview['account_breakdown'][account.get_display_name()] = {
                'balance': account.balance,
                'available': available
            }
            
            # Collect recent transactions
            for transaction in account.transactions[-5:]:  # Last 5 transactions per account
                all_transactions.append({
                    'account': account.get_display_name(),
                    'amount': transaction.amount,
                    'type': transaction.transaction_type,
                    'date': transaction.date
                })
        
        # Sort by date and get most recent
        all_transactions.sort(key=lambda x: x['date'], reverse=True)
        overview['recent_activity'] = all_transactions[:10]  # Last 10 transactions overall
        
        return overview

    def list_accounts_with_nicknames(self):
        """List all accounts with their display names"""
        accounts_list = []
        for account in self.user.accounts:
            accounts_list.append({
                'type': account.account_type,
                'nickname': account.nickname,
                'display_name': account.get_display_name(),
                'balance': account.balance
            })
        return accounts_list