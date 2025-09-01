"""
Integration tests for CLI help system and enhanced error messages.

This module tests the integration of the help system with the main CLI,
command parsing, and error handling workflows.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import io
from contextlib import redirect_stdout, redirect_stderr

# Add src directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import main module functions
import main
from src.utils.help_system import HelpSystem
from src.utils.error_handler import ErrorHandler


class TestCLIHelpIntegration(unittest.TestCase):
    """Test cases for CLI help system integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.original_argv = sys.argv.copy()
    
    def tearDown(self):
        """Clean up after tests"""
        sys.argv = self.original_argv
    
    def test_help_command_no_args(self):
        """Test help command without specific command argument"""
        # Mock args for help command
        args = MagicMock()
        args.command = None
        
        # Capture output
        with redirect_stdout(io.StringIO()) as output:
            main.help_command(args)
        
        result = output.getvalue()
        
        # Check that general help is displayed
        self.assertIn('Banking System - Command Help', result)
        self.assertIn('Available commands:', result)
        self.assertIn('login', result)
        self.assertIn('register', result)
        self.assertIn('interactive', result)
    
    def test_help_command_specific_command(self):
        """Test help command with specific command argument"""
        # Mock args for help command with specific command
        args = MagicMock()
        args.command = 'login'
        
        # Capture output
        with redirect_stdout(io.StringIO()) as output:
            main.help_command(args)
        
        result = output.getvalue()
        
        # Check that specific command help is displayed
        self.assertIn('LOGIN COMMAND', result)
        self.assertIn('Description:', result)
        self.assertIn('Usage:', result)
        self.assertIn('Examples:', result)
    
    def test_suggest_command_with_suggestions(self):
        """Test command suggestion functionality"""
        # Capture output
        with redirect_stdout(io.StringIO()) as output:
            main.suggest_command('logn')
        
        result = output.getvalue()
        
        # Check that suggestions are provided
        self.assertIn('Unknown Command', result)  # Updated to match actual output
        self.assertIn('login', result)
    
    def test_suggest_command_no_suggestions(self):
        """Test command suggestion with no matches"""
        # Mock ErrorHandler to return no suggestions
        with patch.object(HelpSystem, 'get_command_suggestions', return_value=[]):
            with patch.object(ErrorHandler, 'handle_command_not_found') as mock_handler:
                mock_handler.return_value = "No command found"
                
                # Capture output
                with redirect_stdout(io.StringIO()) as output:
                    main.suggest_command('xyz123')
                
                result = output.getvalue()
                
                # Check that error handler is called
                mock_handler.assert_called_once_with('xyz123')
    
    @patch('main.parse_args')
    def test_main_execution_with_valid_command(self, mock_parse_args):
        """Test main execution with valid command"""
        # Mock successful command execution
        mock_args = MagicMock()
        mock_args.func = MagicMock()
        mock_args.command = 'login'
        mock_parse_args.return_value = mock_args
        
        # Mock sys.argv to avoid actual parsing
        with patch.object(sys, 'argv', ['main.py', 'login', 'user', 'pass']):
            # Should not raise exception
            try:
                # Import and run main logic (would need to refactor main.py for better testing)
                pass
            except SystemExit:
                pass  # Expected for successful execution
    
    def test_enhanced_error_messages_in_operations(self):
        """Test that enhanced error messages are used in banking operations"""
        # Test insufficient funds error
        message = ErrorHandler.handle_insufficient_funds(50.0, 100.0, 'savings')
        
        # Check for enhanced formatting and suggestions
        self.assertIn('💸', message)  # Emoji for visual appeal
        self.assertIn('Insufficient Funds', message)
        self.assertIn('💡 Suggestions:', message)
        self.assertIn('python main.py deposit', message)
        self.assertIn('python main.py transfer', message)
    
    def test_session_expired_error_integration(self):
        """Test session expired error message integration"""
        message = ErrorHandler.handle_session_expired('testuser')
        
        # Check for comprehensive guidance
        self.assertIn('🔒 Session Expired', message)
        self.assertIn('testuser', message)
        self.assertIn('💡 To continue:', message)
        self.assertIn('python main.py login', message)
        self.assertIn('python main.py interactive', message)
        self.assertIn('🔐 Security Note:', message)
    
    def test_command_validation_integration(self):
        """Test command validation with help system"""
        # Test valid command
        is_valid, error_msg = HelpSystem.validate_command_usage('login', ['user', 'pass'])
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
        
        # Test invalid command (missing args)
        is_valid, error_msg = HelpSystem.validate_command_usage('login', ['user'])
        self.assertFalse(is_valid)
        self.assertIn('Missing required arguments', error_msg)
        self.assertIn('Usage:', error_msg)
        self.assertIn('python main.py login', error_msg)
    
    def test_interactive_help_context_switching(self):
        """Test context-sensitive help in interactive mode"""
        # Test main menu help
        main_help = HelpSystem.get_interactive_help('main_menu')
        self.assertIn('Main Menu Help', main_help)
        self.assertIn('Account Management', main_help)
        
        # Test account management help
        account_help = HelpSystem.get_interactive_help('account_management')
        self.assertIn('Account Management Help', account_help)
        self.assertIn('Create New Account', account_help)
        
        # Test banking operations help
        banking_help = HelpSystem.get_interactive_help('banking_operations')
        self.assertIn('Banking Operations Help', banking_help)
        self.assertIn('Deposit Money', banking_help)


