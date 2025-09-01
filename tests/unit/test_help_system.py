"""
Unit tests for the enhanced help system and error message accuracy.

This module tests the comprehensive help system, command documentation,
context-sensitive help, and error message catalog functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.help_system import HelpSystem
from src.utils.error_handler import ErrorHandler


class TestHelpSystem(unittest.TestCase):
    """Test cases for the HelpSystem class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.help_system = HelpSystem()
    
    def test_get_command_help_valid_command(self):
        """Test getting help for valid commands"""
        # Test login command help
        help_text = HelpSystem.get_command_help('login')
        
        self.assertIn('LOGIN COMMAND', help_text)
        self.assertIn('Description:', help_text)
        self.assertIn('Usage:', help_text)
        self.assertIn('Arguments:', help_text)
        self.assertIn('Examples:', help_text)
        self.assertIn('python main.py login', help_text)
    
    def test_get_command_help_invalid_command(self):
        """Test getting help for invalid commands"""
        help_text = HelpSystem.get_command_help('invalid_command')
        
        self.assertIn('Unknown command', help_text)
        self.assertIn('Available commands:', help_text)
    
    def test_get_command_help_detailed_vs_brief(self):
        """Test detailed vs brief help text"""
        detailed_help = HelpSystem.get_command_help('register', detailed=True)
        brief_help = HelpSystem.get_command_help('register', detailed=False)
        
        # Detailed help should be longer and contain more sections
        self.assertGreater(len(detailed_help), len(brief_help))
        self.assertIn('Notes:', detailed_help)
        self.assertIn('Related commands:', detailed_help)
        self.assertIn('Common errors', detailed_help)
    
    def test_get_interactive_help_valid_context(self):
        """Test getting interactive help for valid contexts"""
        help_text = HelpSystem.get_interactive_help('main_menu')
        
        self.assertIn('Main Menu Help', help_text)
        self.assertIn('Available options:', help_text)
        self.assertIn('Tips:', help_text)
    
    def test_get_interactive_help_invalid_context(self):
        """Test getting interactive help for invalid contexts"""
        help_text = HelpSystem.get_interactive_help('invalid_context')
        
        self.assertIn('Interactive Mode Help', help_text)
        self.assertIn('Available help contexts:', help_text)
    
    def test_get_error_solution_valid_error(self):
        """Test getting solutions for valid error types"""
        solution_text = HelpSystem.get_error_solution('session_expired')
        
        self.assertIn('SOLUTION:', solution_text)
        self.assertIn('Possible causes:', solution_text)
        self.assertIn('Solutions:', solution_text)
        self.assertIn('Prevention tips:', solution_text)
    
    def test_get_error_solution_invalid_error(self):
        """Test getting solutions for invalid error types"""
        solution_text = HelpSystem.get_error_solution('invalid_error')
        
        self.assertEqual(solution_text, "No specific solution available for this error.")
    
    def test_get_command_suggestions(self):
        """Test command suggestion functionality"""
        # Test exact prefix match
        suggestions = HelpSystem.get_command_suggestions('log')
        self.assertIn('login', suggestions)
        self.assertIn('logout', suggestions)
        
        # Test fuzzy match
        suggestions = HelpSystem.get_command_suggestions('accnt')
        # Should suggest account-related commands or return some suggestions
        self.assertIsInstance(suggestions, list)
        
        # Test no matches
        suggestions = HelpSystem.get_command_suggestions('xyz123')
        # Should return empty list or error handler suggestions
        self.assertIsInstance(suggestions, list)
    
    def test_get_usage_examples_basic(self):
        """Test getting basic usage examples"""
        examples = HelpSystem.get_usage_examples('login')
        
        self.assertIsInstance(examples, list)
        self.assertGreater(len(examples), 0)
        self.assertTrue(any('python main.py login' in example for example in examples))
    
    def test_get_usage_examples_with_scenario(self):
        """Test getting scenario-specific usage examples"""
        beginner_examples = HelpSystem.get_usage_examples('login', 'beginner')
        advanced_examples = HelpSystem.get_usage_examples('transaction_history', 'advanced')
        
        self.assertIsInstance(beginner_examples, list)
        self.assertIsInstance(advanced_examples, list)
        
        # Advanced examples should be more complex
        if advanced_examples:
            self.assertTrue(any('--' in example for example in advanced_examples))
    
    def test_get_all_commands(self):
        """Test getting list of all commands"""
        commands = HelpSystem.get_all_commands()
        
        self.assertIsInstance(commands, list)
        self.assertIn('login', commands)
        self.assertIn('register', commands)
        self.assertIn('add_account', commands)
        self.assertGreater(len(commands), 5)  # Should have multiple commands
    
    def test_validate_command_usage_valid(self):
        """Test command usage validation for valid usage"""
        # Test command with correct arguments
        is_valid, error_msg = HelpSystem.validate_command_usage('login', ['username', 'password'])
        
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")
    
    def test_validate_command_usage_missing_args(self):
        """Test command usage validation for missing arguments"""
        # Test command with missing arguments
        is_valid, error_msg = HelpSystem.validate_command_usage('login', ['username'])
        
        self.assertFalse(is_valid)
        self.assertIn('Missing required arguments', error_msg)
        self.assertIn('Usage:', error_msg)
    
    def test_validate_command_usage_unknown_command(self):
        """Test command usage validation for unknown commands"""
        is_valid, error_msg = HelpSystem.validate_command_usage('unknown_cmd', [])
        
        self.assertFalse(is_valid)
        self.assertIn('Unknown command', error_msg)
    
    def test_command_help_completeness(self):
        """Test that all commands have complete help information"""
        commands = HelpSystem.get_all_commands()
        
        for command in commands:
            help_info = HelpSystem.COMMAND_HELP[command]
            
            # Check required fields
            self.assertIn('description', help_info)
            self.assertIn('usage', help_info)
            self.assertIn('arguments', help_info)
            self.assertIn('examples', help_info)
            
            # Check that description is not empty
            self.assertGreater(len(help_info['description']), 0)
            
            # Check that usage contains the command name
            self.assertIn(command, help_info['usage'])
            
            # Check that examples are provided
            self.assertGreater(len(help_info['examples']), 0)
    
    def test_interactive_help_completeness(self):
        """Test that all interactive contexts have complete help information"""
        contexts = list(HelpSystem.INTERACTIVE_HELP.keys())
        
        for context in contexts:
            help_info = HelpSystem.INTERACTIVE_HELP[context]
            
            # Check required fields
            self.assertIn('title', help_info)
            self.assertIn('description', help_info)
            self.assertIn('options', help_info)
            self.assertIn('tips', help_info)
            
            # Check that fields are not empty
            self.assertGreater(len(help_info['title']), 0)
            self.assertGreater(len(help_info['description']), 0)
    
    def test_error_solutions_completeness(self):
        """Test that all error solutions have complete information"""
        error_types = list(HelpSystem.ERROR_SOLUTIONS.keys())
        
        for error_type in error_types:
            solution_info = HelpSystem.ERROR_SOLUTIONS[error_type]
            
            # Check required fields
            self.assertIn('problem', solution_info)
            self.assertIn('causes', solution_info)
            self.assertIn('solutions', solution_info)
            self.assertIn('prevention', solution_info)
            
            # Check that lists are not empty
            self.assertGreater(len(solution_info['causes']), 0)
            self.assertGreater(len(solution_info['solutions']), 0)
            self.assertGreater(len(solution_info['prevention']), 0)


