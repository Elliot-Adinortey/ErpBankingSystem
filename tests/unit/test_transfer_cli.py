import unittest
from unittest.mock import patch, MagicMock
import io
import sys
from user import User
from account import Account
from main import transfer
from data_storage import save_users_to_file, load_users_from_file


class TestTransferCLI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test accounts
        savings_account = Account("savings", 1000.0, nickname="Emergency Fund")
        current_account = Account("current", 500.0, overdraft_limit=200.0, nickname="Daily Spending")
        salary_account = Account("salary", 2500.0)
        
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
        self.user.add_account(salary_account)

    def capture_output(self, func, args):
        """Helper method to capture print output"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            func(args)
            return captured_output.getvalue()
        finally:
            sys.stdout = sys.__stdout__

    @patch('main.authenticate_user')
    @patch('main.save_users_to_file')
    def test_successful_transfer_by_type(self, mock_save, mock_auth):
        """Test successful transfer using account types"""
        mock_auth.return_value = self.user
        mock_save.return_value = None
        
        args = MagicMock()
        args.from_account = "savings"
        args.to_account = "current"
        args.amount = 200.0
        args.memo = "Test transfer"
        
        output = self.capture_output(transfer, args)
        
        # Check success message
        self.assertIn("✓", output)
        self.assertIn("completed successfully", output)
        self.assertIn("Transfer ID:", output)
        
        # Check updated balances are shown
        self.assertIn("Updated Balances:", output)
        self.assertIn("Emergency Fund (savings): $800.00", output)
        self.assertIn("Daily Spending (current): $700.00", output)
        
        # Verify actual balances
        savings = self.user.get_account("savings")
        current = self.user.get_account("current")
        self.assertEqual(savings.balance, 800.0)
        self.assertEqual(current.balance, 700.0)

    @patch('main.authenticate_user')
    @patch('main.save_users_to_file')
    def test_successful_transfer_by_nickname(self, mock_save, mock_auth):
        """Test successful transfer using account nicknames"""
        mock_auth.return_value = self.user
        mock_save.return_value = None
        
        args = MagicMock()
        args.from_account = "Emergency Fund"
        args.to_account = "Daily Spending"
        args.amount = 150.0
        args.memo = None
        
        output = self.capture_output(transfer, args)
        
        # Check success message
        self.assertIn("✓", output)
        self.assertIn("completed successfully", output)
        
        # Verify balances
        savings = self.user.get_account("savings")
        current = self.user.get_account("current")
        self.assertEqual(savings.balance, 850.0)
        self.assertEqual(current.balance, 650.0)

    @patch('main.authenticate_user')
    def test_transfer_insufficient_funds(self, mock_auth):
        """Test transfer with insufficient funds"""
        mock_auth.return_value = self.user
        
        args = MagicMock()
        args.from_account = "current"
        args.to_account = "savings"
        args.amount = 1000.0  # More than available (500 + 200 overdraft)
        args.memo = None
        
        output = self.capture_output(transfer, args)
        
        # Check error message
        self.assertIn("✗ Transfer failed:", output)
        self.assertIn("Insufficient funds", output)
        self.assertIn("Available balance:", output)
        
        # Verify balances unchanged
        savings = self.user.get_account("savings")
        current = self.user.get_account("current")
        self.assertEqual(savings.balance, 1000.0)
        self.assertEqual(current.balance, 500.0)

    @patch('main.authenticate_user')
    def test_transfer_account_not_found(self, mock_auth):
        """Test transfer with non-existent account"""
        mock_auth.return_value = self.user
        
        args = MagicMock()
        args.from_account = "nonexistent"
        args.to_account = "savings"
        args.amount = 100.0
        args.memo = None
        
        output = self.capture_output(transfer, args)
        
        # Check error message
        self.assertIn("✗ Transfer failed:", output)
        self.assertIn("not found", output)
        
        # Check available accounts are shown
        self.assertIn("Available accounts:", output)
        self.assertIn("Emergency Fund (savings)", output)
        self.assertIn("Daily Spending (current)", output)
        self.assertIn("Salary", output)

    @patch('main.authenticate_user')
    def test_transfer_same_account(self, mock_auth):
        """Test transfer to same account"""
        mock_auth.return_value = self.user
        
        args = MagicMock()
        args.from_account = "savings"
        args.to_account = "Emergency Fund"  # Same account by nickname
        args.amount = 100.0
        args.memo = None
        
        output = self.capture_output(transfer, args)
        
        # Check error message
        self.assertIn("✗ Transfer failed:", output)
        self.assertIn("Cannot transfer to the same account", output)

    @patch('main.authenticate_user')
    def test_transfer_with_memo(self, mock_auth):
        """Test transfer with memo"""
        mock_auth.return_value = self.user
        
        args = MagicMock()
        args.from_account = "salary"
        args.to_account = "savings"
        args.amount = 500.0
        args.memo = "Monthly savings"
        
        output = self.capture_output(transfer, args)
        
        # Check success
        self.assertIn("✓", output)
        self.assertIn("completed successfully", output)
        
        # Verify transfer was recorded with memo
        salary_account = self.user.get_account("salary")
        transfer_transaction = None
        for transaction in salary_account.transactions:
            if hasattr(transaction, 'memo') and transaction.memo == "Monthly savings":
                transfer_transaction = transaction
                break
        
        self.assertIsNotNone(transfer_transaction)
        self.assertEqual(transfer_transaction.memo, "Monthly savings")

    @patch('main.authenticate_user')
    def test_transfer_authentication_failure(self, mock_auth):
        """Test transfer when authentication fails"""
        mock_auth.return_value = None
        
        args = MagicMock()
        args.from_account = "savings"
        args.to_account = "current"
        args.amount = 100.0
        args.memo = None
        
        output = self.capture_output(transfer, args)
        
        # Should not contain transfer information when auth fails
        self.assertEqual(output, "")

    @patch('main.authenticate_user')
    @patch('main.save_users_to_file')
    def test_transfer_with_overdraft(self, mock_save, mock_auth):
        """Test transfer using overdraft facility"""
        mock_auth.return_value = self.user
        mock_save.return_value = None
        
        args = MagicMock()
        args.from_account = "current"  # Has 500 balance + 200 overdraft
        args.to_account = "savings"
        args.amount = 600.0  # Uses overdraft
        args.memo = None
        
        output = self.capture_output(transfer, args)
        
        # Check success
        self.assertIn("✓", output)
        self.assertIn("completed successfully", output)
        
        # Verify balances (current should be negative)
        current = self.user.get_account("current")
        savings = self.user.get_account("savings")
        self.assertEqual(current.balance, -100.0)  # 500 - 600
        self.assertEqual(savings.balance, 1600.0)  # 1000 + 600

    def test_transfer_validation_directly(self):
        """Test transfer validation logic directly"""
        # Test valid transfer
        is_valid, message, from_acc, to_acc = self.user.validate_transfer("savings", "current", 100.0)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Transfer validation successful")
        
        # Test invalid amount
        is_valid, message, _, _ = self.user.validate_transfer("savings", "current", -100.0)
        self.assertFalse(is_valid)
        self.assertIn("positive", message)
        
        # Test insufficient funds
        is_valid, message, _, _ = self.user.validate_transfer("current", "savings", 1000.0)
        self.assertFalse(is_valid)
        self.assertIn("Insufficient funds", message)

    def test_transfer_history_tracking(self):
        """Test that transfers are properly tracked in history"""
        # Execute a transfer
        success, message, transfer_id = self.user.transfer_between_accounts("savings", "current", 200.0, "Test memo")
        self.assertTrue(success)
        
        # Check transfer history
        transfer_history = self.user.get_transfer_history()
        self.assertEqual(len(transfer_history), 2)  # One outgoing, one incoming
        
        # Check transfer by ID
        transfer = self.user.get_transfer_by_id(transfer_id)
        self.assertIsNotNone(transfer)
        self.assertEqual(transfer.transfer_id, transfer_id)
        self.assertEqual(transfer.memo, "Test memo")


if __name__ == '__main__':
    unittest.main()