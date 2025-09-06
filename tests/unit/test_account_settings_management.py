import unittest
import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.user import User
from src.core.account import Account, AccountManager


class TestAccountSettingsManagement(unittest.TestCase):
    """Test suite for account settings and management features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test accounts
        self.savings_account = Account("savings", 1000.0, 0, "My Savings")
        self.current_account = Account("current", 500.0, 200.0, "Main Current")
        self.salary_account = Account("salary", 2000.0, 0)
        
        self.user.add_account(self.savings_account)
        self.user.add_account(self.current_account)
        self.user.add_account(self.salary_account)
    
    def test_account_initialization_with_active_status(self):
        """Test that accounts are initialized as active by default"""
        account = Account("savings", 100.0)
        self.assertTrue(account.is_active)
    
    def test_update_nickname(self):
        """Test updating account nickname"""
        old_nickname = self.savings_account.nickname
        self.savings_account.update_nickname("Updated Savings")
        
        self.assertEqual(self.savings_account.nickname, "Updated Savings")
        self.assertNotEqual(self.savings_account.nickname, old_nickname)
    
    def test_update_overdraft_limit_current_account(self):
        """Test updating overdraft limit for current account"""
        old_limit = self.current_account.overdraft_limit
        new_limit = 300.0
        
        returned_old_limit = self.current_account.update_overdraft_limit(new_limit)
        
        self.assertEqual(self.current_account.overdraft_limit, new_limit)
        self.assertEqual(returned_old_limit, old_limit)
    
    def test_update_overdraft_limit_non_current_account(self):
        """Test that overdraft limit cannot be set for non-current accounts"""
        with self.assertRaises(ValueError) as context:
            self.savings_account.update_overdraft_limit(100.0)
        
        self.assertIn("Overdraft limit can only be set for current accounts", str(context.exception))
    
    def test_update_overdraft_limit_negative_value(self):
        """Test that overdraft limit cannot be negative"""
        with self.assertRaises(ValueError) as context:
            self.current_account.update_overdraft_limit(-50.0)
        
        self.assertIn("Overdraft limit cannot be negative", str(context.exception))
    
    def test_account_deactivation(self):
        """Test account deactivation"""
        self.assertTrue(self.savings_account.is_active)
        
        self.savings_account.deactivate()
        
        self.assertFalse(self.savings_account.is_active)
    
    def test_account_deactivation_already_inactive(self):
        """Test deactivating an already inactive account"""
        self.savings_account.deactivate()
        
        with self.assertRaises(ValueError) as context:
            self.savings_account.deactivate()
        
        self.assertIn("Account is already deactivated", str(context.exception))
    
    def test_account_reactivation(self):
        """Test account reactivation"""
        self.savings_account.deactivate()
        self.assertFalse(self.savings_account.is_active)
        
        self.savings_account.reactivate()
        
        self.assertTrue(self.savings_account.is_active)
    
    def test_account_reactivation_already_active(self):
        """Test reactivating an already active account"""
        with self.assertRaises(ValueError) as context:
            self.savings_account.reactivate()
        
        self.assertIn("Account is already active", str(context.exception))
    
    def test_display_name_with_inactive_status(self):
        """Test that display name shows inactive status"""
        original_name = self.savings_account.get_display_name()
        
        self.savings_account.deactivate()
        inactive_name = self.savings_account.get_display_name()
        
        self.assertNotEqual(original_name, inactive_name)
        self.assertIn("[INACTIVE]", inactive_name)
    
    def test_deposit_to_inactive_account(self):
        """Test that deposits are blocked on inactive accounts"""
        self.savings_account.deactivate()
        original_balance = self.savings_account.balance
        
        # Capture print output to verify error message
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.savings_account.deposit(100.0)
        
        output = f.getvalue()
        
        # Balance should not change
        self.assertEqual(self.savings_account.balance, original_balance)
        self.assertIn("Cannot deposit to inactive account", output)
    
    def test_withdraw_from_inactive_account(self):
        """Test that withdrawals are blocked on inactive accounts"""
        self.savings_account.deactivate()
        original_balance = self.savings_account.balance
        
        # Capture print output to verify error message
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.savings_account.withdraw(50.0)
        
        output = f.getvalue()
        
        # Balance should not change
        self.assertEqual(self.savings_account.balance, original_balance)
        self.assertIn("Cannot withdraw from inactive account", output)


class TestAccountManager(unittest.TestCase):
    """Test suite for AccountManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test accounts
        self.savings_account = Account("savings", 1000.0, 0, "My Savings")
        self.current_account = Account("current", 500.0, 200.0, "Main Current")
        
        self.user.add_account(self.savings_account)
        self.user.add_account(self.current_account)
        
        self.account_manager = AccountManager(self.user)
    
    def test_update_account_settings_nickname_only(self):
        """Test updating only nickname"""
        changes = self.account_manager.update_account_settings("savings", nickname="New Savings Name")
        
        self.assertEqual(len(changes), 1)
        self.assertIn("nickname", changes[0])
        self.assertEqual(self.savings_account.nickname, "New Savings Name")
    
    def test_update_account_settings_overdraft_only(self):
        """Test updating only overdraft limit"""
        changes = self.account_manager.update_account_settings("current", overdraft_limit=300.0)
        
        self.assertEqual(len(changes), 1)
        self.assertIn("overdraft limit", changes[0])
        self.assertEqual(self.current_account.overdraft_limit, 300.0)
    
    def test_update_account_settings_both(self):
        """Test updating both nickname and overdraft limit"""
        changes = self.account_manager.update_account_settings(
            "current", 
            nickname="Updated Current", 
            overdraft_limit=250.0
        )
        
        self.assertEqual(len(changes), 2)
        self.assertEqual(self.current_account.nickname, "Updated Current")
        self.assertEqual(self.current_account.overdraft_limit, 250.0)
    
    def test_update_account_settings_no_changes(self):
        """Test updating with same values (no changes)"""
        original_nickname = self.savings_account.nickname
        changes = self.account_manager.update_account_settings("savings", nickname=original_nickname)
        
        self.assertEqual(len(changes), 0)
    
    def test_update_account_settings_invalid_account(self):
        """Test updating settings for non-existent account"""
        with self.assertRaises(ValueError) as context:
            self.account_manager.update_account_settings("nonexistent", nickname="Test")
        
        self.assertIn("Account 'nonexistent' not found", str(context.exception))
    
    def test_update_account_settings_invalid_overdraft(self):
        """Test updating overdraft for non-current account"""
        with self.assertRaises(ValueError) as context:
            self.account_manager.update_account_settings("savings", overdraft_limit=100.0)
        
        self.assertIn("Cannot update overdraft limit", str(context.exception))
    
    def test_deactivate_account(self):
        """Test account deactivation through manager"""
        result = self.account_manager.deactivate_account("savings")
        
        self.assertTrue(result)
        self.assertFalse(self.savings_account.is_active)
    
    def test_deactivate_account_invalid(self):
        """Test deactivating non-existent account"""
        with self.assertRaises(ValueError) as context:
            self.account_manager.deactivate_account("nonexistent")
        
        self.assertIn("Account 'nonexistent' not found", str(context.exception))
    
    def test_deactivate_account_already_inactive(self):
        """Test deactivating already inactive account"""
        self.account_manager.deactivate_account("savings")
        
        with self.assertRaises(ValueError) as context:
            self.account_manager.deactivate_account("savings")
        
        self.assertIn("Cannot deactivate account", str(context.exception))
    
    def test_reactivate_account(self):
        """Test account reactivation through manager"""
        self.account_manager.deactivate_account("savings")
        result = self.account_manager.reactivate_account("savings")
        
        self.assertTrue(result)
        self.assertTrue(self.savings_account.is_active)
    
    def test_reactivate_account_invalid(self):
        """Test reactivating non-existent account"""
        with self.assertRaises(ValueError) as context:
            self.account_manager.reactivate_account("nonexistent")
        
        self.assertIn("Account 'nonexistent' not found", str(context.exception))
    
    def test_reactivate_account_already_active(self):
        """Test reactivating already active account"""
        with self.assertRaises(ValueError) as context:
            self.account_manager.reactivate_account("savings")
        
        self.assertIn("Cannot reactivate account", str(context.exception))
    
    def test_get_account_settings(self):
        """Test retrieving account settings"""
        settings = self.account_manager.get_account_settings("savings")
        
        self.assertEqual(settings['account_type'], "savings")
        self.assertEqual(settings['nickname'], "My Savings")
        self.assertEqual(settings['balance'], 1000.0)
        self.assertTrue(settings['is_active'])
        self.assertIn('created_date', settings)
        self.assertIn('last_activity', settings)
        self.assertIn('display_name', settings)
    
    def test_get_account_settings_invalid(self):
        """Test retrieving settings for non-existent account"""
        with self.assertRaises(ValueError) as context:
            self.account_manager.get_account_settings("nonexistent")
        
        self.assertIn("Account 'nonexistent' not found", str(context.exception))
    
    def test_list_accounts_with_status(self):
        """Test listing accounts includes active status"""
        self.account_manager.deactivate_account("current")
        
        accounts_list = self.account_manager.list_accounts_with_nicknames()
        
        # Find the accounts in the list
        savings_info = next(acc for acc in accounts_list if acc['type'] == 'savings')
        current_info = next(acc for acc in accounts_list if acc['type'] == 'current')
        
        self.assertTrue(savings_info['is_active'])
        self.assertFalse(current_info['is_active'])


