"""
Comprehensive Error Handling System for Banking Application

This module provides context-aware error messages, command suggestions,
and help text integration to improve user experience.
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class ErrorHandler:
    """
    Centralized error handling with context-aware messages and suggestions
    """
    
    # Command mappings for suggestions
    COMMAND_SUGGESTIONS = {
        'login': ['login', 'log_in', 'signin', 'sign_in'],
        'logout': ['logout', 'log_out', 'signout', 'sign_out', 'exit', 'quit'],
        'register': ['register', 'signup', 'sign_up', 'create_user'],
        'add_account': ['add_account', 'create_account', 'new_account'],
        'deposit': ['deposit', 'add_money', 'credit'],
        'withdraw': ['withdraw', 'take_money', 'debit'],
        'transfer': ['transfer', 'move_money', 'send_money'],
        'view_balance': ['balance', 'view_balance', 'check_balance'],
        'list_accounts': ['list_accounts', 'accounts', 'show_accounts'],
        'transaction_history': ['history', 'transactions', 'transaction_history'],
        'interactive': ['interactive', 'menu', 'gui']
    }
    
    # Valid account types
    VALID_ACCOUNT_TYPES = ['savings', 'current', 'salary']
    
    # Common error patterns and their fixes
    ERROR_PATTERNS = {
        'invalid_amount': r'invalid.*amount|amount.*invalid',
        'insufficient_funds': r'insufficient.*funds|not.*enough.*money',
        'account_not_found': r'account.*not.*found|not.*found.*account',
        'session_expired': r'session.*expired|expired.*session',
        'invalid_credentials': r'invalid.*credentials|incorrect.*password',
        'command_not_found': r'command.*not.*found|invalid.*command'
    }

    @staticmethod
    def handle_session_expired(username: Optional[str] = None) -> str:
        """
        Handle session expiration with clear instructions
        
        Args:
            username: Optional username for personalized message
            
        Returns:
            Formatted error message with instructions
        """
        message = "🔒 Session Expired\n"
        message += "=" * 50 + "\n"
        
        if username:
            message += f"Your session for user '{username}' has expired.\n"
        else:
            message += "Your session has expired for security reasons.\n"
        
        message += "\nThis happened because:\n"
        message += "• You've been inactive for more than 30 minutes\n"
        message += "• The session token is no longer valid\n"
        message += "• System security timeout was triggered\n"
        
        message += "\n💡 To continue:\n"
        message += "1. Run: python main.py login <username> <password>\n"
        message += "2. Or use interactive mode: python main.py interactive\n"
        message += "3. Your session token will be automatically saved\n"
        
        message += "\n🔐 Security Note: Sessions expire automatically to protect your account."
        
        return message

    @staticmethod
    def handle_insufficient_funds(available: float, requested: float, account_name: str = "account") -> str:
        """
        Handle insufficient funds with detailed balance information
        
        Args:
            available: Available balance including overdraft
            requested: Requested amount
            account_name: Name of the account
            
        Returns:
            Formatted error message with suggestions
        """
        shortage = requested - available
        
        message = "💸 Insufficient Funds\n"
        message += "=" * 40 + "\n"
        message += f"Account: {account_name}\n"
        message += f"Available balance: ${available:.2f}\n"
        message += f"Requested amount: ${requested:.2f}\n"
        message += f"Shortage: ${shortage:.2f}\n"
        
        message += "\n💡 Suggestions:\n"
        if available > 0:
            message += f"• Try withdrawing ${available:.2f} or less\n"
        
        message += "• Deposit money first: python main.py deposit <account> <amount>\n"
        message += "• Check other accounts: python main.py list_accounts\n"
        message += "• Transfer from another account: python main.py transfer <from> <to> <amount>\n"
        
        if "current" in account_name.lower():
            message += "• Consider increasing your overdraft limit\n"
        
        return message

    @staticmethod
    def handle_invalid_account(account_name: str, available_accounts: List[str]) -> str:
        """
        Handle invalid account reference with suggestions
        
        Args:
            account_name: The invalid account name provided
            available_accounts: List of valid account names
            
        Returns:
            Formatted error message with account suggestions
        """
        message = f"❌ Account Not Found: '{account_name}'\n"
        message += "=" * 50 + "\n"
        
        if not available_accounts:
            message += "You don't have any accounts yet.\n"
            message += "\n💡 Create an account first:\n"
            message += "python main.py add_account <type> <balance>\n"
            message += f"Valid types: {', '.join(ErrorHandler.VALID_ACCOUNT_TYPES)}\n"
        else:
            message += "Available accounts:\n"
            for i, account in enumerate(available_accounts, 1):
                message += f"{i}. {account}\n"
            
            # Suggest similar account names
            suggestions = ErrorHandler._find_similar_accounts(account_name, available_accounts)
            if suggestions:
                message += f"\n💡 Did you mean:\n"
                for suggestion in suggestions:
                    message += f"• {suggestion}\n"
            
            message += "\n📋 To see all accounts: python main.py list_accounts\n"
        
        return message

    @staticmethod
    def handle_invalid_amount(amount_str: str, context: str = "transaction") -> str:
        """
        Handle invalid amount format with examples
        
        Args:
            amount_str: The invalid amount string
            context: Context where amount is used (transaction, balance, etc.)
            
        Returns:
            Formatted error message with examples
        """
        message = f"💰 Invalid Amount: '{amount_str}'\n"
        message += "=" * 40 + "\n"
        message += f"The amount for {context} must be a valid number.\n"
        
        message += "\n✅ Valid formats:\n"
        message += "• 100 (whole number)\n"
        message += "• 100.50 (decimal)\n"
        message += "• 1000.00 (with cents)\n"
        
        message += "\n❌ Invalid formats:\n"
        message += "• $100 (no currency symbols)\n"
        message += "• 100,50 (use dots, not commas)\n"
        message += "• -50 (negative amounts not allowed)\n"
        message += "• abc (letters not allowed)\n"
        
        message += "\n💡 Examples:\n"
        message += "• Deposit: python main.py deposit savings 100.50\n"
        message += "• Withdraw: python main.py withdraw current 50\n"
        message += "• Transfer: python main.py transfer savings current 200\n"
        
        return message

    @staticmethod
    def handle_command_not_found(command: str) -> str:
        """
        Handle unknown command with suggestions
        
        Args:
            command: The invalid command
            
        Returns:
            Formatted error message with command suggestions
        """
        message = f"❓ Unknown Command: '{command}'\n"
        message += "=" * 50 + "\n"
        
        # Find similar commands
        suggestions = ErrorHandler._find_similar_commands(command)
        
        if suggestions:
            message += "💡 Did you mean:\n"
            for suggestion in suggestions:
                message += f"• {suggestion}\n"
        
        message += "\n📚 Available commands:\n"
        message += "• login <username> <password>\n"
        message += "• register <username> <password> <email>\n"
        message += "• add_account <type> <balance>\n"
        message += "• deposit <account> <amount>\n"
        message += "• withdraw <account> <amount>\n"
        message += "• transfer <from> <to> <amount>\n"
        message += "• view_balance <account>\n"
        message += "• list_accounts\n"
        message += "• transaction_history\n"
        message += "• interactive\n"
        message += "• logout\n"
        
        message += "\n🆘 For detailed help: python main.py <command> --help\n"
        message += "🎯 For interactive mode: python main.py interactive\n"
        
        return message

    @staticmethod
    def handle_invalid_account_type(account_type: str) -> str:
        """
        Handle invalid account type with valid options
        
        Args:
            account_type: The invalid account type
            
        Returns:
            Formatted error message with valid types
        """
        message = f"🏦 Invalid Account Type: '{account_type}'\n"
        message += "=" * 45 + "\n"
        
        message += "Valid account types:\n"
        for i, valid_type in enumerate(ErrorHandler.VALID_ACCOUNT_TYPES, 1):
            message += f"{i}. {valid_type}\n"
        
        # Suggest similar account type
        suggestions = ErrorHandler._find_similar_strings(account_type, ErrorHandler.VALID_ACCOUNT_TYPES)
        if suggestions:
            message += f"\n💡 Did you mean: {suggestions[0]}?\n"
        
        message += "\n📝 Examples:\n"
        message += "• Create savings: python main.py add_account savings 1000\n"
        message += "• Create current: python main.py add_account current 500 --overdraft_limit 200\n"
        message += "• Create salary: python main.py add_account salary 0\n"
        
        return message

    @staticmethod
    def handle_validation_error(field: str, value: str, requirements: List[str]) -> str:
        """
        Handle field validation errors with specific requirements
        
        Args:
            field: Field name that failed validation
            value: The invalid value
            requirements: List of validation requirements
            
        Returns:
            Formatted error message with requirements
        """
        message = f"⚠️  Validation Error: {field}\n"
        message += "=" * 40 + "\n"
        message += f"Invalid value: '{value}'\n"
        
        message += "\n📋 Requirements:\n"
        for requirement in requirements:
            message += f"• {requirement}\n"
        
        if field.lower() == 'password':
            message += "\n💡 Password tips:\n"
            message += "• Use a mix of uppercase and lowercase letters\n"
            message += "• Include numbers and special characters\n"
            message += "• Avoid common words or personal information\n"
            message += "• Consider using a password manager\n"
        
        return message

    @staticmethod
    def handle_network_error(operation: str, retry_count: int = 0) -> str:
        """
        Handle network-related errors with retry suggestions
        
        Args:
            operation: The operation that failed
            retry_count: Number of retries attempted
            
        Returns:
            Formatted error message with retry instructions
        """
        message = f"🌐 Network Error\n"
        message += "=" * 30 + "\n"
        message += f"Operation: {operation}\n"
        
        if retry_count > 0:
            message += f"Retry attempts: {retry_count}\n"
        
        message += "\n🔧 Troubleshooting:\n"
        message += "• Check your internet connection\n"
        message += "• Verify server is accessible\n"
        message += "• Try again in a few moments\n"
        
        if retry_count < 3:
            message += f"• The system will automatically retry ({3 - retry_count} attempts remaining)\n"
        
        message += "\n📞 If problem persists:\n"
        message += "• Contact system administrator\n"
        message += "• Check system status page\n"
        
        return message

    @staticmethod
    def suggest_command_fix(invalid_command: str) -> str:
        """
        Suggest command fixes for common typos and mistakes
        
        Args:
            invalid_command: The invalid command entered
            
        Returns:
            Suggestion string or empty if no suggestions
        """
        suggestions = ErrorHandler._find_similar_commands(invalid_command)
        
        if suggestions:
            if len(suggestions) == 1:
                return f"Did you mean: {suggestions[0]}?"
            else:
                return f"Did you mean: {', '.join(suggestions[:3])}?"
        
        return ""

    @staticmethod
    def get_help_text(command: str) -> str:
        """
        Get detailed help text for a command
        
        Args:
            command: Command name
            
        Returns:
            Detailed help text with examples
        """
        help_texts = {
            'login': """