class TestErrorHandlerIntegration(unittest.TestCase):
    """Test cases for ErrorHandler integration with help system"""
    
    def test_error_handler_command_suggestions(self):
        """Test that error handler provides command suggestions"""
        suggestion = ErrorHandler.suggest_command_fix('logn')
        
        self.assertIsInstance(suggestion, str)
        if suggestion:  # If suggestions are provided
            self.assertIn('login', suggestion.lower())
    
    def test_error_handler_help_text_integration(self):
        """Test that error handler integrates with help system"""
        # Test getting help text for a command
        help_text = ErrorHandler.get_help_text('login')
        
        self.assertIn('LOGIN COMMAND', help_text)
        self.assertIn('Usage:', help_text)
        self.assertIn('Examples:', help_text)
    
    def test_error_handler_session_expired_message(self):
        """Test session expired error message quality"""
        message = ErrorHandler.handle_session_expired('testuser')
        
        self.assertIn('Session Expired', message)
        self.assertIn('testuser', message)
        self.assertIn('python main.py login', message)
        self.assertIn('interactive', message)
    
    def test_error_handler_insufficient_funds_message(self):
        """Test insufficient funds error message quality"""
        message = ErrorHandler.handle_insufficient_funds(100.0, 150.0, 'savings')
        
        self.assertIn('Insufficient Funds', message)
        self.assertIn('100.00', message)  # Available amount
        self.assertIn('150.00', message)  # Requested amount
        self.assertIn('50.00', message)   # Shortage
        self.assertIn('savings', message)
        self.assertIn('deposit', message.lower())  # Should suggest deposit
    
    def test_error_handler_invalid_account_message(self):
        """Test invalid account error message quality"""
        available_accounts = ['savings', 'current']
        message = ErrorHandler.handle_invalid_account('saving', available_accounts)
        
        self.assertIn('Account Not Found', message)
        self.assertIn('saving', message)
        self.assertIn('Available accounts:', message)
        self.assertIn('savings', message)
        self.assertIn('current', message)
    
    def test_error_handler_invalid_amount_message(self):
        """Test invalid amount error message quality"""
        message = ErrorHandler.handle_invalid_amount('$100', 'deposit')
        
        self.assertIn('Invalid Amount', message)
        self.assertIn('$100', message)
        self.assertIn('Valid formats:', message)
        self.assertIn('100.50', message)
        self.assertIn('no currency symbols', message.lower())
    
    def test_error_handler_command_not_found_message(self):
        """Test command not found error message quality"""
        message = ErrorHandler.handle_command_not_found('logn')
        
        self.assertIn('Unknown Command', message)
        self.assertIn('logn', message)
        self.assertIn('Available commands:', message)
        self.assertIn('login', message)
        self.assertIn('--help', message)


