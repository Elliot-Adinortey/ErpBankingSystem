"""
Integration tests for Interactive Menu Operations

Tests the individual menu operations and their functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from io import StringIO
import sys

from interactive_session import InteractiveSession
from user import User
from account import Account


class TestInteractiveMenuOperations(unittest.TestCase):
    """Integration tests for individual menu operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "password123", "test@example.com")
        self.users_dict = {"testuser": self.user}
        self.session = InteractiveSession(self.user, self.users_dict)
        
        # Add test accounts with transactions
        savings_account = Account("savings", 1000.0, 0, "My Savings")
        savings_account.deposit(100.0)
        savings_account.withdraw(50.0)
        
        current_account = Account("current", 500.0, 200.0, "Daily Spending")
        current_account.deposit(200.0)
        
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_account_management_list_accounts(self, mock_print, mock_input):
        """Test listing accounts in account management menu"""
        # Test the list accounts method directly
        self.session._list_accounts()
        
        # Verify account information was displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("My Savings", printed_text)
        self.assertIn("Daily Spending", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_create_account_operation(self, mock_print, mock_input):
        """Test creating account operation"""
        # Simulate creating a salary account
        mock_input.side_effect = [
            '3',  # Salary account
            '1000',  # Initial balance
            'Work Account',  # Nickname
            ''  # Press Enter to continue
        ]
        
        self.session._create_account()
        
        # Verify account was created
        salary_account = self.user.get_account('salary')
        self.assertIsNotNone(salary_account)
        self.assertEqual(salary_account.balance, 1000.0)
        self.assertEqual(salary_account.nickname, 'Work Account')
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_deposit_operation(self, mock_print, mock_input):
        """Test deposit operation"""
        original_balance = self.user.get_account('savings').balance
        
        # Simulate deposit to savings account
        mock_input.side_effect = [
            '1',  # Select first account (savings)
            '100',  # Deposit amount
            ''  # Press Enter to continue
        ]
        
        self.session._deposit_money()
        
        # Verify deposit was made
        new_balance = self.user.get_account('savings').balance
        self.assertEqual(new_balance, original_balance + 100.0)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_withdraw_operation(self, mock_print, mock_input):
        """Test withdrawal operation"""
        original_balance = self.user.get_account('savings').balance
        
        # Simulate withdrawal from savings account
        mock_input.side_effect = [
            '1',  # Select first account (savings)
            '50',  # Withdrawal amount
            ''  # Press Enter to continue
        ]
        
        self.session._withdraw_money()
        
        # Verify withdrawal was made
        new_balance = self.user.get_account('savings').balance
        self.assertEqual(new_balance, original_balance - 50.0)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_transfer_operation(self, mock_print, mock_input):
        """Test transfer operation"""
        savings_balance = self.user.get_account('savings').balance
        current_balance = self.user.get_account('current').balance
        
        # Simulate transfer from savings to current
        mock_input.side_effect = [
            '1',  # From savings (first account)
            '1',  # To current (first in remaining accounts)
            '100',  # Transfer amount
            'Test transfer',  # Memo
            ''  # Press Enter to continue
        ]
        
        self.session._transfer_money()
        
        # Verify transfer was made
        new_savings_balance = self.user.get_account('savings').balance
        new_current_balance = self.user.get_account('current').balance
        
        self.assertEqual(new_savings_balance, savings_balance - 100.0)
        self.assertEqual(new_current_balance, current_balance + 100.0)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_view_all_transactions_operation(self, mock_print, mock_input):
        """Test viewing all transactions operation"""
        self.session._view_all_transactions()
        
        # Verify transaction data was displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("transactions", printed_text.lower())
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_filter_by_account_operation(self, mock_print, mock_input):
        """Test filtering transactions by account"""
        # Simulate selecting savings account for filtering
        mock_input.side_effect = [
            '1',  # Select first account (savings)
            ''  # Press Enter to continue
        ]
        
        self.session._filter_by_account()
        
        # Verify filtering was applied
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("My Savings", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_transaction_summary_operation(self, mock_print, mock_input):
        """Test transaction summary"""
        self.session._transaction_summary()
        
        # Verify summary was displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Transaction Summary", printed_text)
        self.assertIn("Total Transactions", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_update_nicknames_operation(self, mock_print, mock_input):
        """Test updating account nicknames"""
        # Simulate updating savings account nickname
        mock_input.side_effect = [
            '1',  # Select first account (savings)
            'Updated Savings',  # New nickname
            ''  # Press Enter to continue
        ]
        
        self.session._update_nicknames()
        
        # Verify nickname was updated
        savings_account = self.user.get_account('savings')
        self.assertEqual(savings_account.nickname, 'Updated Savings')
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_view_profile_operation(self, mock_print, mock_input):
        """Test viewing profile information"""
        self.session._view_profile()
        
        # Verify profile information was displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("testuser", printed_text)
        self.assertIn("test@example.com", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_session_info_operation(self, mock_print, mock_input):
        """Test viewing session information"""
        self.session._session_info()
        
        # Verify session information was displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Session Information", printed_text)
        self.assertIn("Session started", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_account_details_operation(self, mock_print, mock_input):
        """Test viewing account details"""
        self.session._account_details()
        
        # Verify account details were displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Account Summary", printed_text)
        self.assertIn("My Savings", printed_text)
        self.assertIn("Daily Spending", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_account_selection_edge_cases(self, mock_print, mock_input):
        """Test edge cases in account selection"""
        # Test with no accounts
        empty_user = User("empty", "password", "empty@test.com")
        empty_session = InteractiveSession(empty_user, {})
        
        # Test deposit with no accounts
        empty_session._deposit_money()
        
        # Verify no accounts message was shown
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("No accounts found", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_transfer_insufficient_accounts(self, mock_print, mock_input):
        """Test transfer with insufficient accounts"""
        # Create user with only one account
        single_user = User("single", "password", "single@test.com")
        single_user.add_account(Account("savings", 1000.0))
        single_session = InteractiveSession(single_user, {})
        
        # Test transfer with insufficient accounts
        single_session._transfer_money()
        
        # Verify insufficient accounts message was shown
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("at least 2 accounts", printed_text)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_financial_overview_operation(self, mock_print, mock_input):
        """Test financial overview operation"""
        self.session._financial_overview()
        
        # Verify overview was displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Financial Overview", printed_text)
        self.assertIn("Total Balance", printed_text)


if __name__ == '__main__':
    unittest.main()