🔐 LOGIN COMMAND
Usage: python main.py login <username> <password>

Description:
  Authenticate with the banking system and create a session token.

Arguments:
  username    Your registered username
  password    Your account password

Examples:
  python main.py login john_doe mypassword123
  python main.py login alice SecurePass456

After login:
  • Session token is saved to .session file
  • Token is valid for 30 minutes of inactivity
  • Use other commands without re-entering credentials

Related commands:
  • register - Create a new account
  • logout - End current session
  • status - Check login status
            """,
            
            'register': """
🆕 REGISTER COMMAND
Usage: python main.py register <username> <password> <email>

Description:
  Create a new user account in the banking system.

Arguments:
  username    Unique username (letters, numbers, underscore only)
  password    Strong password (min 8 chars, mixed case, numbers)
  email       Valid email address

Password Requirements:
  • At least 8 characters long
  • Contains uppercase letters
  • Contains lowercase letters
  • Contains at least one number

Examples:
  python main.py register john_doe MyPass123 john@email.com
  python main.py register alice_smith SecureP@ss456 alice@company.com

After registration:
  • Use 'login' command to access your account
  • Create accounts with 'add_account' command
            """,
            
            'add_account': """
🏦 ADD ACCOUNT COMMAND
Usage: python main.py add_account <type> <balance> [--overdraft_limit <amount>]