class TestHelpSystemUsability(unittest.TestCase):
    """Test cases for help system usability and user experience"""
    
    def test_help_text_readability(self):
        """Test that help text is readable and well-formatted"""
        help_text = HelpSystem.get_command_help('transfer')
        
        # Check for proper formatting
        self.assertIn('=', help_text)  # Should have section dividers
        self.assertIn('•', help_text)  # Should have bullet points
        
        # Check for clear structure
        lines = help_text.split('\n')
        self.assertGreater(len(lines), 10)  # Should be multi-line
        
        # Check for consistent formatting
        title_lines = [line for line in lines if 'COMMAND' in line]
        self.assertGreater(len(title_lines), 0)
    
    def test_examples_are_executable(self):
        """Test that provided examples are valid command formats"""
        commands = ['login', 'register', 'add_account', 'deposit', 'withdraw']
        
        for command in commands:
            help_info = HelpSystem.COMMAND_HELP[command]
            examples = help_info['examples']
            
            for example in examples:
                # Examples should start with 'python main.py'
                self.assertTrue(
                    example.startswith('python main.py') or example.startswith('#'),
                    f"Invalid example format in {command}: {example}"
                )
                
                # Examples should contain the command name
                if not example.startswith('#'):  # Skip comments
                    self.assertIn(command, example)
    
    def test_error_messages_are_actionable(self):
        """Test that error messages provide actionable solutions"""
        error_types = ['session_expired', 'insufficient_funds', 'account_not_found']
        
        for error_type in error_types:
            solution_text = HelpSystem.get_error_solution(error_type)
            
            # Should contain specific commands or actions
            self.assertTrue(
                'python main.py' in solution_text or 
                'Run:' in solution_text or
                'Use:' in solution_text,
                f"Error solution for {error_type} lacks actionable commands"
            )
    
    def test_help_system_consistency(self):
        """Test consistency across help system components"""
        # Check that all commands mentioned in help exist
        all_commands = set(HelpSystem.get_all_commands())
        
        for command, help_info in HelpSystem.COMMAND_HELP.items():
            # Check related commands exist
            for related_cmd in help_info.get('related_commands', []):
                self.assertIn(
                    related_cmd, 
                    all_commands,
                    f"Related command '{related_cmd}' in {command} help does not exist"
                )
    
    def test_interactive_help_navigation(self):
        """Test that interactive help provides clear navigation guidance"""
        contexts = ['main_menu', 'account_management', 'banking_operations']
        
        for context in contexts:
            help_text = HelpSystem.get_interactive_help(context)
            
            # Should provide navigation instructions
            self.assertTrue(
                'Type' in help_text or 'Select' in help_text or 'Enter' in help_text,
                f"Interactive help for {context} lacks navigation guidance"
            )
            
            # Should mention help availability
            self.assertIn('help', help_text.lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)