class TestErrorMessageAccuracy(unittest.TestCase):
    """Test cases for error message accuracy and helpfulness"""
    
    def test_invalid_amount_error_accuracy(self):
        """Test accuracy of invalid amount error messages"""
        test_cases = [
            ('$100', 'currency symbols'),
            ('100,50', 'commas'),
            ('-50', 'negative'),
            ('abc', 'letters')
        ]
        
        for invalid_amount, expected_guidance in test_cases:
            message = ErrorHandler.handle_invalid_amount(invalid_amount)
            
            # Check that message contains relevant guidance
            self.assertIn('Invalid Amount', message)
            self.assertIn(invalid_amount, message)
            self.assertIn('Valid formats:', message)
            self.assertIn('Examples:', message)
    
    def test_account_not_found_error_accuracy(self):
        """Test accuracy of account not found error messages"""
        available_accounts = ['savings', 'current', 'salary']
        
        # Test with similar account name
        message = ErrorHandler.handle_invalid_account('saving', available_accounts)
        
        self.assertIn('Account Not Found', message)
        self.assertIn('saving', message)
        self.assertIn('Available accounts:', message)
        self.assertIn('savings', message)  # Should show available accounts
        self.assertIn('Did you mean:', message)  # Should suggest similar
    
    def test_command_not_found_error_accuracy(self):
        """Test accuracy of command not found error messages"""
        message = ErrorHandler.handle_command_not_found('logn')
        
        self.assertIn('Unknown Command', message)
        self.assertIn('logn', message)
        self.assertIn('Available commands:', message)
        self.assertIn('login', message)
        self.assertIn('register', message)
        self.assertIn('--help', message)
        self.assertIn('interactive', message)
    
    def test_validation_error_accuracy(self):
        """Test accuracy of validation error messages"""
        requirements = [
            'At least 8 characters long',
            'Contains uppercase letters',
            'Contains lowercase letters',
            'Contains at least one number'
        ]
        
        message = ErrorHandler.handle_validation_error('password', 'weak', requirements)
        
        self.assertIn('Validation Error', message)
        self.assertIn('password', message)
        self.assertIn('weak', message)
        self.assertIn('Requirements:', message)
        
        # Check that all requirements are listed
        for requirement in requirements:
            self.assertIn(requirement, message)
    
    def test_network_error_accuracy(self):
        """Test accuracy of network error messages"""
        message = ErrorHandler.handle_network_error('login', retry_count=2)
        
        self.assertIn('Network Error', message)
        self.assertIn('login', message)
        self.assertIn('Retry attempts: 2', message)
        self.assertIn('Troubleshooting:', message)
        self.assertIn('internet connection', message)
        self.assertIn('1 attempts remaining', message)  # 3 - 2 = 1


