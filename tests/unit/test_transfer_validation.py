"""
Unit tests for transfer validation logic
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from user import User
from account import Account
from transfer_manager import TransferValidator, TransferManager, TransferTransaction


class TestTransferTransaction(unittest.TestCase):
    """Test TransferTransaction class"""
    
    def test_transfer_transaction_creation(self):
        """Test creating a transfer transaction"""
        transfer = TransferTransaction(100.0, "savings", "current", "Test transfer")
        
        self.assertEqual(transfer.amount, 100.0)
        self.assertEqual(transfer.transaction_type, "transfer")
        self.assertEqual(transfer.from_account, "savings")
        self.assertEqual(transfer.to_account, "current")
        self.assertEqual(transfer.memo, "Test transfer")
        self.assertIsNotNone(transfer.transfer_id)
        self.assertTrue(transfer.transfer_id.startswith("TXF-"))
        self.assertIsInstance(transfer.date, datetime)
    
    def test_transfer_transaction_with_custom_id(self):
        """Test creating transfer transaction with custom ID"""
        custom_id = "TXF-CUSTOM123"
        transfer = TransferTransaction(50.0, "current", "savings", transfer_id=custom_id)
        
        self.assertEqual(transfer.transfer_id, custom_id)
    
    def test_transfer_transaction_to_dict(self):
        """Test converting transfer transaction to dictionary"""
        transfer = TransferTransaction(75.0, "savings", "current", "Test memo", "TXF-TEST123")
        transfer.is_outgoing = True
        
        result = transfer.to_dict()
        
        self.assertEqual(result["amount"], 75.0)
        self.assertEqual(result["transaction"], "transfer")
        self.assertEqual(result["from_account"], "savings")
        self.assertEqual(result["to_account"], "current")
        self.assertEqual(result["memo"], "Test memo")
        self.assertEqual(result["transfer_id"], "TXF-TEST123")
        self.assertTrue(result["is_outgoing"])


class TestTransferValidator(unittest.TestCase):
    """Test TransferValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = Mock()
        self.validator = TransferValidator(self.user)
        
        # Create mock accounts
        self.savings_account = Mock()
        self.savings_account.account_type = "savings"
        self.savings_account.balance = 1000.0
        self.savings_account.overdraft_limit = 0
        
        self.current_account = Mock()
        self.current_account.account_type = "current"
        self.current_account.balance = 500.0
        self.current_account.overdraft_limit = 200.0
    
    def test_validate_positive_amount(self):
        """Test validation of positive amounts"""
        self.assertTrue(self.validator._validate_amount(100.0))
        self.assertTrue(self.validator._validate_amount("50.5"))
        self.assertTrue(self.validator._validate_amount(1))
    
    def test_validate_invalid_amounts(self):
        """Test validation of invalid amounts"""
        self.assertFalse(self.validator._validate_amount(0))
        self.assertFalse(self.validator._validate_amount(-50))
        self.assertFalse(self.validator._validate_amount("invalid"))
        self.assertFalse(self.validator._validate_amount(None))
    
    def test_validate_account_exists(self):
        """Test account existence validation"""
        self.user.get_account.return_value = self.savings_account
        
        result = self.validator._validate_account_exists("savings")
        
        self.assertEqual(result, self.savings_account)
        self.user.get_account.assert_called_once_with("savings")
    
    def test_validate_account_not_exists(self):
        """Test validation when account doesn't exist"""
        self.user.get_account.return_value = None
        
        result = self.validator._validate_account_exists("nonexistent")
        
        self.assertIsNone(result)
    
    def test_get_available_balance_savings(self):
        """Test available balance calculation for savings account"""
        available = self.validator._get_available_balance(self.savings_account)
        self.assertEqual(available, 1000.0)
    
    def test_get_available_balance_current_with_overdraft(self):
        """Test available balance calculation for current account with overdraft"""
        available = self.validator._get_available_balance(self.current_account)
        self.assertEqual(available, 700.0)  # 500 + 200 overdraft
    
    def test_validate_sufficient_funds_success(self):
        """Test sufficient funds validation - success case"""
        result = self.validator._validate_sufficient_funds(self.savings_account, 500.0)
        self.assertTrue(result)
    
    def test_validate_sufficient_funds_failure(self):
        """Test sufficient funds validation - insufficient funds"""
        result = self.validator._validate_sufficient_funds(self.savings_account, 1500.0)
        self.assertFalse(result)
    
    def test_validate_sufficient_funds_with_overdraft(self):
        """Test sufficient funds validation with overdraft"""
        # Should succeed with overdraft
        result = self.validator._validate_sufficient_funds(self.current_account, 600.0)
        self.assertTrue(result)
        
        # Should fail even with overdraft
        result = self.validator._validate_sufficient_funds(self.current_account, 800.0)
        self.assertFalse(result)
    
    def test_validate_transfer_success(self):
        """Test successful transfer validation"""
        self.user.get_account.side_effect = [self.savings_account, self.current_account]
        
        is_valid, message, from_acc, to_acc = self.validator.validate_transfer("savings", "current", 300.0)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Transfer validation successful")
        self.assertEqual(from_acc, self.savings_account)
        self.assertEqual(to_acc, self.current_account)
    
    def test_validate_transfer_invalid_amount(self):
        """Test transfer validation with invalid amount"""
        is_valid, message, from_acc, to_acc = self.validator.validate_transfer("savings", "current", -100)
        
        self.assertFalse(is_valid)
        self.assertEqual(message, "Transfer amount must be positive")
        self.assertIsNone(from_acc)
        self.assertIsNone(to_acc)
    
    def test_validate_transfer_source_account_not_found(self):
        """Test transfer validation when source account doesn't exist"""
        self.user.get_account.side_effect = [None, self.current_account]
        
        is_valid, message, from_acc, to_acc = self.validator.validate_transfer("nonexistent", "current", 100)
        
        self.assertFalse(is_valid)
        self.assertEqual(message, "Source account 'nonexistent' not found")
        self.assertIsNone(from_acc)
        self.assertIsNone(to_acc)
    
    def test_validate_transfer_destination_account_not_found(self):
        """Test transfer validation when destination account doesn't exist"""
        self.user.get_account.side_effect = [self.savings_account, None]
        
        is_valid, message, from_acc, to_acc = self.validator.validate_transfer("savings", "nonexistent", 100)
        
        self.assertFalse(is_valid)
        self.assertEqual(message, "Destination account 'nonexistent' not found")
        self.assertIsNone(from_acc)
        self.assertIsNone(to_acc)
    
    def test_validate_transfer_same_account(self):
        """Test transfer validation when trying to transfer to same account"""
        self.user.get_account.side_effect = [self.savings_account, self.savings_account]
        
        is_valid, message, from_acc, to_acc = self.validator.validate_transfer("savings", "savings", 100)
        
        self.assertFalse(is_valid)
        self.assertEqual(message, "Cannot transfer to the same account")
        self.assertIsNone(from_acc)
        self.assertIsNone(to_acc)
    
    def test_validate_transfer_insufficient_funds(self):
        """Test transfer validation with insufficient funds"""
        self.user.get_account.side_effect = [self.savings_account, self.current_account]
        
        is_valid, message, from_acc, to_acc = self.validator.validate_transfer("savings", "current", 1500.0)
        
        self.assertFalse(is_valid)
        self.assertIn("Insufficient funds", message)
        self.assertIn("Available balance: $1000.00", message)
        self.assertEqual(from_acc, self.savings_account)
        self.assertEqual(to_acc, self.current_account)


