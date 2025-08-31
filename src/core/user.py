import re
from src.core.account import Account, AccountManager
from src.utils.security_utils import PasswordSecurity
from src.managers.transfer_manager import TransferManager
from src.managers.transaction_manager import TransactionManager


class User:
    def __init__(self, username, password, email, is_hashed=False):
        self.username = username
        # Hash password if it's not already hashed
        if is_hashed:
            self.password = password
        else:
            self.password = PasswordSecurity.hash_password(password)
        self.email = email
        self.accounts = []
        self.account_manager = AccountManager(self)
        self.transfer_manager = TransferManager(self)
        self.transaction_manager = TransactionManager(self)

    def check_password(self, password):
        return PasswordSecurity.verify_password(password, self.password)

    def set_password(self, new_password):
        self.password = PasswordSecurity.hash_password(new_password)

    def add_account(self, account):
        self.accounts.append(account)
        print(f"{account.account_type.capitalize()} account added successfully")

    def get_account(self, account_identifier):
        """Get account by type or nickname"""
        # First try by account type
        for account in self.accounts:
            if account.account_type == account_identifier:
                return account
        
        # Then try by nickname
        for account in self.accounts:
            if account.nickname and account.nickname.lower() == account_identifier.lower():
                return account
        
        print(f"Error: Account '{account_identifier}' not found.")
        return None

    def get_accounts_summary(self):
        """Get basic accounts summary (backward compatibility)"""
        summary = {}
        for account in self.accounts:
            key = account.get_display_name()
            summary[key] = account.get_balance()
        return summary

    def create_account_with_nickname(self, account_type, balance=0, overdraft_limit=0, nickname=None):
        """Create account with optional nickname using AccountManager"""
        return self.account_manager.create_account_with_nickname(account_type, balance, overdraft_limit, nickname)

    def update_account_nickname(self, account_identifier, nickname):
        """Update account nickname"""
        return self.account_manager.update_account_nickname(account_identifier, nickname)

    def get_account_by_nickname(self, nickname):
        """Get account by nickname"""
        return self.account_manager.get_account_by_nickname(nickname)

    def get_enhanced_summary(self):
        """Get enhanced account summary with all details"""
        return self.account_manager.generate_account_summary()

    def get_financial_overview(self):
        """Get comprehensive financial overview"""
        return self.account_manager.get_financial_overview()

    def transfer_between_accounts(self, from_account, to_account, amount, memo=None):
        """Transfer money between user's accounts"""
        return self.transfer_manager.execute_transfer(from_account, to_account, amount, memo)

    def validate_transfer(self, from_account, to_account, amount):
        """Validate transfer between accounts"""
        return self.transfer_manager.validate_transfer(from_account, to_account, amount)

    def get_transfer_history(self, account=None):
        """Get transfer history for all accounts or specific account"""
        return self.transfer_manager.get_transfer_history(account)

    def get_transfer_by_id(self, transfer_id):
        """Get transfer details by transfer ID"""
        return self.transfer_manager.get_transfer_by_id(transfer_id)

    def get_transaction_history(self, account=None, start_date=None, end_date=None, page=1, page_size=50):
        """Get transaction history with filtering and pagination"""
        return self.transaction_manager.get_transaction_history(account, start_date, end_date, page, page_size)

    def filter_transactions(self, transactions, filters):
        """Apply filters to transaction list"""
        return self.transaction_manager.filter_transactions(transactions, filters)

    def get_transaction_summary(self, account=None, start_date=None, end_date=None):
        """Get transaction summary statistics"""
        return self.transaction_manager.get_transaction_summary(account, start_date, end_date)

    def export_transactions(self, transactions, format='csv'):
        """Export transactions to specified format"""
        return self.transaction_manager.export_transactions(transactions, format)

def register_user(users, username, password, email):
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        print("Error: Username can only contain letters, numbers, and underscore")
        return False

    if len(password) < 8:
        print("Error: Password must be at least 8 characters long.")
        return False
    
    # Enhanced password validation
    if not re.search(r"[A-Z]", password):
        print("Error: Password must contain at least one uppercase letter.")
        return False
    
    if not re.search(r"[a-z]", password):
        print("Error: Password must contain at least one lowercase letter.")
        return False
    
    if not re.search(r"\d", password):
        print("Error: Password must contain at least one number.")
        return False

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("Error: Invalid email address.")
        return False

    if username in users:
        print("Error: Username already taken.")
        return False
    else:
        users[username] = User(username, password, email)
        print("User registered successfully.")
        return True
            
def login_user(users, username, password):
    if username in users:
        user = users[username]
        if user.check_password(password):
            print("Login successful.")
            return user
        else:
            print("Error: Incorrect password.")
    else:
        print("Error: User not found.")
    return None