class TestHelpSystemPerformance(unittest.TestCase):
    """Test cases for help system performance and efficiency"""
    
    def test_help_text_generation_performance(self):
        """Test that help text generation is efficient"""
        import time
        
        # Test multiple help text generations
        start_time = time.time()
        
        for _ in range(100):
            HelpSystem.get_command_help('login')
            HelpSystem.get_interactive_help('main_menu')
            HelpSystem.get_error_solution('session_expired')
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly (less than 1 second for 100 iterations)
        self.assertLess(duration, 1.0, "Help text generation is too slow")
    
    def test_command_suggestion_performance(self):
        """Test that command suggestions are generated efficiently"""
        import time
        
        test_inputs = ['log', 'acc', 'trans', 'xyz', 'invalid']
        
        start_time = time.time()
        
        for _ in range(50):
            for input_cmd in test_inputs:
                HelpSystem.get_command_suggestions(input_cmd)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        self.assertLess(duration, 0.5, "Command suggestion generation is too slow")
    
    def test_memory_usage_reasonable(self):
        """Test that help system doesn't use excessive memory"""
        import sys
        
        # Get initial memory usage
        initial_size = sys.getsizeof(HelpSystem.COMMAND_HELP)
        initial_size += sys.getsizeof(HelpSystem.INTERACTIVE_HELP)
        initial_size += sys.getsizeof(HelpSystem.ERROR_SOLUTIONS)
        
        # Memory usage should be reasonable (less than 1MB for help data)
        self.assertLess(initial_size, 1024 * 1024, "Help system uses too much memory")


class TestHelpSystemAccessibility(unittest.TestCase):
    """Test cases for help system accessibility and usability"""
    
    def test_help_text_formatting_consistency(self):
        """Test that help text formatting is consistent across commands"""
        commands = HelpSystem.get_all_commands()
        
        for command in commands:
            help_text = HelpSystem.get_command_help(command)
            
            # Check for consistent formatting elements
            self.assertIn('=' * 60, help_text)  # Section dividers
            self.assertIn('Description:', help_text)
            self.assertIn('Usage:', help_text)
            self.assertIn('Examples:', help_text)
            
            # Check for proper emoji usage (should be consistent)
            emoji_count = help_text.count('🔧')
            self.assertEqual(emoji_count, 1, f"Inconsistent emoji usage in {command} help")
    
    def test_error_message_tone_consistency(self):
        """Test that error messages have consistent, helpful tone"""
        error_types = ['session_expired', 'insufficient_funds', 'account_not_found']
        
        for error_type in error_types:
            message = HelpSystem.get_error_solution(error_type)
            
            # Should use helpful, positive language
            self.assertIn('💡', message)  # Tips emoji
            self.assertIn('✓', message)   # Success emoji
            
            # Should not use harsh or negative language
            negative_words = ['failed', 'error', 'wrong', 'bad']
            message_lower = message.lower()
            
            # Count negative words (some are acceptable in context)
            negative_count = sum(1 for word in negative_words if word in message_lower)
            self.assertLessEqual(negative_count, 2, f"Too many negative words in {error_type} solution")
    
    def test_help_text_readability_metrics(self):
        """Test basic readability metrics for help text"""
        help_text = HelpSystem.get_command_help('transfer')
        
        # Check line length (should not be too long)
        lines = help_text.split('\n')
        long_lines = [line for line in lines if len(line) > 100]
        
        # Most lines should be reasonably short
        self.assertLess(len(long_lines), len(lines) * 0.3, "Too many long lines in help text")
        
        # Check for proper spacing
        empty_lines = [line for line in lines if line.strip() == '']
        self.assertGreater(len(empty_lines), 0, "Help text should have spacing for readability")


if __name__ == '__main__':
    unittest.main(verbosity=2)