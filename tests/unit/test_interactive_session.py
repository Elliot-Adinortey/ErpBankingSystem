"""
Unit tests for Interactive Session Management

Tests the InteractiveSession class functionality including menu navigation,
session timeout handling, and user operations.
"""

import unittest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from io import StringIO
import sys

from ui.interactive_session import InteractiveSession, start_interactive_session
from core.user import User
from core.account import Account


class TestInteractiveSession(unittest.TestCase):
    """Test cases for InteractiveSession class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "password123", "test@example.com")
        self.users_dict = {"testuser": self.user}
        self.session = InteractiveSession(self.user, self.users_dict)
        
        # Add test accounts
        self.user.add_account(Account("savings", 1000.0))
        self.user.add_account(Account("current", 500.0, 200.0))
    
    def test_session_initialization(self):
        """Test session initialization"""
        self.assertEqual(self.session.user, self.user)
        self.assertEqual(self.session.users_dict, self.users_dict)
        self.assertTrue(self.session.session_active)
        self.assertIsInstance(self.session.session_start, datetime)
        self.assertIsInstance(self.session.last_activity, datetime)
        self.assertFalse(self.session.warned_timeout)
    
    def test_update_activity(self):
        """Test activity timestamp update"""
        original_time = self.session.last_activity
        self.session._update_activity()
        self.assertGreater(self.session.last_activity, original_time)
        self.assertFalse(self.session.warned_timeout)
    
    def test_session_timeout_check_valid(self):
        """Test session timeout check with valid session"""
        # Session just started, should be valid
        self.assertTrue(self.session._check_session_timeout())
    
    def test_session_timeout_check_expired(self):
        """Test session timeout check with expired session"""
        # Simulate expired session
        expired_time = datetime.now() - timedelta(minutes=35)
        self.session.last_activity = expired_time
        
        with patch('builtins.print') as mock_print:
            result = self.session._check_session_timeout()
            self.assertFalse(result)
            # Verify timeout message was printed
            mock_print.assert_called()
    
    def test_should_show_timeout_warning(self):
        """Test timeout warning logic"""
        # Fresh session - no warning
        self.assertFalse(self.session._should_show_timeout_warning())
        
        # Simulate approaching timeout
        warning_time = datetime.now() - timedelta(minutes=26)
        self.session.last_activity = warning_time
        self.assertTrue(self.session._should_show_timeout_warning())
        
        # After warning shown
        self.session.warned_timeout = True
        self.assertFalse(self.session._should_show_timeout_warning())
    
    @patch('builtins.print')
    def test_display_main_menu(self, mock_print):
        """Test main menu display"""
        self.session.display_main_menu()
        mock_print.assert_called()
        
        # Check that menu options are displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Account Management", printed_text)
        self.assertIn("Banking Operations", printed_text)
        self.assertIn("Transaction History", printed_text)
    
    def test_handle_menu_selection_valid(self):
        """Test valid menu selection handling"""
        with patch.object(self.session, '_handle_account_management', return_value=True):
            result = self.session.handle_menu_selection('1')
            self.assertTrue(result)
    
    def test_handle_menu_selection_invalid(self):
        """Test invalid menu selection handling"""
        with patch('builtins.print') as mock_print:
            result = self.session.handle_menu_selection('9')
            self.assertTrue(result)  # Should continue session
            mock_print.assert_called_with("❌ Invalid choice. Please select 1-6.")
    
    def test_handle_menu_selection_logout(self):
        """Test logout menu selection"""
        with patch.object(self.session, '_handle_logout', return_value=False):
            result = self.session.handle_menu_selection('6')
            self.assertFalse(result)
    
    def test_handle_menu_selection_timeout(self):
        """Test menu selection with session timeout"""
        with patch('builtins.print'):
            with patch.object(self.session, '_check_session_timeout', return_value=False):
                result = self.session.handle_menu_selection('1')
                self.assertFalse(result)
    
    @patch('builtins.input', return_value='y')
    @patch('builtins.print')
    def test_handle_logout_confirm(self, mock_print, mock_input):
        """Test logout confirmation"""
        result = self.session._handle_logout()
        self.assertFalse(result)
        mock_print.assert_called()
    
    @patch('builtins.input', return_value='n')
    @patch('builtins.print')
    def test_handle_logout_cancel(self, mock_print, mock_input):
        """Test logout cancellation"""
        result = self.session._handle_logout()
        self.assertTrue(result)
    
    @patch('builtins.print')
    def test_show_help(self, mock_print):
        """Test help display"""
        self.session._show_help()
        mock_print.assert_called()
        
        # Check that help content is displayed
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("HELP", printed_text)
        self.assertIn("Navigation", printed_text)
    
    @patch('ui.interactive_session.save_users_to_file')
    @patch('builtins.print')
    def test_cleanup_session(self, mock_print, mock_save):
        """Test session cleanup"""
        self.session.cleanup_session()
        
        # Verify data was saved
        mock_save.assert_called_once_with(self.users_dict)
        
        # Verify cleanup messages
        mock_print.assert_called()
        self.assertFalse(self.session.session_active)
    
    @patch('ui.interactive_session.save_users_to_file', side_effect=Exception("Save error"))
    @patch('builtins.print')
    def test_cleanup_session_save_error(self, mock_print, mock_save):
        """Test session cleanup with save error"""
        self.session.cleanup_session()
        
        # Verify error was handled
        mock_print.assert_called()
        printed_text = ''.join(str(call) for call in mock_print.call_args_list)
        self.assertIn("Error saving data", printed_text)
    
    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_select_account_helper(self, mock_print, mock_input):
        """Test account selection helper method"""
        account = self.session._select_account("Test prompt")
        self.assertIsNotNone(account)
        self.assertEqual(account.account_type, "savings")
    
    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    def test_select_account_invalid_choice(self, mock_print, mock_input):
        """Test account selection with invalid choice"""
        # Mock multiple inputs: first invalid, then valid
        mock_input.side_effect = ['0', '1']
        
        account = self.session._select_account("Test prompt")
        self.assertIsNotNone(account)
        
        # Verify error message was shown
        mock_print.assert_called()
    
    def test_select_account_no_accounts(self):
        """Test account selection with no accounts"""
        # Create user with no accounts
        empty_user = User("empty", "password", "empty@test.com")
        empty_session = InteractiveSession(empty_user, {})
        
        with patch('builtins.print') as mock_print:
            result = empty_session._select_account("Test prompt")
            self.assertIsNone(result)
            mock_print.assert_called_with("No accounts available.")


class TestInteractiveSessionIntegration(unittest.TestCase):
    """Integration tests for interactive session"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "password123", "test@example.com")
        self.users_dict = {"testuser": self.user}
        
        # Add test accounts with transactions
        savings_account = Account("savings", 1000.0)
        savings_account.deposit(100.0)
        savings_account.withdraw(50.0)
        
        current_account = Account("current", 500.0, 200.0)
        current_account.deposit(200.0)
        
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
    
    @patch('builtins.input', side_effect=['6', 'y'])  # Go to logout, confirm
    @patch('ui.interactive_session.save_users_to_file')
    @patch('builtins.print')
    def test_full_session_flow(self, mock_print, mock_save, mock_input):
        """Test complete session flow from start to logout"""
        session = InteractiveSession(self.user, self.users_dict)
        session.run_session()
        
        # Verify session completed
        self.assertFalse(session.session_active)
        mock_save.assert_called()
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('ui.interactive_session.save_users_to_file')
    @patch('builtins.print')
    def test_session_keyboard_interrupt(self, mock_print, mock_save, mock_input):
        """Test session handling of keyboard interrupt"""
        session = InteractiveSession(self.user, self.users_dict)
        session.run_session()
        
        # Verify cleanup was called
        mock_save.assert_called()
        self.assertFalse(session.session_active)
    
    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_account_management_menu(self, mock_print, mock_input):
        """Test account management submenu navigation"""
        session = InteractiveSession(self.user, self.users_dict)
        
        # Mock the submenu to return to main menu
        with patch.object(session, '_list_accounts') as mock_list:
            # Simulate: select account management, then list accounts, then back
            mock_input.side_effect = ['1', '6']  # Account mgmt, then back
            
            result = session._handle_account_management()
            self.assertTrue(result)
    
    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_banking_operations_menu(self, mock_print, mock_input):
        """Test banking operations submenu navigation"""
        session = InteractiveSession(self.user, self.users_dict)
        
        # Mock the submenu to return to main menu
        with patch.object(session, '_deposit_money') as mock_deposit:
            # Simulate: select banking operations, then deposit, then back
            mock_input.side_effect = ['1', '6']  # Banking ops, then back
            
            result = session._handle_banking_operations()
            self.assertTrue(result)
    
    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_transaction_history_menu(self, mock_print, mock_input):
        """Test transaction history submenu navigation"""
        session = InteractiveSession(self.user, self.users_dict)
        
        # Mock the submenu to return to main menu
        with patch.object(session, '_view_all_transactions') as mock_view:
            # Simulate: select transaction history, then view all, then back
            mock_input.side_effect = ['1', '7']  # Transaction history, then back
            
            result = session._handle_transaction_history()
            self.assertTrue(result)


class TestStartInteractiveSession(unittest.TestCase):
    """Test the start_interactive_session function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "password123", "test@example.com")
        self.users_dict = {"testuser": self.user}
    
    @patch('ui.interactive_session.InteractiveSession')
    def test_start_interactive_session(self, mock_session_class):
        """Test start_interactive_session function"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        start_interactive_session(self.user, self.users_dict)
        
        # Verify session was created and started
        mock_session_class.assert_called_once_with(self.user, self.users_dict)
        mock_session.run_session.assert_called_once()


if __name__ == '__main__':
    unittest.main()