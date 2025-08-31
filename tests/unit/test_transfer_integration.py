"""
Integration tests for transfer functionality with User class
"""

import unittest
from user import User, register_user, login_user
from account import Account


class TestTransferIntegrationWithUser(unittest.TestCase):
    """Test transfer functionality integrated with User class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.users = {}
        
        # Register a test user
        register_user(self.users, "testuser", "TestPass123", "test@example.com")
        self.user = self.users["testuser"]
        
        # Create accounts for the user
        self.user.create_account_with_nickname("savings", 1000.0, 0, "Emergency Fund")
        self.user.create_account_with_nickname("current", 500.0, 200.0, "Daily Spending")
    
    def test_user_transfer_functionality(self):
        """Test complete transfer functionality through User class"""
        # Test transfer validation
        is_valid, message, from_acc, to_acc = self.user.validate_transfer(
            "Emergency Fund", "Daily Spending", 300.0
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Transfer validation successful")
        
        # Test transfer execution
        success, exec_message, transfer_id = self.user.transfer_between_accounts(
            "Emergency Fund", "Daily Spending", 300.0, "Monthly budget"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(transfer_id)
        self.assertIn("Transfer of $300.00", exec_message)
        
        # Verify balances
        savings_account = self.user.get_account("Emergency Fund")
        current_account = self.user.get_account("Daily Spending")
        
        self.assertEqual(savings_account.balance, 700.0)  # 1000 - 300
        self.assertEqual(current_account.balance, 800.0)  # 500 + 300
    
    def test_user_transfer_history(self):
        """Test transfer history functionality through User class"""
        # Execute multiple transfers
        self.user.transfer_between_accounts("savings", "current", 100.0, "Transfer 1")
        self.user.transfer_between_accounts("current", "savings", 50.0, "Transfer 2")
        
        # Get complete transfer history
        all_transfers = self.user.get_transfer_history()
        self.assertEqual(len(all_transfers), 4)  # 2 transfers × 2 transactions each
        
        # Get transfer history for specific account
        savings_transfers = self.user.get_transfer_history("savings")
        self.assertEqual(len(savings_transfers), 2)  # 1 outgoing + 1 incoming
        
        # Test getting transfer by ID
        transfer_id = all_transfers[0].transfer_id
        retrieved_transfer = self.user.get_transfer_by_id(transfer_id)
        self.assertIsNotNone(retrieved_transfer)
        self.assertEqual(retrieved_transfer.transfer_id, transfer_id)
    
    def test_user_transfer_with_login(self):
        """Test transfer functionality with user login workflow"""
        # Login user
        logged_in_user = login_user(self.users, "testuser", "TestPass123")
        self.assertIsNotNone(logged_in_user)
        
        # Perform transfer
        success, message, transfer_id = logged_in_user.transfer_between_accounts(
            "savings", "current", 200.0, "Post-login transfer"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(transfer_id)
        
        # Verify the transfer is tracked
        transfers = logged_in_user.get_transfer_history()
        self.assertGreater(len(transfers), 0)
        
        # Verify transfer can be retrieved
        retrieved = logged_in_user.get_transfer_by_id(transfer_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.memo, "Post-login transfer")
    
    def test_transfer_validation_errors(self):
        """Test transfer validation error handling through User class"""
        # Test insufficient funds
        is_valid, message, _, _ = self.user.validate_transfer("savings", "current", 2000.0)
        self.assertFalse(is_valid)
        self.assertIn("Insufficient funds", message)
        
        # Test non-existent account
        is_valid, message, _, _ = self.user.validate_transfer("nonexistent", "current", 100.0)
        self.assertFalse(is_valid)
        self.assertIn("not found", message)
        
        # Test same account transfer
        is_valid, message, _, _ = self.user.validate_transfer("savings", "savings", 100.0)
        self.assertFalse(is_valid)
        self.assertIn("Cannot transfer to the same account", message)
    
    def test_transfer_with_overdraft(self):
        """Test transfer using overdraft facility through User class"""
        # Transfer more than current account balance but within overdraft
        success, message, transfer_id = self.user.transfer_between_accounts(
            "current", "savings", 600.0, "Overdraft transfer"
        )
        
        self.assertTrue(success)
        
        # Verify balances
        current_account = self.user.get_account("current")
        savings_account = self.user.get_account("savings")
        
        self.assertEqual(current_account.balance, -100.0)  # 500 - 600
        self.assertEqual(savings_account.balance, 1600.0)  # 1000 + 600


if __name__ == '__main__':
    unittest.main()