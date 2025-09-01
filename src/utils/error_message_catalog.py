"""
Comprehensive Error Message Catalog for Banking System

This module provides a centralized catalog of all error messages used throughout
the banking system, ensuring consistency and providing easy maintenance.
"""

from typing import Dict, List, Optional
from datetime import datetime


class ErrorMessageCatalog:
    """
    Centralized catalog of error messages with consistent formatting and tone
    """
    
    # Authentication and Session Errors
    AUTH_ERRORS = {
        'invalid_credentials': {
            'title': '🔒 Authentication Failed',
            'message': 'Invalid username or password.',
            'suggestions': [
                'Check your username spelling',
                'Verify your password is correct',
                'Use "python main.py help login" for login help',
                'Register if you don\'t have an account: python main.py register'
            ],
            'severity': 'warning'
        },
        
        'user_not_found': {
            'title': '👤 User Not Found',
            'message': 'The specified username does not exist in the system.',
            'suggestions': [
                'Check the username spelling',
                'Register a new account: python main.py register <username> <password> <email>',
                'Contact support if you believe this is an error'
            ],
            'severity': 'error'
        },
        
        'session_expired': {
            'title': '⏰ Session Expired',
            'message': 'Your session has expired for security reasons.',
            'suggestions': [
                'Login again: python main.py login <username> <password>',
                'Use interactive mode: python main.py interactive',
                'Check session status: python main.py status'
            ],
            'severity': 'warning',
            'details': 'Sessions expire after 30 minutes of inactivity to protect your account.'
        },
        
        'session_not_found': {
            'title': '🔑 No Active Session',
            'message': 'No session token found. Please login first.',
            'suggestions': [
                'Login to create a session: python main.py login <username> <password>',
                'Use interactive mode: python main.py interactive'
            ],
            'severity': 'info'
        },
        
        'account_locked': {
            'title': '🔒 Account Locked',
            'message': 'Your account has been temporarily locked due to multiple failed login attempts.',
            'suggestions': [
                'Wait 15 minutes before trying again',
                'Contact support if you need immediate access',
                'Use password reset if you forgot your password'
            ],
            'severity': 'error'
        }
    }
    
    # Account Management Errors
    ACCOUNT_ERRORS = {
        'account_not_found': {
            'title': '🏦 Account Not Found',
            'message': 'The specified account does not exist.',
            'suggestions': [
                'Check account name spelling',
                'List your accounts: python main.py list_accounts',
                'Create an account: python main.py add_account <type> <balance>'
            ],
            'severity': 'error'
        },
        
        'account_already_exists': {
            'title': '🏦 Account Already Exists',
            'message': 'You already have an account of this type.',
            'suggestions': [
                'Each user can have only one account per type',
                'View existing accounts: python main.py list_accounts',
                'Choose a different account type: savings, current, or salary'
            ],
            'severity': 'warning'
        },
        
        'invalid_account_type': {
            'title': '🏦 Invalid Account Type',
            'message': 'The specified account type is not valid.',
            'suggestions': [
                'Valid types: savings, current, salary',
                'Use "python main.py help add_account" for examples',
                'Check spelling of account type'
            ],
            'severity': 'error'
        },
        
        'account_creation_failed': {
            'title': '❌ Account Creation Failed',
            'message': 'Unable to create the account due to system error.',
            'suggestions': [
                'Try again in a few moments',
                'Check your input parameters',
                'Contact support if problem persists'
            ],
            'severity': 'error'
        }
    }
    
    # Transaction Errors
    TRANSACTION_ERRORS = {
        'insufficient_funds': {
            'title': '💸 Insufficient Funds',
            'message': 'Not enough money available for this transaction.',
            'suggestions': [
                'Check your balance: python main.py view_balance <account>',
                'Deposit money first: python main.py deposit <account> <amount>',
                'Transfer from another account: python main.py transfer <from> <to> <amount>',
                'Use a smaller amount'
            ],
            'severity': 'warning'
        },
        
        'invalid_amount': {
            'title': '💰 Invalid Amount',
            'message': 'The amount format is not valid.',
            'suggestions': [
                'Use numbers only (e.g., 100 or 100.50)',
                'Remove currency symbols ($, €, etc.)',
                'Use dots for decimals, not commas',
                'Amount must be positive'
            ],
            'severity': 'error'
        },
        
        'negative_amount': {
            'title': '💰 Negative Amount',
            'message': 'Amount cannot be negative.',
            'suggestions': [
                'Enter a positive number',
                'For withdrawals, use the withdraw command',
                'Check your input for typos'
            ],
            'severity': 'error'
        },
        
        'zero_amount': {
            'title': '💰 Zero Amount',
            'message': 'Amount must be greater than zero.',
            'suggestions': [
                'Enter an amount greater than 0',
                'Check your input for typos',
                'Use decimal format if needed (e.g., 0.01)'
            ],
            'severity': 'error'
        },
        
        'transaction_failed': {
            'title': '❌ Transaction Failed',
            'message': 'The transaction could not be completed.',
            'suggestions': [
                'Check account balances',
                'Verify account names',
                'Try again in a few moments',
                'Contact support if problem persists'
            ],
            'severity': 'error'
        },
        
        'overdraft_exceeded': {
            'title': '🚫 Overdraft Limit Exceeded',
            'message': 'This transaction would exceed your overdraft limit.',
            'suggestions': [
                'Use a smaller amount',
                'Deposit money to increase available balance',
                'Contact support to discuss overdraft limit increase'
            ],
            'severity': 'warning'
        }
    }
    
    # Transfer Specific Errors
    TRANSFER_ERRORS = {
        'same_account_transfer': {
            'title': '🔄 Invalid Transfer',
            'message': 'Cannot transfer money to the same account.',
            'suggestions': [
                'Choose different source and destination accounts',
                'List your accounts: python main.py list_accounts',
                'Use deposit or withdraw for single account operations'
            ],
            'severity': 'error'
        },
        
        'transfer_to_nonexistent_account': {
            'title': '🔄 Transfer Failed',
            'message': 'Destination account does not exist.',
            'suggestions': [
                'Check destination account name',
                'List your accounts: python main.py list_accounts',
                'Create the account first if needed'
            ],
            'severity': 'error'
        },
        
        'transfer_from_nonexistent_account': {
            'title': '🔄 Transfer Failed',
            'message': 'Source account does not exist.',
            'suggestions': [
                'Check source account name',
                'List your accounts: python main.py list_accounts',
                'Create the account first if needed'
            ],
            'severity': 'error'
        }
    }
    
    # Command and Input Errors
    COMMAND_ERRORS = {
        'command_not_found': {
            'title': '❓ Unknown Command',
            'message': 'The specified command is not recognized.',
            'suggestions': [
                'Check command spelling',
                'Use "python main.py help" to see all commands',
                'Use "python main.py interactive" for guided operations',
                'Use "python main.py help <command>" for specific help'
            ],
            'severity': 'error'
        },
        
        'missing_arguments': {
            'title': '📝 Missing Arguments',
            'message': 'Required arguments are missing for this command.',
            'suggestions': [
                'Check command usage with --help flag',
                'Use "python main.py help <command>" for examples',
                'Use interactive mode for guided input'
            ],
            'severity': 'error'
        },
        
        'invalid_arguments': {
            'title': '📝 Invalid Arguments',
            'message': 'One or more arguments are not valid.',
            'suggestions': [
                'Check argument format and spelling',
                'Use "python main.py help <command>" for examples',
                'Verify required vs optional arguments'
            ],
            'severity': 'error'
        },
        
        'too_many_arguments': {
            'title': '📝 Too Many Arguments',
            'message': 'More arguments provided than expected.',
            'suggestions': [
                'Check command usage with --help flag',
                'Remove extra arguments',
                'Use quotes for arguments with spaces'
            ],
            'severity': 'error'
        }
    }
    
    # System and Technical Errors
    SYSTEM_ERRORS = {
        'file_not_found': {
            'title': '📁 File Not Found',
            'message': 'Required system file could not be found.',
            'suggestions': [
                'Check if the application is properly installed',
                'Verify file permissions',
                'Contact support for assistance'
            ],
            'severity': 'error'
        },
        
        'permission_denied': {
            'title': '🔐 Permission Denied',
            'message': 'Insufficient permissions to perform this operation.',
            'suggestions': [
                'Check file and directory permissions',
                'Run with appropriate user privileges',
                'Contact system administrator'
            ],
            'severity': 'error'
        },
        
        'disk_full': {
            'title': '💾 Disk Full',
            'message': 'Not enough disk space to complete the operation.',
            'suggestions': [
                'Free up disk space',
                'Move files to external storage',
                'Contact system administrator'
            ],
            'severity': 'error'
        },
        
        'network_error': {
            'title': '🌐 Network Error',
            'message': 'Network connection problem detected.',
            'suggestions': [
                'Check your internet connection',
                'Verify server accessibility',
                'Try again in a few moments',
                'Contact network administrator if problem persists'
            ],
            'severity': 'warning'
        },
        
        'database_error': {
            'title': '🗄️ Database Error',
            'message': 'Database operation failed.',
            'suggestions': [
                'Try the operation again',
                'Check system resources',
                'Contact support if problem persists'
            ],
            'severity': 'error'
        }
    }
    
    # Validation Errors
    VALIDATION_ERRORS = {
        'invalid_email': {
            'title': '📧 Invalid Email',
            'message': 'The email address format is not valid.',
            'suggestions': [
                'Use format: user@domain.com',
                'Check for typos in email address',
                'Ensure @ symbol and domain are present'
            ],
            'severity': 'error'
        },
        
        'weak_password': {
            'title': '🔒 Weak Password',
            'message': 'Password does not meet security requirements.',
            'suggestions': [
                'Use at least 8 characters',
                'Include uppercase and lowercase letters',
                'Add numbers and special characters',
                'Avoid common words or personal information'
            ],
            'severity': 'warning'
        },
        
        'invalid_username': {
            'title': '👤 Invalid Username',
            'message': 'Username format is not valid.',
            'suggestions': [
                'Use letters, numbers, and underscores only',
                'Start with a letter',
                'Length should be 3-20 characters',
                'Avoid spaces and special characters'
            ],
            'severity': 'error'
        },
        
        'username_taken': {
            'title': '👤 Username Taken',
            'message': 'This username is already in use.',
            'suggestions': [
                'Choose a different username',
                'Add numbers or underscores to make it unique',
                'Try variations of your preferred name'
            ],
            'severity': 'warning'
        }
    }

    @classmethod
    def get_error_message(cls, category: str, error_type: str, **kwargs) -> str:
        """
        Get formatted error message from catalog
        
        Args:
            category: Error category (auth, account, transaction, etc.)
            error_type: Specific error type within category
            **kwargs: Additional context for message formatting
            
        Returns:
            Formatted error message string
        """
        # Map category names to error dictionaries
        category_map = {
            'auth': cls.AUTH_ERRORS,
            'account': cls.ACCOUNT_ERRORS,
            'transaction': cls.TRANSACTION_ERRORS,
            'transfer': cls.TRANSFER_ERRORS,
            'command': cls.COMMAND_ERRORS,
            'system': cls.SYSTEM_ERRORS,
            'validation': cls.VALIDATION_ERRORS
        }
        
        if category not in category_map:
            return cls._get_generic_error_message(f"Unknown error category: {category}")
        
        error_dict = category_map[category]
        
        if error_type not in error_dict:
            return cls._get_generic_error_message(f"Unknown error type: {error_type}")
        
        error_info = error_dict[error_type]
        
        # Build formatted message
        lines = []
        lines.append(error_info['title'])
        lines.append("=" * 60)
        lines.append(error_info['message'])
        
        # Add context-specific details if provided
        if kwargs:
            lines.append("")
            lines.append("Details:")
            for key, value in kwargs.items():
                lines.append(f"  • {key.replace('_', ' ').title()}: {value}")
        
        # Add additional details if available
        if 'details' in error_info:
            lines.append("")
            lines.append(f"ℹ️  {error_info['details']}")
        
        # Add suggestions
        lines.append("")
        lines.append("💡 Suggestions:")
        for suggestion in error_info['suggestions']:
            lines.append(f"  • {suggestion}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("For more help: python main.py help")
        lines.append("Interactive mode: python main.py interactive")
        
        return "\n".join(lines)

    @classmethod
    def get_error_summary(cls, category: str, error_type: str) -> str:
        """
        Get brief error summary without full formatting
        
        Args:
            category: Error category
            error_type: Specific error type
            
        Returns:
            Brief error message
        """
        category_map = {
            'auth': cls.AUTH_ERRORS,
            'account': cls.ACCOUNT_ERRORS,
            'transaction': cls.TRANSACTION_ERRORS,
            'transfer': cls.TRANSFER_ERRORS,
            'command': cls.COMMAND_ERRORS,
            'system': cls.SYSTEM_ERRORS,
            'validation': cls.VALIDATION_ERRORS
        }
        
        if category in category_map and error_type in category_map[category]:
            return category_map[category][error_type]['message']
        
        return f"Unknown error: {category}.{error_type}"

    @classmethod
    def get_error_severity(cls, category: str, error_type: str) -> str:
        """
        Get error severity level
        
        Args:
            category: Error category
            error_type: Specific error type
            
        Returns:
            Severity level (info, warning, error)
        """
        category_map = {
            'auth': cls.AUTH_ERRORS,
            'account': cls.ACCOUNT_ERRORS,
            'transaction': cls.TRANSACTION_ERRORS,
            'transfer': cls.TRANSFER_ERRORS,
            'command': cls.COMMAND_ERRORS,
            'system': cls.SYSTEM_ERRORS,
            'validation': cls.VALIDATION_ERRORS
        }
        
        if category in category_map and error_type in category_map[category]:
            return category_map[category][error_type].get('severity', 'error')
        
        return 'error'

    @classmethod
    def list_all_errors(cls) -> Dict[str, List[str]]:
        """
        Get list of all available error types by category
        
        Returns:
            Dictionary mapping categories to lists of error types
        """
        return {
            'auth': list(cls.AUTH_ERRORS.keys()),
            'account': list(cls.ACCOUNT_ERRORS.keys()),
            'transaction': list(cls.TRANSACTION_ERRORS.keys()),
            'transfer': list(cls.TRANSFER_ERRORS.keys()),
            'command': list(cls.COMMAND_ERRORS.keys()),
            'system': list(cls.SYSTEM_ERRORS.keys()),
            'validation': list(cls.VALIDATION_ERRORS.keys())
        }

    @classmethod
    def _get_generic_error_message(cls, error_description: str) -> str:
        """Get generic error message for unknown errors"""
        lines = []
        lines.append("❌ System Error")
        lines.append("=" * 40)
        lines.append(error_description)
        lines.append("")
        lines.append("💡 Suggestions:")
        lines.append("  • Try the operation again")
        lines.append("  • Check your input parameters")
        lines.append("  • Use 'python main.py help' for assistance")
        lines.append("  • Contact support if problem persists")
        lines.append("")
        lines.append("=" * 40)
        
        return "\n".join(lines)

    @classmethod
    def validate_error_catalog(cls) -> List[str]:
        """
        Validate error catalog completeness and consistency
        
        Returns:
            List of validation issues found
        """
        issues = []
        
        # Check that all error entries have required fields
        required_fields = ['title', 'message', 'suggestions', 'severity']
        
        all_categories = [
            ('auth', cls.AUTH_ERRORS),
            ('account', cls.ACCOUNT_ERRORS),
            ('transaction', cls.TRANSACTION_ERRORS),
            ('transfer', cls.TRANSFER_ERRORS),
            ('command', cls.COMMAND_ERRORS),
            ('system', cls.SYSTEM_ERRORS),
            ('validation', cls.VALIDATION_ERRORS)
        ]
        
        for category_name, category_dict in all_categories:
            for error_type, error_info in category_dict.items():
                # Check required fields
                for field in required_fields:
                    if field not in error_info:
                        issues.append(f"{category_name}.{error_type}: Missing required field '{field}'")
                
                # Check that suggestions is a non-empty list
                if 'suggestions' in error_info:
                    if not isinstance(error_info['suggestions'], list):
                        issues.append(f"{category_name}.{error_type}: 'suggestions' must be a list")
                    elif len(error_info['suggestions']) == 0:
                        issues.append(f"{category_name}.{error_type}: 'suggestions' list is empty")
                
                # Check severity values
                if 'severity' in error_info:
                    valid_severities = ['info', 'warning', 'error']
                    if error_info['severity'] not in valid_severities:
                        issues.append(f"{category_name}.{error_type}: Invalid severity '{error_info['severity']}'")
        
        return issues