class TestTransferManager(unittest.TestCase):
    """Test TransferManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = Mock()
        self.transfer_manager = TransferManager(self.user)
        # Mock the validator
        self.transfer_manager.validator = Mock()
        
        # Create mock accounts
        self.savings_account = Mock()
        self.savings_account.account_type = "savings"
        self.savings_account.balance = 1000.0
        self.savings_account.overdraft_limit = 0
        self.savings_account.transactions = []
        self.savings_account.get_display_name.return_value = "Savings"
        
        self.current_account = Mock()
        self.current_account.account_type = "current"
        self.current_account.balance = 500.0
        self.current_account.overdraft_limit = 200.0
        self.current_account.transactions = []
        self.current_account.get_display_name.return_value = "Current"
    
    @patch('transfer_manager.uuid.uuid4')
    def test_execute_transfer_success(self, mock_uuid):
        """Test successful transfer execution"""
        mock_uuid.return_value.hex = "abcd1234efgh5678"
        
        # Mock validator to return success
        self.transfer_manager.validator.validate_transfer.return_value = (
            True, "Transfer validation successful", self.savings_account, self.current_account
        )
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", 300.0, "Test transfer"
        )
        
        self.assertTrue(success)
        self.assertIn("Transfer of $300.00", message)
        self.assertIn("completed successfully", message)
        self.assertEqual(transfer_id, "TXF-ABCD1234")
        
        # Verify balance updates
        self.assertEqual(self.savings_account.balance, 700.0)  # 1000 - 300
        self.assertEqual(self.current_account.balance, 800.0)  # 500 + 300
        
        # Verify transactions were added
        self.assertEqual(len(self.savings_account.transactions), 1)
        self.assertEqual(len(self.current_account.transactions), 1)
        
        # Verify activity updates were called
        self.savings_account.update_activity.assert_called_once()
        self.current_account.update_activity.assert_called_once()
    
    def test_execute_transfer_validation_failure(self):
        """Test transfer execution with validation failure"""
        self.transfer_manager.validator.validate_transfer.return_value = (
            False, "Insufficient funds", None, None
        )
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", 2000.0
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Insufficient funds")
        self.assertIsNone(transfer_id)
    
    @patch('transfer_manager.uuid.uuid4')
    def test_execute_transfer_system_error(self, mock_uuid):
        """Test transfer execution with system error"""
        mock_uuid.side_effect = Exception("System error")
        
        self.transfer_manager.validator.validate_transfer.return_value = (
            True, "Transfer validation successful", self.savings_account, self.current_account
        )
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", 100.0
        )
        
        self.assertFalse(success)
        self.assertIn("Transfer failed due to system error", message)
        self.assertIsNone(transfer_id)
    
    def test_get_transfer_history_all_accounts(self):
        """Test getting transfer history for all accounts"""
        # Create mock transfer transactions
        transfer1 = TransferTransaction(100.0, "savings", "current")
        transfer2 = TransferTransaction(50.0, "current", "savings")
        
        self.savings_account.transactions = [transfer1]
        self.current_account.transactions = [transfer2]
        self.user.accounts = [self.savings_account, self.current_account]
        
        transfers = self.transfer_manager.get_transfer_history()
        
        self.assertEqual(len(transfers), 2)
        self.assertIn(transfer1, transfers)
        self.assertIn(transfer2, transfers)
    
    def test_get_transfer_history_specific_account(self):
        """Test getting transfer history for specific account"""
        transfer1 = TransferTransaction(100.0, "savings", "current")
        self.savings_account.transactions = [transfer1]
        
        self.user.get_account.return_value = self.savings_account
        
        transfers = self.transfer_manager.get_transfer_history("savings")
        
        self.assertEqual(len(transfers), 1)
        self.assertEqual(transfers[0], transfer1)
    
    def test_get_transfer_history_account_not_found(self):
        """Test getting transfer history for non-existent account"""
        self.user.get_account.return_value = None
        
        transfers = self.transfer_manager.get_transfer_history("nonexistent")
        
        self.assertEqual(len(transfers), 0)
    
    def test_get_transfer_by_id(self):
        """Test getting transfer by ID"""
        transfer_id = "TXF-TEST123"
        transfer = TransferTransaction(100.0, "savings", "current", transfer_id=transfer_id)
        
        self.savings_account.transactions = [transfer]
        self.user.accounts = [self.savings_account]
        
        result = self.transfer_manager.get_transfer_by_id(transfer_id)
        
        self.assertEqual(result, transfer)
    
    def test_get_transfer_by_id_not_found(self):
        """Test getting transfer by non-existent ID"""
        self.user.accounts = [self.savings_account]
        self.savings_account.transactions = []
        
        result = self.transfer_manager.get_transfer_by_id("TXF-NOTFOUND")
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()