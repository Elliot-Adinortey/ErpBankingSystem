import unittest
from unittest.mock import patch, MagicMock
import io
import sys
from datetime import datetime
from user import User
from account import Account
from main import account_summary, financial_overview, list_accounts


class TestEnhancedCLICommands(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test accounts with different configurations
        savings_account = Account("savings", 1000.0, nickname="Emergency Fund")
        current_account = Account("current", 500.0, overdraft_limit=200.0, nickname="Daily Spending")
        salary_account = Account("salary", 2500.0)
        
        # Add some transactions for testing
        savings_account.deposit(100.0)
        current_account.withdraw(50.0)
        salary_account.deposit(2500.0)
        
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
    def test_account_summary_with_accounts(self, mock_auth):
        """Test account_summary command with multiple accounts"""
        mock_auth.return_value = self.user
        args = MagicMock()
        
        output = self.capture_output(account_summary, args)
        
        # Check that summary contains expected information
        self.assertIn("Account Summary for testuser", output)
        self.assertIn("Total Accounts: 3", output)
        self.assertIn("Emergency Fund (savings)", output)
        self.assertIn("Daily Spending (current)", output)
        self.assertIn("Salary", output)
        self.assertIn("Overdraft Limit: $200.00", output)
        self.assertIn("Available Balance: $650.00", output)  # 450 + 200 overdraft

    @patch('main.authenticate_user')
    def test_account_summary_no_accounts(self, mock_auth):
        """Test account_summary command with no accounts"""
        empty_user = User("emptyuser", "TestPass123", "empty@example.com")
        mock_auth.return_value = empty_user
        args = MagicMock()
        
        output = self.capture_output(account_summary, args)
        
        self.assertIn("No accounts found", output)
        self.assertIn("add_account", output)

    @patch('main.authenticate_user')
    def test_financial_overview_with_accounts(self, mock_auth):
        """Test financial_overview command with multiple accounts"""
        mock_auth.return_value = self.user
        args = MagicMock()
        
        output = self.capture_output(financial_overview, args)
        
        # Check financial overview content
        self.assertIn("Financial Overview for testuser", output)
        self.assertIn("Total Balance:", output)
        self.assertIn("Total Available:", output)
        self.assertIn("Account Breakdown:", output)
        self.assertIn("Emergency Fund (savings)", output)
        self.assertIn("Daily Spending (current)", output)
        self.assertIn("Recent Activity", output)

    @patch('main.authenticate_user')
    def test_financial_overview_no_accounts(self, mock_auth):
        """Test financial_overview command with no accounts"""
        empty_user = User("emptyuser", "TestPass123", "empty@example.com")
        mock_auth.return_value = empty_user
        args = MagicMock()
        
        output = self.capture_output(financial_overview, args)
        
        self.assertIn("No accounts found", output)

    @patch('main.authenticate_user')
    def test_enhanced_list_accounts_with_nicknames(self, mock_auth):
        """Test enhanced list_accounts command showing nicknames"""
        mock_auth.return_value = self.user
        args = MagicMock()
        
        output = self.capture_output(list_accounts, args)
        
        # Check that nicknames are displayed
        self.assertIn("Emergency Fund (savings)", output)
        self.assertIn("Daily Spending (current)", output)
        self.assertIn("Salary", output)  # No nickname, should show type
        self.assertIn("Total:", output)

    @patch('main.authenticate_user')
    def test_authenticate_user_failure(self, mock_auth):
        """Test commands when authentication fails"""
        mock_auth.return_value = None
        args = MagicMock()
        
        # Test that functions handle authentication failure gracefully
        output_summary = self.capture_output(account_summary, args)
        output_overview = self.capture_output(financial_overview, args)
        output_list = self.capture_output(list_accounts, args)
        
        # Should not contain account information when auth fails
        self.assertEqual(output_summary, "")
        self.assertEqual(output_overview, "")
        self.assertEqual(output_list, "")

    def test_account_manager_summary_generation(self):
        """Test AccountManager summary generation directly"""
        summary = self.user.get_enhanced_summary()
        
        self.assertEqual(summary['total_accounts'], 3)
        self.assertGreater(summary['total_balance'], 0)
        self.assertEqual(len(summary['accounts']), 3)
        
        # Check account details
        savings_info = next(acc for acc in summary['accounts'] if acc['type'] == 'savings')
        self.assertEqual(savings_info['nickname'], "Emergency Fund")
        self.assertEqual(savings_info['display_name'], "Emergency Fund (savings)")
        
        current_info = next(acc for acc in summary['accounts'] if acc['type'] == 'current')
        self.assertEqual(current_info['overdraft_limit'], 200.0)
        self.assertEqual(current_info['available_balance'], 650.0)  # 450 + 200

    def test_financial_overview_generation(self):
        """Test financial overview generation directly"""
        overview = self.user.get_financial_overview()
        
        self.assertGreater(overview['total_balance'], 0)
        self.assertGreater(overview['total_available'], overview['total_balance'])  # Due to overdraft
        self.assertEqual(len(overview['account_breakdown']), 3)
        self.assertIsInstance(overview['recent_activity'], list)
        
        # Check that current account has higher available than balance
        current_breakdown = overview['account_breakdown']['Daily Spending (current)']
        self.assertEqual(current_breakdown['available'], 650.0)  # 450 + 200 overdraft
        self.assertEqual(current_breakdown['balance'], 450.0)

    def test_account_display_names(self):
        """Test account display name functionality"""
        savings = self.user.accounts[0]  # Emergency Fund
        current = self.user.accounts[1]  # Daily Spending
        salary = self.user.accounts[2]   # No nickname
        
        self.assertEqual(savings.get_display_name(), "Emergency Fund (savings)")
        self.assertEqual(current.get_display_name(), "Daily Spending (current)")
        self.assertEqual(salary.get_display_name(), "Salary")

    def test_account_summary_formatting(self):
        """Test that account summary contains proper formatting"""
        summary = self.user.get_enhanced_summary()
        
        for account_info in summary['accounts']:
            # Check required fields are present
            self.assertIn('type', account_info)
            self.assertIn('display_name', account_info)
            self.assertIn('balance', account_info)
            self.assertIn('transaction_count', account_info)
            self.assertIn('created_date', account_info)
            self.assertIn('last_activity', account_info)
            
            # Check date formatting
            self.assertRegex(account_info['created_date'], r'\d{4}-\d{2}-\d{2}')
            self.assertRegex(account_info['last_activity'], r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')


if __name__ == '__main__':
    unittest.main()