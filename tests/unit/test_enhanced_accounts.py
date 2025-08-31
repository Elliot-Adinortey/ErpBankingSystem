import unittest
from datetime import datetime, timedelta
from user import User
from account import Account, AccountManager


class TestEnhancedAccounts(unittest.TestCase):
    """Test suite for enhanced account management features"""

    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")

    def test_account_nickname_creation(self):
        """Test creating account with nickname"""
        account = Account("savings", 1000, 0, "My Savings")
        
        self.assertEqual(account.nickname, "My Savings")
        self.assertEqual(account.account_type, "savings")
        self.assertEqual(account.balance, 1000)
        self.assertIsInstance(account.created_date, datetime)
        self.assertIsInstance(account.last_activity, datetime)

    def test_account_nickname_update(self):
        """Test updating account nickname"""
        account = Account("current", 500, 1000)
        original_activity = account.last_activity
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        account.update_nickname("Main Checking")
        
        self.assertEqual(account.nickname, "Main Checking")
        self.assertGreater(account.last_activity, original_activity)

    def test_account_display_name(self):
        """Test account display name functionality"""
        # Account without nickname
        account1 = Account("savings", 1000)
        self.assertEqual(account1.get_display_name(), "Savings")
        
        # Account with nickname
        account2 = Account("current", 500, 1000, "Main Account")
        self.assertEqual(account2.get_display_name(), "Main Account (current)")

    def test_account_activity_tracking(self):
        """Test that account activity is tracked on transactions"""
        account = Account("savings", 1000)
        original_activity = account.last_activity
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        account.deposit(100)
        self.assertGreater(account.last_activity, original_activity)

    def test_account_manager_initialization(self):
        """Test AccountManager initialization"""
        manager = AccountManager(self.user)
        self.assertEqual(manager.user, self.user)

    def test_create_account_with_nickname_via_manager(self):
        """Test creating account with nickname through AccountManager"""
        manager = self.user.account_manager
        
        account = manager.create_account_with_nickname("savings", 1000, 0, "Emergency Fund")
        
        self.assertEqual(account.nickname, "Emergency Fund")
        self.assertEqual(account.account_type, "savings")
        self.assertEqual(account.balance, 1000)
        self.assertIn(account, self.user.accounts)

    def test_create_account_invalid_type(self):
        """Test creating account with invalid type"""
        manager = self.user.account_manager
        
        with self.assertRaises(ValueError) as context:
            manager.create_account_with_nickname("invalid", 1000)
        
        self.assertIn("Invalid account type", str(context.exception))

    def test_create_duplicate_account_type(self):
        """Test creating duplicate account type"""
        manager = self.user.account_manager
        
        # Create first account
        manager.create_account_with_nickname("savings", 1000)
        
        # Try to create another savings account
        with self.assertRaises(ValueError) as context:
            manager.create_account_with_nickname("savings", 500)
        
        self.assertIn("already exists", str(context.exception))

    def test_update_account_nickname_via_manager(self):
        """Test updating account nickname through AccountManager"""
        manager = self.user.account_manager
        
        # Create account
        account = manager.create_account_with_nickname("current", 500, 1000)
        
        # Update nickname
        result = manager.update_account_nickname("current", "Primary Checking")
        
        self.assertTrue(result)
        self.assertEqual(account.nickname, "Primary Checking")

    def test_update_nonexistent_account_nickname(self):
        """Test updating nickname for nonexistent account"""
        manager = self.user.account_manager
        
        with self.assertRaises(ValueError) as context:
            manager.update_account_nickname("nonexistent", "New Name")
        
        self.assertIn("not found", str(context.exception))

    def test_get_account_by_nickname(self):
        """Test retrieving account by nickname"""
        manager = self.user.account_manager
        
        # Create account with nickname
        account = manager.create_account_with_nickname("savings", 1000, 0, "Emergency Fund")
        
        # Retrieve by nickname
        retrieved = manager.get_account_by_nickname("Emergency Fund")
        self.assertEqual(retrieved, account)
        
        # Case insensitive search
        retrieved_case = manager.get_account_by_nickname("emergency fund")
        self.assertEqual(retrieved_case, account)
        
        # Non-existent nickname
        not_found = manager.get_account_by_nickname("Non-existent")
        self.assertIsNone(not_found)

    def test_get_account_by_type(self):
        """Test retrieving account by type"""
        manager = self.user.account_manager
        
        # Create account
        account = manager.create_account_with_nickname("current", 500, 1000, "Main Account")
        
        # Retrieve by type
        retrieved = manager.get_account_by_type("current")
        self.assertEqual(retrieved, account)
        
        # Non-existent type
        not_found = manager.get_account_by_type("nonexistent")
        self.assertIsNone(not_found)

    def test_get_account_by_identifier(self):
        """Test retrieving account by type or nickname"""
        manager = self.user.account_manager
        
        # Create account with nickname
        account = manager.create_account_with_nickname("savings", 1000, 0, "Emergency Fund")
        
        # Retrieve by nickname
        by_nickname = manager.get_account_by_identifier("Emergency Fund")
        self.assertEqual(by_nickname, account)
        
        # Retrieve by type
        by_type = manager.get_account_by_identifier("savings")
        self.assertEqual(by_type, account)

    def test_generate_account_summary(self):
        """Test generating comprehensive account summary"""
        manager = self.user.account_manager
        
        # Create multiple accounts
        savings = manager.create_account_with_nickname("savings", 1000, 0, "Emergency Fund")
        current = manager.create_account_with_nickname("current", 500, 1000, "Main Checking")
        
        # Add some transactions
        savings.deposit(100)
        current.withdraw(50)
        
        summary = manager.generate_account_summary()
        
        self.assertEqual(summary['total_accounts'], 2)
        self.assertEqual(summary['total_balance'], 1550)  # 1100 + 450
        self.assertEqual(len(summary['accounts']), 2)
        
        # Check account details
        savings_info = next(acc for acc in summary['accounts'] if acc['type'] == 'savings')
        self.assertEqual(savings_info['nickname'], "Emergency Fund")
        self.assertEqual(savings_info['balance'], 1100)
        self.assertEqual(savings_info['transaction_count'], 1)
        
        current_info = next(acc for acc in summary['accounts'] if acc['type'] == 'current')
        self.assertEqual(current_info['available_balance'], 1450)  # 450 + 1000 overdraft

    def test_get_financial_overview(self):
        """Test getting financial overview"""
        manager = self.user.account_manager
        
        # Create accounts
        savings = manager.create_account_with_nickname("savings", 1000, 0, "Emergency Fund")
        current = manager.create_account_with_nickname("current", 500, 1000)
        
        # Add transactions
        savings.deposit(200)
        current.withdraw(100)
        
        overview = manager.get_financial_overview()
        
        self.assertEqual(overview['total_balance'], 1600)  # 1200 + 400
        self.assertEqual(overview['total_available'], 2600)  # 1200 + 400 + 1000 overdraft
        
        # Check account breakdown
        self.assertIn("Emergency Fund (savings)", overview['account_breakdown'])
        self.assertIn("Current", overview['account_breakdown'])
        
        # Check recent activity
        self.assertGreater(len(overview['recent_activity']), 0)

    def test_user_enhanced_methods(self):
        """Test enhanced methods in User class"""
        # Test create_account_with_nickname
        account = self.user.create_account_with_nickname("savings", 1000, 0, "My Savings")
        self.assertEqual(account.nickname, "My Savings")
        
        # Test update_account_nickname
        result = self.user.update_account_nickname("savings", "Updated Savings")
        self.assertTrue(result)
        self.assertEqual(account.nickname, "Updated Savings")
        
        # Test get_account_by_nickname
        retrieved = self.user.get_account_by_nickname("Updated Savings")
        self.assertEqual(retrieved, account)
        
        # Test enhanced summary
        summary = self.user.get_enhanced_summary()
        self.assertEqual(summary['total_accounts'], 1)
        
        # Test financial overview
        overview = self.user.get_financial_overview()
        self.assertEqual(overview['total_balance'], 1000)

    def test_user_get_account_enhanced(self):
        """Test enhanced get_account method in User class"""
        # Create account with nickname
        account = self.user.create_account_with_nickname("current", 500, 1000, "Main Account")
        
        # Get by type
        by_type = self.user.get_account("current")
        self.assertEqual(by_type, account)
        
        # Get by nickname
        by_nickname = self.user.get_account("Main Account")
        self.assertEqual(by_nickname, account)
        
        # Case insensitive nickname search
        by_nickname_case = self.user.get_account("main account")
        self.assertEqual(by_nickname_case, account)

    def test_backward_compatibility(self):
        """Test that existing functionality still works"""
        # Create account the old way
        old_account = Account("savings", 1000)
        self.user.add_account(old_account)
        
        # Test old methods still work
        summary = self.user.get_accounts_summary()
        self.assertIn("Savings", summary)
        self.assertEqual(summary["Savings"], 1000)
        
        # Test get_account still works with type
        retrieved = self.user.get_account("savings")
        self.assertEqual(retrieved, old_account)


if __name__ == '__main__':
    unittest.main()