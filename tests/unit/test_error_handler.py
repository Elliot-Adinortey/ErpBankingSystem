"""
Unit tests for the comprehensive error handling system
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.utils.error_handler import ErrorHandler, ErrorContext, CommandValidator


class TestErrorHandler(unittest.TestCase):
    """Test cases for ErrorHandler class"""
    
    def test_handle_session_expired_with_username(self):
        """Test session expired error with username"""
        result = ErrorHandler.handle_session_expired("john_doe")
        
        self.assertIn("Session Expired", result)
        self.assertIn("john_doe", result)
        self.assertIn("python main.py login", result)
        self.assertIn("30 minutes", result)
        
    def test_handle_session_expired_without_username(self):
        """Test session expired error without username"""
        result = ErrorHandler.handle_session_expired()
        
        self.assertIn("Session Expired", result)
        self.assertIn("python main.py login", result)
        self.assertIn("security reasons", result)
        
    def test_handle_insufficient_funds_basic(self):
        """Test insufficient funds error with basic information"""
        result = ErrorHandler.handle_insufficient_funds(100.0, 150.0, "savings")
        
        self.assertIn("Insufficient Funds", result)
        self.assertIn("$100.00", result)
        self.assertIn("$150.00", result)
        self.assertIn("$50.00", result)  # shortage
        self.assertIn("savings", result)
        
    def test_handle_insufficient_funds_with_suggestions(self):
        """Test insufficient funds error includes helpful suggestions"""
        result = ErrorHandler.handle_insufficient_funds(75.50, 100.0, "current")
        
        self.assertIn("Try withdrawing $75.50", result)
        self.assertIn("Deposit money first", result)
        self.assertIn("Transfer from another account", result)
        self.assertIn("overdraft limit", result)  # current account suggestion
        
    def test_handle_insufficient_funds_zero_balance(self):
        """Test insufficient funds with zero balance"""
        result = ErrorHandler.handle_insufficient_funds(0.0, 50.0, "savings")
        
        self.assertIn("$0.00", result)
        self.assertIn("$50.00", result)
        self.assertIn("Deposit money first", result)
        
    def test_handle_invalid_account_with_suggestions(self):
        """Test invalid account error with available accounts"""
        available_accounts = ["savings", "current", "My Salary Account"]
        result = ErrorHandler.handle_invalid_account("saving", available_accounts)
        
        self.assertIn("Account Not Found", result)
        self.assertIn("saving", result)
        self.assertIn("Available accounts", result)
        self.assertIn("savings", result)
        self.assertIn("current", result)
        self.assertIn("My Salary Account", result)
        
    def test_handle_invalid_account_no_accounts(self):
        """Test invalid account error when no accounts exist"""
        result = ErrorHandler.handle_invalid_account("savings", [])
        
        self.assertIn("don't have any accounts", result)
        self.assertIn("Create an account first", result)
        self.assertIn("add_account", result)
        self.assertIn("savings, current, salary", result)
        
    def test_handle_invalid_amount_basic(self):
        """Test invalid amount error with examples"""
        result = ErrorHandler.handle_invalid_amount("abc", "deposit")
        
        self.assertIn("Invalid Amount", result)
        self.assertIn("abc", result)
        self.assertIn("deposit", result)
        self.assertIn("Valid formats", result)
        self.assertIn("100.50", result)
        
    def test_handle_invalid_amount_with_context(self):
        """Test invalid amount error with different contexts"""
        result = ErrorHandler.handle_invalid_amount("-50", "withdrawal")
        
        self.assertIn("withdrawal", result)
        self.assertIn("negative amounts not allowed", result)
        self.assertIn("Examples", result)
        
    def test_handle_command_not_found_with_suggestions(self):
        """Test command not found with similar command suggestions"""
        result = ErrorHandler.handle_command_not_found("loginn")
        
        self.assertIn("Unknown Command", result)
        self.assertIn("loginn", result)
        self.assertIn("Available commands", result)
        self.assertIn("login", result)
        
    def test_handle_command_not_found_no_suggestions(self):
        """Test command not found with no similar commands"""
        result = ErrorHandler.handle_command_not_found("xyz123")
        
        self.assertIn("Unknown Command", result)
        self.assertIn("xyz123", result)
        self.assertIn("Available commands", result)
        
    def test_handle_invalid_account_type(self):
        """Test invalid account type error"""
        result = ErrorHandler.handle_invalid_account_type("checking")
        
        self.assertIn("Invalid Account Type", result)
        self.assertIn("checking", result)
        self.assertIn("Valid account types", result)
        self.assertIn("savings", result)
        self.assertIn("current", result)
        self.assertIn("salary", result)
        
    def test_handle_validation_error_password(self):
        """Test validation error for password field"""
        requirements = [
            "At least 8 characters long",
            "Contains uppercase letters",
            "Contains numbers"
        ]
        result = ErrorHandler.handle_validation_error("password", "weak", requirements)
        
        self.assertIn("Validation Error", result)
        self.assertIn("password", result)
        self.assertIn("weak", result)
        self.assertIn("At least 8 characters", result)
        self.assertIn("Password tips", result)
        
    def test_handle_validation_error_generic_field(self):
        """Test validation error for generic field"""
        requirements = ["Must be positive", "Must be numeric"]
        result = ErrorHandler.handle_validation_error("amount", "abc", requirements)
        
        self.assertIn("Validation Error", result)
        self.assertIn("amount", result)
        self.assertIn("abc", result)
        self.assertIn("Must be positive", result)
        self.assertIn("Must be numeric", result)
        
    def test_handle_network_error_basic(self):
        """Test network error handling"""
        result = ErrorHandler.handle_network_error("login", 0)
        
        self.assertIn("Network Error", result)
        self.assertIn("login", result)
        self.assertIn("internet connection", result)
        self.assertIn("automatically retry", result)
        
    def test_handle_network_error_with_retries(self):
        """Test network error with retry count"""
        result = ErrorHandler.handle_network_error("transfer", 2)
        
        self.assertIn("Network Error", result)
        self.assertIn("transfer", result)
        self.assertIn("Retry attempts: 2", result)
        self.assertIn("1 attempts remaining", result)
        
    def test_handle_network_error_max_retries(self):
        """Test network error at max retries"""
        result = ErrorHandler.handle_network_error("deposit", 3)
        
        self.assertIn("Network Error", result)
        self.assertIn("deposit", result)
        self.assertIn("Retry attempts: 3", result)
        self.assertNotIn("automatically retry", result)
        
    def test_suggest_command_fix_with_match(self):
        """Test command suggestion with close match"""
        result = ErrorHandler.suggest_command_fix("loginn")
        
        self.assertIn("Did you mean", result)
        self.assertIn("login", result)
        
    def test_suggest_command_fix_no_match(self):
        """Test command suggestion with no close match"""
        result = ErrorHandler.suggest_command_fix("xyz123")
        
        self.assertEqual(result, "")
        
    def test_get_help_text_login(self):
        """Test help text for login command"""
        result = ErrorHandler.get_help_text("login")
        
        self.assertIn("LOGIN COMMAND", result)
        self.assertIn("Usage:", result)
        self.assertIn("python main.py login", result)
        self.assertIn("Examples:", result)
        self.assertIn("Session token", result)
        
    def test_get_help_text_register(self):
        """Test help text for register command"""
        result = ErrorHandler.get_help_text("register")
        
        self.assertIn("REGISTER COMMAND", result)
        self.assertIn("Password Requirements", result)
        self.assertIn("8 characters", result)
        self.assertIn("uppercase", result)
        
    def test_get_help_text_unknown_command(self):
        """Test help text for unknown command"""
        result = ErrorHandler.get_help_text("unknown_cmd")
        
        self.assertIn("No detailed help available", result)
        self.assertIn("unknown_cmd", result)
        
    def test_find_similar_commands(self):
        """Test finding similar commands"""
        # Test direct method access for internal testing
        suggestions = ErrorHandler._find_similar_commands("loginn")
        
        self.assertIn("login", suggestions)
        
    def test_find_similar_accounts(self):
        """Test finding similar account names"""
        accounts = ["savings", "current", "My Salary"]
        suggestions = ErrorHandler._find_similar_accounts("saving", accounts)
        
        self.assertIn("savings", suggestions)
        
    def test_calculate_similarity_exact_match(self):
        """Test similarity calculation for exact match"""
        similarity = ErrorHandler._calculate_similarity("login", "login")
        self.assertEqual(similarity, 1.0)
        
    def test_calculate_similarity_no_match(self):
        """Test similarity calculation for no match"""
        similarity = ErrorHandler._calculate_similarity("abc", "xyz")
        self.assertLess(similarity, 0.5)
        
    def test_calculate_similarity_partial_match(self):
        """Test similarity calculation for partial match"""
        similarity = ErrorHandler._calculate_similarity("login", "loginn")
        self.assertGreater(similarity, 0.5)


class TestErrorContext(unittest.TestCase):
    """Test cases for ErrorContext class"""
    
    def test_error_context_initialization(self):
        """Test ErrorContext initialization"""
        context = ErrorContext("test_operation", "test_user", {"key": "value"})
        
        self.assertEqual(context.operation, "test_operation")
        self.assertEqual(context.user, "test_user")
        self.assertEqual(context.additional_info["key"], "value")
        self.assertIsInstance(context.start_time, datetime)
        
    def test_error_context_no_error(self):
        """Test ErrorContext when no error occurs"""
        with patch('builtins.print') as mock_print:
            with ErrorContext("test_op", "user"):
                pass  # No error
            
            mock_print.assert_not_called()
            
    def test_error_context_with_error(self):
        """Test ErrorContext when error occurs"""
        with patch('builtins.print') as mock_print:
            try:
                with ErrorContext("test_op", "user", {"info": "test"}):
                    raise ValueError("Test error")
            except ValueError:
                pass  # Expected
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            self.assertIn("Error Context", call_args)
            self.assertIn("test_op", call_args)
            self.assertIn("user", call_args)
            self.assertIn("ValueError", call_args)


class TestCommandValidator(unittest.TestCase):
    """Test cases for CommandValidator class"""
    
    def test_validate_amount_valid_integer(self):
        """Test amount validation with valid integer"""
        is_valid, amount, error = CommandValidator.validate_amount("100")
        
        self.assertTrue(is_valid)
        self.assertEqual(amount, 100.0)
        self.assertEqual(error, "")
        
    def test_validate_amount_valid_decimal(self):
        """Test amount validation with valid decimal"""
        is_valid, amount, error = CommandValidator.validate_amount("150.75")
        
        self.assertTrue(is_valid)
        self.assertEqual(amount, 150.75)
        self.assertEqual(error, "")
        
    def test_validate_amount_negative(self):
        """Test amount validation with negative number"""
        is_valid, amount, error = CommandValidator.validate_amount("-50")
        
        self.assertFalse(is_valid)
        self.assertEqual(amount, 0)
        self.assertIn("Invalid Amount", error)
        
    def test_validate_amount_zero(self):
        """Test amount validation with zero"""
        is_valid, amount, error = CommandValidator.validate_amount("0")
        
        self.assertFalse(is_valid)
        self.assertEqual(amount, 0)
        self.assertIn("greater than zero", error)
        
    def test_validate_amount_invalid_string(self):
        """Test amount validation with invalid string"""
        is_valid, amount, error = CommandValidator.validate_amount("abc")
        
        self.assertFalse(is_valid)
        self.assertEqual(amount, 0)
        self.assertIn("Invalid Amount", error)
        
    def test_validate_account_type_valid(self):
        """Test account type validation with valid type"""
        is_valid, error = CommandValidator.validate_account_type("savings")
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
    def test_validate_account_type_valid_case_insensitive(self):
        """Test account type validation is case insensitive"""
        is_valid, error = CommandValidator.validate_account_type("CURRENT")
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
    def test_validate_account_type_invalid(self):
        """Test account type validation with invalid type"""
        is_valid, error = CommandValidator.validate_account_type("checking")
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid Account Type", error)
        self.assertIn("checking", error)
        
    def test_validate_command_exists_valid(self):
        """Test command validation with valid command"""
        commands = ["login", "register", "deposit"]
        is_valid, error = CommandValidator.validate_command_exists("login", commands)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
    def test_validate_command_exists_invalid(self):
        """Test command validation with invalid command"""
        commands = ["login", "register", "deposit"]
        is_valid, error = CommandValidator.validate_command_exists("unknown", commands)
        
        self.assertFalse(is_valid)
        self.assertIn("Unknown Command", error)
        self.assertIn("unknown", error)


class TestErrorHandlerIntegration(unittest.TestCase):
    """Integration tests for error handling system"""
    
    def test_error_flow_insufficient_funds_to_suggestion(self):
        """Test complete error flow from insufficient funds to suggestion"""
        # Simulate insufficient funds scenario
        available = 50.0
        requested = 100.0
        account = "savings"
        
        error_msg = ErrorHandler.handle_insufficient_funds(available, requested, account)
        
        # Verify error message contains all expected elements
        self.assertIn("Insufficient Funds", error_msg)
        self.assertIn("$50.00", error_msg)
        self.assertIn("$100.00", error_msg)
        self.assertIn("Try withdrawing $50.00", error_msg)
        self.assertIn("Deposit money first", error_msg)
        
    def test_error_flow_invalid_command_to_help(self):
        """Test complete error flow from invalid command to help"""
        invalid_cmd = "loginn"
        
        # Get command error
        error_msg = ErrorHandler.handle_command_not_found(invalid_cmd)
        
        # Get suggestion
        suggestion = ErrorHandler.suggest_command_fix(invalid_cmd)
        
        # Get help for correct command
        help_text = ErrorHandler.get_help_text("login")
        
        # Verify flow provides comprehensive assistance
        self.assertIn("Unknown Command", error_msg)
        self.assertIn("login", suggestion)
        self.assertIn("LOGIN COMMAND", help_text)
        
    def test_validation_and_error_integration(self):
        """Test integration between validation and error handling"""
        # Test invalid amount validation
        is_valid, amount, error = CommandValidator.validate_amount("abc")
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid Amount", error)
        self.assertIn("Valid formats", error)
        
        # Test invalid account type validation
        is_valid, error = CommandValidator.validate_account_type("checking")
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid Account Type", error)
        self.assertIn("savings", error)


if __name__ == '__main__':
    unittest.main()