Description:
  Create a new bank account of specified type.

Arguments:
  type        Account type: savings, current, or salary
  balance     Initial balance (must be positive number)
  
Options:
  --overdraft_limit    Overdraft limit for current accounts (default: 0)

Account Types:
  • savings  - Standard savings account
  • current  - Checking account with optional overdraft
  • salary   - Salary account for payroll

Examples:
  python main.py add_account savings 1000
  python main.py add_account current 500 --overdraft_limit 200
  python main.py add_account salary 0

Note: You must be logged in to create accounts.
            """,
            
            'transfer': """
🔄 TRANSFER COMMAND
Usage: python main.py transfer <from_account> <to_account> <amount> [--memo <text>]

Description:
  Transfer money between your accounts.

Arguments:
  from_account    Source account (type or nickname)
  to_account      Destination account (type or nickname)
  amount          Amount to transfer (positive number)

Options:
  --memo          Optional memo for the transfer

Examples:
  python main.py transfer savings current 200
  python main.py transfer "My Savings" "Daily Spending" 150.50
  python main.py transfer savings current 100 --memo "Monthly budget"

Requirements:
  • Both accounts must belong to you
  • Sufficient funds in source account
  • Amount must be positive

Related commands:
  • list_accounts - See available accounts
  • view_balance - Check account balances
            """
        }
        
        return help_texts.get(command, f"No detailed help available for '{command}'. Use --help flag with the command.")

    @staticmethod
    def _find_similar_commands(command: str) -> List[str]:
        """Find commands similar to the given command"""
        suggestions = []
        command_lower = command.lower()
        
        # Check all command mappings
        for correct_cmd, variations in ErrorHandler.COMMAND_SUGGESTIONS.items():
            for variation in variations:
                if ErrorHandler._calculate_similarity(command_lower, variation) > 0.6:
                    if correct_cmd not in suggestions:
                        suggestions.append(correct_cmd)
        
        return suggestions[:3]  # Return top 3 suggestions

    @staticmethod
    def _find_similar_accounts(account_name: str, available_accounts: List[str]) -> List[str]:
        """Find accounts similar to the given account name"""
        suggestions = []
        account_lower = account_name.lower()
        
        for account in available_accounts:
            if ErrorHandler._calculate_similarity(account_lower, account.lower()) > 0.5:
                suggestions.append(account)
        
        return suggestions[:3]  # Return top 3 suggestions

    @staticmethod
    def _find_similar_strings(target: str, candidates: List[str]) -> List[str]:
        """Find strings similar to target from candidates list"""
        suggestions = []
        target_lower = target.lower()
        
        for candidate in candidates:
            if ErrorHandler._calculate_similarity(target_lower, candidate.lower()) > 0.5:
                suggestions.append(candidate)
        
        return suggestions

    @staticmethod
    def _calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using simple algorithm
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        if str1 == str2:
            return 1.0
        
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        # Simple character-based similarity
        matches = 0
        total_chars = max(len(str1), len(str2))
        
        for i in range(min(len(str1), len(str2))):
            if str1[i] == str2[i]:
                matches += 1
        
        # Check for substring matches
        if str1 in str2 or str2 in str1:
            matches += min(len(str1), len(str2)) * 0.5
        
        return min(matches / total_chars, 1.0)


class ErrorContext:
    """
    Context manager for error handling with additional information
    """
    
    def __init__(self, operation: str, user: str = None, additional_info: Dict = None):
        """
        Initialize error context
        
        Args:
            operation: Name of the operation being performed
            user: Username if available
            additional_info: Additional context information
        """
        self.operation = operation
        self.user = user
        self.additional_info = additional_info or {}
        self.start_time = datetime.now()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log error with context
            duration = datetime.now() - self.start_time
            error_info = {
                'operation': self.operation,
                'user': self.user,
                'duration_ms': int(duration.total_seconds() * 1000),
                'error_type': exc_type.__name__,
                'error_message': str(exc_val),
                'additional_info': self.additional_info
            }
            
            # In a real application, this would log to a file or monitoring system
            print(f"🔍 Error Context: {error_info}")
        
        return False  # Don't suppress exceptions


class CommandValidator:
    """
    Validates commands and provides suggestions for corrections
    """
    
    @staticmethod
    def validate_amount(amount_str: str) -> Tuple[bool, float, str]:
        """
        Validate amount string and return parsed value
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Tuple of (is_valid, parsed_amount, error_message)
        """
        try:
            amount = float(amount_str)
            if amount < 0:
                return False, 0, ErrorHandler.handle_invalid_amount(amount_str, "transaction")
            if amount == 0:
                return False, 0, "Amount must be greater than zero."
            return True, amount, ""
        except ValueError:
            return False, 0, ErrorHandler.handle_invalid_amount(amount_str, "transaction")
    
    @staticmethod
    def validate_account_type(account_type: str) -> Tuple[bool, str]:
        """
        Validate account type
        
        Args:
            account_type: Account type string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if account_type.lower() in ErrorHandler.VALID_ACCOUNT_TYPES:
            return True, ""
        else:
            return False, ErrorHandler.handle_invalid_account_type(account_type)
    
    @staticmethod
    def validate_command_exists(command: str, available_commands: List[str]) -> Tuple[bool, str]:
        """
        Validate that command exists
        
        Args:
            command: Command name
            available_commands: List of valid commands
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if command in available_commands:
            return True, ""
        else:
            return False, ErrorHandler.handle_command_not_found(command)