class TestUserAccountManagement(unittest.TestCase):
    """Test suite for User class account management methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test accounts
        savings_account = Account("savings", 1000.0, 0, "My Savings")
        current_account = Account("current", 500.0, 200.0)
        
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
    
    def test_user_update_account_settings(self):
        """Test user can update account settings"""
        changes = self.user.update_account_settings("savings", nickname="Updated Savings")
        
        self.assertEqual(len(changes), 1)
        self.assertIn("nickname", changes[0])
    
    def test_user_deactivate_account(self):
        """Test user can deactivate account"""
        result = self.user.deactivate_account("savings")
        
        self.assertTrue(result)
        account = self.user.get_account("savings")
        self.assertFalse(account.is_active)
    
    def test_user_reactivate_account(self):
        """Test user can reactivate account"""
        self.user.deactivate_account("savings")
        result = self.user.reactivate_account("savings")
        
        self.assertTrue(result)
        account = self.user.get_account("savings")
        self.assertTrue(account.is_active)
    
    def test_user_get_account_settings(self):
        """Test user can get account settings"""
        settings = self.user.get_account_settings("savings")
        
        self.assertIn('account_type', settings)
        self.assertIn('nickname', settings)
        self.assertIn('is_active', settings)
        self.assertEqual(settings['account_type'], "savings")


if __name__ == '__main__':
    unittest.main()