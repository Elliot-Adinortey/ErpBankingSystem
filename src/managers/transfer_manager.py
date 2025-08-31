"""
Transfer Manager Module

This module handles account-to-account transfers including validation,
execution, and tracking of transfer operations.
"""

from datetime import datetime
from src.core.transaction import Transaction
import uuid


class TransferTransaction(Transaction):
    """Extended Transaction class for transfer operations"""
    
    def __init__(self, amount, from_account_type, to_account_type, memo=None, transfer_id=None):
        super().__init__(amount, "transfer", datetime.now())
        self.from_account = from_account_type
        self.to_account = to_account_type
        self.memo = memo
        self.transfer_id = transfer_id or self._generate_transfer_id()
        self.is_outgoing = None  # Will be set based on perspective (True for withdrawal, False for deposit)
    
    def _generate_transfer_id(self):
        """Generate unique transfer ID"""
        return f"TXF-{uuid.uuid4().hex[:8].upper()}"
    
    def to_dict(self):
        """Convert to dictionary with transfer-specific fields"""
        base_dict = super().to_dict()
        base_dict.update({
            "from_account": self.from_account,
            "to_account": self.to_account,
            "memo": self.memo,
            "transfer_id": self.transfer_id,
            "is_outgoing": self.is_outgoing
        })
        return base_dict


class TransferValidator:
    """Handles validation logic for transfer operations"""
    
    def __init__(self, user):
        self.user = user
    
    def validate_transfer(self, from_account_identifier, to_account_identifier, amount):
        """
        Comprehensive transfer validation
        
        Args:
            from_account_identifier: Account type or nickname for source account
            to_account_identifier: Account type or nickname for destination account
            amount: Transfer amount
            
        Returns:
            tuple: (is_valid, error_message, from_account, to_account)
        """
        # Validate amount
        if not self._validate_amount(amount):
            return False, "Transfer amount must be positive", None, None
        
        # Validate account existence and ownership
        from_account = self._validate_account_exists(from_account_identifier)
        if not from_account:
            return False, f"Source account '{from_account_identifier}' not found", None, None
        
        to_account = self._validate_account_exists(to_account_identifier)
        if not to_account:
            return False, f"Destination account '{to_account_identifier}' not found", None, None
        
        # Validate accounts are different
        if from_account == to_account:
            return False, "Cannot transfer to the same account", None, None
        
        # Validate sufficient funds (including overdraft)
        if not self._validate_sufficient_funds(from_account, amount):
            available_balance = self._get_available_balance(from_account)
            return False, f"Insufficient funds. Available balance: ${available_balance:.2f}", from_account, to_account
        
        return True, "Transfer validation successful", from_account, to_account
    
    def _validate_amount(self, amount):
        """Validate transfer amount is positive"""
        try:
            amount_float = float(amount)
            return amount_float > 0
        except (ValueError, TypeError):
            return False
    
    def _validate_account_exists(self, account_identifier):
        """Validate account exists and belongs to user"""
        return self.user.get_account(account_identifier)
    
    def _validate_sufficient_funds(self, account, amount):
        """Validate account has sufficient funds including overdraft consideration"""
        available_balance = self._get_available_balance(account)
        return available_balance >= amount
    
    def _get_available_balance(self, account):
        """Get available balance including overdraft for current accounts"""
        available = account.balance
        if account.account_type == 'current':
            available += account.overdraft_limit
        return available


class TransferManager:
    """Manages transfer operations between user accounts"""
    
    def __init__(self, user):
        self.user = user
        self.validator = TransferValidator(user)
    
    def validate_transfer(self, from_account_identifier, to_account_identifier, amount):
        """Validate transfer operation"""
        return self.validator.validate_transfer(from_account_identifier, to_account_identifier, amount)
    
    def execute_transfer(self, from_account_identifier, to_account_identifier, amount, memo=None):
        """
        Execute transfer between accounts
        
        Args:
            from_account_identifier: Source account identifier
            to_account_identifier: Destination account identifier
            amount: Transfer amount
            memo: Optional transfer memo
            
        Returns:
            tuple: (success, message, transfer_id)
        """
        # Validate transfer
        is_valid, error_message, from_account, to_account = self.validate_transfer(
            from_account_identifier, to_account_identifier, amount
        )
        
        if not is_valid:
            return False, error_message, None
        
        try:
            # Generate transfer ID
            transfer_id = f"TXF-{uuid.uuid4().hex[:8].upper()}"
            
            # Create transfer transactions
            outgoing_transfer = TransferTransaction(
                amount, from_account.account_type, to_account.account_type, memo, transfer_id
            )
            outgoing_transfer.is_outgoing = True
            
            incoming_transfer = TransferTransaction(
                amount, from_account.account_type, to_account.account_type, memo, transfer_id
            )
            incoming_transfer.is_outgoing = False
            
            # Execute the transfer (update balances and add transactions)
            from_account.balance -= amount
            from_account.transactions.append(outgoing_transfer)
            from_account.update_activity()
            
            to_account.balance += amount
            to_account.transactions.append(incoming_transfer)
            to_account.update_activity()
            
            success_message = (
                f"Transfer of ${amount:.2f} from {from_account.get_display_name()} "
                f"to {to_account.get_display_name()} completed successfully. "
                f"Transfer ID: {transfer_id}"
            )
            
            return True, success_message, transfer_id
            
        except Exception as e:
            return False, f"Transfer failed due to system error: {str(e)}", None
    
    def get_transfer_history(self, account_identifier=None):
        """
        Get transfer history for specific account or all accounts
        
        Args:
            account_identifier: Optional account identifier to filter transfers
            
        Returns:
            list: List of transfer transactions
        """
        transfers = []
        
        if account_identifier:
            # Get transfers for specific account
            account = self.user.get_account(account_identifier)
            if account:
                transfers = [t for t in account.transactions if isinstance(t, TransferTransaction)]
        else:
            # Get transfers for all accounts
            for account in self.user.accounts:
                account_transfers = [t for t in account.transactions if isinstance(t, TransferTransaction)]
                transfers.extend(account_transfers)
        
        # Sort by date (most recent first)
        transfers.sort(key=lambda x: x.date, reverse=True)
        return transfers
    
    def get_transfer_by_id(self, transfer_id):
        """Get transfer details by transfer ID"""
        for account in self.user.accounts:
            for transaction in account.transactions:
                if isinstance(transaction, TransferTransaction) and transaction.transfer_id == transfer_id:
                    return transaction
        return None