"""
Enhanced Help System for Banking Application

This module provides comprehensive help text, command documentation,
and context-sensitive assistance for both CLI and interactive modes.
"""

from typing import Dict, List, Optional, Tuple
from src.utils.error_handler import ErrorHandler


class HelpSystem:
    """
    Centralized help system with detailed command documentation and examples
    """
    
    # Comprehensive command help texts with detailed examples
    COMMAND_HELP = {
        'login': {
            'description': 'Authenticate with the banking system and create a session token',
            'usage': 'python main.py login <username> <password>',
            'arguments': [
                ('username', 'Your registered username', True),
                ('password', 'Your account password', True)
            ],
            'examples': [
                'python main.py login john_doe mypassword123',
                'python main.py login alice SecurePass456'
            ],
            'notes': [
                'Session token is saved to .session file',
                'Token is valid for 30 minutes of inactivity',
                'Use other commands without re-entering credentials after login'
            ],
            'related_commands': ['register', 'logout', 'status'],
            'common_errors': [
                ('Invalid credentials', 'Check username and password spelling'),
                ('User not found', 'Register first with the register command'),
                ('Session already active', 'Use logout command first or continue with existing session')
            ]
        },
        
        'register': {
            'description': 'Create a new user account in the banking system',
            'usage': 'python main.py register <username> <password> <email>',
            'arguments': [
                ('username', 'Unique username (letters, numbers, underscore only)', True),
                ('password', 'Strong password (min 8 chars, mixed case, numbers)', True),
                ('email', 'Valid email address', True)
            ],
            'examples': [
                'python main.py register john_doe MyPass123 john@email.com',
                'python main.py register alice_smith SecureP@ss456 alice@company.com'
            ],
            'notes': [
                'Username must be unique across all users',
                'Password requirements: 8+ chars, uppercase, lowercase, numbers',
                'Email is used for password reset functionality'
            ],
            'related_commands': ['login'],
            'common_errors': [
                ('Username already exists', 'Choose a different username'),
                ('Weak password', 'Include uppercase, lowercase, and numbers'),
                ('Invalid email format', 'Use format: user@domain.com')
            ]
        },
        
        'add_account': {
            'description': 'Create a new bank account of specified type',
            'usage': 'python main.py add_account <type> <balance> [--overdraft_limit <amount>]',
            'arguments': [
                ('type', 'Account type: savings, current, or salary', True),
                ('balance', 'Initial balance (must be positive number)', True),
                ('--overdraft_limit', 'Overdraft limit for current accounts (default: 0)', False)
            ],
            'examples': [
                'python main.py add_account savings 1000',
                'python main.py add_account current 500 --overdraft_limit 200',
                'python main.py add_account salary 0'
            ],
            'notes': [
                'You can only have one account of each type',
                'Overdraft limits only apply to current accounts',
                'Initial balance cannot be negative'
            ],
            'related_commands': ['list_accounts', 'account_summary'],
            'common_errors': [
                ('Account type already exists', 'You can only have one account per type'),
                ('Invalid account type', 'Use: savings, current, or salary'),
                ('Negative balance', 'Initial balance must be positive or zero')
            ]
        },
        
        'deposit': {
            'description': 'Deposit money into an account',
            'usage': 'python main.py deposit <account> <amount>',
            'arguments': [
                ('account', 'Account type (savings, current, salary) or nickname', True),
                ('amount', 'Amount to deposit (positive number)', True)
            ],
            'examples': [
                'python main.py deposit savings 100.50',
                'python main.py deposit current 250',
                'python main.py deposit "My Savings" 75.25'
            ],
            'notes': [
                'Amount must be positive',
                'You can use account nicknames if set',
                'Transaction is recorded with timestamp'
            ],
            'related_commands': ['withdraw', 'view_balance', 'transaction_history'],
            'common_errors': [
                ('Account not found', 'Check account name or create account first'),
                ('Invalid amount', 'Use positive numbers only'),
                ('Session expired', 'Login again to continue')
            ]
        },
        
        'withdraw': {
            'description': 'Withdraw money from an account',
            'usage': 'python main.py withdraw <account> <amount>',
            'arguments': [
                ('account', 'Account type (savings, current, salary) or nickname', True),
                ('amount', 'Amount to withdraw (positive number)', True)
            ],
            'examples': [
                'python main.py withdraw savings 50',
                'python main.py withdraw current 100.75',
                'python main.py withdraw "Daily Spending" 25'
            ],
            'notes': [
                'Amount cannot exceed available balance + overdraft',
                'Overdraft applies only to current accounts',
                'Transaction is recorded with timestamp'
            ],
            'related_commands': ['deposit', 'view_balance', 'transfer'],
            'common_errors': [
                ('Insufficient funds', 'Check balance or use smaller amount'),
                ('Account not found', 'Verify account name or create account'),
                ('Invalid amount', 'Use positive numbers only')
            ]
        },
        
        'transfer': {
            'description': 'Transfer money between your accounts',
            'usage': 'python main.py transfer <from_account> <to_account> <amount> [--memo <text>]',
            'arguments': [
                ('from_account', 'Source account (type or nickname)', True),
                ('to_account', 'Destination account (type or nickname)', True),
                ('amount', 'Amount to transfer (positive number)', True),
                ('--memo', 'Optional memo for the transfer', False)
            ],
            'examples': [
                'python main.py transfer savings current 200',
                'python main.py transfer "My Savings" "Daily Spending" 150.50',
                'python main.py transfer savings current 100 --memo "Monthly budget"'
            ],
            'notes': [
                'Both accounts must belong to you',
                'Sufficient funds required in source account',
                'Creates linked withdrawal and deposit transactions'
            ],
            'related_commands': ['list_accounts', 'view_balance', 'transaction_history'],
            'common_errors': [
                ('Account not found', 'Check account names with list_accounts'),
                ('Insufficient funds', 'Check source account balance'),
                ('Same account transfer', 'Source and destination must be different')
            ]
        },
        
        'view_balance': {
            'description': 'View account balance and details',
            'usage': 'python main.py view_balance <account>',
            'arguments': [
                ('account', 'Account type (savings, current, salary) or nickname', True)
            ],
            'examples': [
                'python main.py view_balance savings',
                'python main.py view_balance current',
                'python main.py view_balance "My Savings"'
            ],
            'notes': [
                'Shows current balance and available balance',
                'Displays overdraft information for current accounts',
                'Includes transaction count'
            ],
            'related_commands': ['list_accounts', 'account_summary', 'financial_overview'],
            'common_errors': [
                ('Account not found', 'Check account name or create account first'),
                ('Session expired', 'Login again to continue')
            ]
        },
        
        'list_accounts': {
            'description': 'List all accounts for the logged in user',
            'usage': 'python main.py list_accounts',
            'arguments': [],
            'examples': [
                'python main.py list_accounts'
            ],
            'notes': [
                'Shows all account types and balances',
                'Displays nicknames if set',
                'Includes total balance across all accounts'
            ],
            'related_commands': ['account_summary', 'financial_overview', 'add_account'],
            'common_errors': [
                ('No accounts found', 'Create an account first with add_account'),
                ('Session expired', 'Login again to continue')
            ]
        },
        
        'account_summary': {
            'description': 'Display comprehensive account summary with detailed information',
            'usage': 'python main.py account_summary',
            'arguments': [],
            'examples': [
                'python main.py account_summary'
            ],
            'notes': [
                'Shows detailed information for all accounts',
                'Includes creation dates and last activity',
                'Displays transaction counts and overdraft details'
            ],
            'related_commands': ['list_accounts', 'financial_overview'],
            'common_errors': [
                ('No accounts found', 'Create an account first'),
                ('Session expired', 'Login again to continue')
            ]
        },
        
        'financial_overview': {
            'description': 'Display financial overview with total balances and recent activity',
            'usage': 'python main.py financial_overview',
            'arguments': [],
            'examples': [
                'python main.py financial_overview'
            ],
            'notes': [
                'Shows total balance across all accounts',
                'Displays recent transaction activity',
                'Includes available balance calculations'
            ],
            'related_commands': ['account_summary', 'transaction_history'],
            'common_errors': [
                ('No accounts found', 'Create an account first'),
                ('Session expired', 'Login again to continue')
            ]
        },
        
        'transaction_history': {
            'description': 'View transaction history with filtering options',
            'usage': 'python main.py transaction_history [options]',
            'arguments': [
                ('--account', 'Account identifier (type or nickname)', False),
                ('--start-date', 'Start date (YYYY-MM-DD, MM/DD/YYYY)', False),
                ('--end-date', 'End date (YYYY-MM-DD, MM/DD/YYYY)', False),
                ('--type', 'Filter by transaction type(s)', False),
                ('--min-amount', 'Minimum transaction amount', False),
                ('--max-amount', 'Maximum transaction amount', False),
                ('--page', 'Page number (default: 1)', False),
                ('--page-size', 'Transactions per page (default: 20)', False),
                ('--sort-by', 'Sort by: date, amount, type, account', False),
                ('--export-format', 'Export to CSV or JSON', False)
            ],
            'examples': [
                'python main.py transaction_history',
                'python main.py transaction_history --account savings',
                'python main.py transaction_history --start-date 2024-01-01 --end-date 2024-01-31',
                'python main.py transaction_history --type deposit withdrawal --min-amount 100',
                'python main.py transaction_history --export-format csv'
            ],
            'notes': [
                'Default shows all transactions, newest first',
                'Date formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY',
                'Multiple transaction types can be specified',
                'Export creates timestamped files'
            ],
            'related_commands': ['transaction_summary', 'account_summary'],
            'common_errors': [
                ('Invalid date format', 'Use YYYY-MM-DD or MM/DD/YYYY format'),
                ('No transactions found', 'Check filters or create transactions first'),
                ('Invalid account', 'Check account name with list_accounts')
            ]
        },
        
        'transaction_summary': {
            'description': 'Display transaction summary statistics',
            'usage': 'python main.py transaction_summary [options]',
            'arguments': [
                ('--account', 'Account identifier (type or nickname)', False),
                ('--start-date', 'Start date for summary period', False),
                ('--end-date', 'End date for summary period', False)
            ],
            'examples': [
                'python main.py transaction_summary',
                'python main.py transaction_summary --account savings',
                'python main.py transaction_summary --start-date 2024-01-01'
            ],
            'notes': [
                'Shows totals for deposits, withdrawals, and transfers',
                'Calculates net change over period',
                'Includes transaction counts by type'
            ],
            'related_commands': ['transaction_history', 'financial_overview'],
            'common_errors': [
                ('No transactions in period', 'Adjust date range or check account'),
                ('Invalid date range', 'Start date must be before end date')
            ]
        },
        
        'interactive': {
            'description': 'Start interactive banking session with menu interface',
            'usage': 'python main.py interactive',
            'arguments': [],
            'examples': [
                'python main.py interactive'
            ],
            'notes': [
                'Provides menu-driven interface for all operations',
                'Session timeout after 30 minutes of inactivity',
                'Type "help" in interactive mode for assistance',
                'Use Ctrl+C or "exit" to quit'
            ],
            'related_commands': ['login', 'logout'],
            'common_errors': [
                ('Session expired', 'Login again to start interactive mode'),
                ('No session token', 'Login first before using interactive mode')
            ]
        },
        
        'logout': {
            'description': 'Logout and invalidate current session',
            'usage': 'python main.py logout',
            'arguments': [],
            'examples': [
                'python main.py logout'
            ],
            'notes': [
                'Invalidates current session token',
                'Removes .session file if present',
                'Required before switching users'
            ],
            'related_commands': ['login', 'status'],
            'common_errors': [
                ('No active session', 'Already logged out or no session found')
            ]
        },
        
        'status': {
            'description': 'Check login status and session information',
            'usage': 'python main.py status',
            'arguments': [],
            'examples': [
                'python main.py status'
            ],
            'notes': [
                'Shows current login status',
                'Displays session expiry information',
                'Useful for checking if login is required'
            ],
            'related_commands': ['login', 'logout'],
            'common_errors': []
        },
        
        'audit_logs': {
            'description': 'View audit logs and system activity with filtering options',
            'usage': 'python main.py audit_logs [options]',
            'arguments': [
                ('--user', 'Filter logs by specific user', False),
                ('--event-type', 'Filter by event type (login_success, login_failure, deposit, etc.)', False),
                ('--hours', 'Number of hours to look back (default: 24)', False),
                ('--limit', 'Maximum number of entries to show (default: 100)', False),
                ('--failed-only', 'Show only failed operations', False),
                ('--token', 'Session token (optional if saved in .session file)', False)
            ],
            'examples': [
                'python main.py audit_logs',
                'python main.py audit_logs --user john_doe --hours 48',
                'python main.py audit_logs --event-type login_failure --failed-only',
                'python main.py audit_logs --limit 50 --hours 12'
            ],
            'notes': [
                'Requires authentication to access audit logs',
                'Shows timestamps, users, events, and operation details',
                'Useful for security monitoring and troubleshooting'
            ],
            'related_commands': ['audit_stats', 'status'],
            'common_errors': [
                ('No logs found', 'Try expanding the time range with --hours'),
                ('Access denied', 'Ensure you are logged in with proper permissions')
            ]
        },
        
        'audit_stats': {
            'description': 'View audit log statistics and system activity summary',
            'usage': 'python main.py audit_stats [--hours <hours>]',
            'arguments': [
                ('--hours', 'Number of hours to analyze (default: 24)', False),
                ('--token', 'Session token (optional if saved in .session file)', False)
            ],
            'examples': [
                'python main.py audit_stats',
                'python main.py audit_stats --hours 48',
                'python main.py audit_stats --hours 168'  # One week
            ],
            'notes': [
                'Shows summary statistics for system activity',
                'Includes login attempts, operation counts, and user activity',
                'Useful for system monitoring and usage analysis'
            ],
            'related_commands': ['audit_logs', 'status'],
            'common_errors': [
                ('No data available', 'System may be newly installed or logs cleared'),
                ('Access denied', 'Ensure you are logged in with proper permissions')
            ]
        },
        
        'update_account_settings': {
            'description': 'Update account settings (nickname and overdraft limit)',
            'usage': 'python main.py update_account_settings <account> [--nickname <name>] [--overdraft-limit <amount>]',
            'arguments': [
                ('account', 'Account identifier (account type or nickname)', True),
                ('--nickname', 'New nickname for the account', False),
                ('--overdraft-limit', 'New overdraft limit (only for current accounts)', False),
                ('--token', 'Session token (optional if saved in .session file)', False)
            ],
            'examples': [
                'python main.py update_account_settings savings --nickname "Emergency Fund"',
                'python main.py update_account_settings current --overdraft-limit 500',
                'python main.py update_account_settings "My Savings" --nickname "Vacation Fund"',
                'python main.py update_account_settings current --nickname "Main Checking" --overdraft-limit 300'
            ],
            'notes': [
                'At least one setting (nickname or overdraft limit) must be provided',
                'Overdraft limits can only be set for current accounts',
                'Nicknames help identify accounts more easily',
                'Changes are saved immediately and logged for audit'
            ],
            'related_commands': ['view_account_settings', 'list_accounts', 'account_summary'],
            'common_errors': [
                ('Account not found', 'Check account identifier or use list_accounts to see available accounts'),
                ('Cannot update overdraft limit', 'Overdraft limits only apply to current accounts'),
                ('No settings provided', 'Specify at least --nickname or --overdraft-limit')
            ]
        },
        
        'view_account_settings': {
            'description': 'View current account settings and details',
            'usage': 'python main.py view_account_settings <account>',
            'arguments': [
                ('account', 'Account identifier (account type or nickname)', True),
                ('--token', 'Session token (optional if saved in .session file)', False)
            ],
            'examples': [
                'python main.py view_account_settings savings',
                'python main.py view_account_settings current',
                'python main.py view_account_settings "My Savings"'
            ],
            'notes': [
                'Shows detailed account information including status and settings',
                'Displays nickname, overdraft limits, and activity timestamps',
                'Useful for checking account configuration before making changes'
            ],
            'related_commands': ['update_account_settings', 'account_summary', 'list_accounts'],
            'common_errors': [
                ('Account not found', 'Check account identifier or use list_accounts to see available accounts')
            ]
        },
        
        'deactivate_account': {
            'description': 'Deactivate an account to prevent transactions',
            'usage': 'python main.py deactivate_account <account> --confirm',
            'arguments': [
                ('account', 'Account identifier (account type or nickname)', True),
                ('--confirm', 'Required confirmation flag for account deactivation', True),
                ('--token', 'Session token (optional if saved in .session file)', False)
            ],
            'examples': [
                'python main.py deactivate_account savings --confirm',
                'python main.py deactivate_account "Old Account" --confirm'
            ],
            'notes': [
                'Deactivated accounts cannot be used for transactions',
                'Account data and balance are preserved',
                'Use reactivate_account to restore functionality',
                'Confirmation flag is required to prevent accidental deactivation'
            ],
            'related_commands': ['reactivate_account', 'view_account_settings', 'list_accounts'],
            'common_errors': [
                ('Account not found', 'Check account identifier or use list_accounts to see available accounts'),
                ('Account already deactivated', 'Account is already inactive'),
                ('Confirmation required', 'Add --confirm flag to proceed with deactivation')
            ]
        },
        
        'reactivate_account': {
            'description': 'Reactivate a previously deactivated account',
            'usage': 'python main.py reactivate_account <account>',
            'arguments': [
                ('account', 'Account identifier (account type or nickname)', True),
                ('--token', 'Session token (optional if saved in .session file)', False)
            ],
            'examples': [
                'python main.py reactivate_account savings',
                'python main.py reactivate_account "Old Account"'
            ],
            'notes': [
                'Restores full functionality to deactivated accounts',
                'Account can immediately be used for transactions after reactivation',
                'All previous data and settings are preserved'
            ],
            'related_commands': ['deactivate_account', 'view_account_settings', 'list_accounts'],
            'common_errors': [
                ('Account not found', 'Check account identifier or use list_accounts to see available accounts'),
                ('Account already active', 'Account is already active and functional')
            ]
        }
    }
    
    # Interactive mode help contexts
    INTERACTIVE_HELP = {
        'main_menu': {
            'title': 'Main Menu Help',
            'description': 'Navigate the main menu by selecting numbered options',
            'options': [
                ('1', 'Account Management', 'Create, view, and manage your accounts'),
                ('2', 'Banking Operations', 'Deposits, withdrawals, and transfers'),
                ('3', 'Transaction History', 'View and filter transaction records'),
                ('4', 'Account Statements', 'Generate account statements (coming soon)'),
                ('5', 'Settings & Profile', 'Update account settings and profile'),
                ('6', 'Logout', 'End session and exit')
            ],
            'tips': [
                'Type the number and press Enter to select an option',
                'Type "help" at any prompt for assistance',
                'Type "exit" or use Ctrl+C to logout',
                'Session automatically times out after 30 minutes of inactivity'
            ]
        },
        
        'account_management': {
            'title': 'Account Management Help',
            'description': 'Manage your bank accounts and view account information',
            'options': [
                ('1', 'List All Accounts', 'View all your accounts with balances'),
                ('2', 'Create New Account', 'Add a new savings, current, or salary account'),
                ('3', 'Account Details', 'View detailed account information and statistics'),
                ('4', 'Update Settings', 'Change account nicknames and settings'),
                ('5', 'Financial Overview', 'See total balances and recent activity'),
                ('6', 'Back to Main Menu', 'Return to the main menu')
            ],
            'tips': [
                'You can have one account of each type (savings, current, salary)',
                'Account nicknames help identify accounts more easily',
                'Current accounts can have overdraft limits',
                'All changes are automatically saved'
            ]
        },
        
        'banking_operations': {
            'title': 'Banking Operations Help',
            'description': 'Perform banking transactions and view balances',
            'options': [
                ('1', 'Deposit Money', 'Add money to any of your accounts'),
                ('2', 'Withdraw Money', 'Take money from your accounts'),
                ('3', 'Transfer Between Accounts', 'Move money between your accounts'),
                ('4', 'View Account Balance', 'Check current balance and available funds'),
                ('5', 'Transfer History', 'View history of transfers between accounts'),
                ('6', 'Back to Main Menu', 'Return to the main menu')
            ],
            'tips': [
                'All amounts must be positive numbers',
                'Withdrawals respect account balance and overdraft limits',
                'Transfers require at least two accounts',
                'All transactions are recorded with timestamps'
            ]
        },
        
        'transaction_history': {
            'title': 'Transaction History Help',
            'description': 'View and analyze your transaction history',
            'options': [
                ('1', 'View All Transactions', 'See all transactions across accounts'),
                ('2', 'Filter by Account', 'View transactions for specific account'),
                ('3', 'Filter by Date Range', 'View transactions within date range'),
                ('4', 'Filter by Type', 'View specific transaction types'),
                ('5', 'Transaction Summary', 'View summary statistics'),
                ('6', 'Export Transactions', 'Export data to CSV or JSON'),
                ('7', 'Back to Main Menu', 'Return to the main menu')
            ],
            'tips': [
                'Transactions are shown newest first by default',
                'Use filters to find specific transactions',
                'Export feature creates timestamped files',
                'Summary shows totals and net changes'
            ]
        },
        
        'settings': {
            'title': 'Settings & Profile Help',
            'description': 'Manage account settings and view profile information',
            'options': [
                ('1', 'Update Nicknames', 'Change account nicknames for easier identification'),
                ('2', 'Account Settings', 'Modify account-specific settings'),
                ('3', 'Profile Information', 'View your user profile details'),
                ('4', 'Session Information', 'View current session details'),
                ('5', 'Help & Documentation', 'Access help and documentation'),
                ('6', 'Back to Main Menu', 'Return to the main menu')
            ],
            'tips': [
                'Nicknames make accounts easier to identify',
                'Settings changes are saved immediately',
                'Session information shows login time and expiry',
                'Help is available throughout the system'
            ]
        }
    }
    
    # Common error scenarios and their solutions
    ERROR_SOLUTIONS = {
        'session_expired': {
            'problem': 'Your session has expired',
            'causes': [
                'Inactive for more than 30 minutes',
                'Session token is invalid or corrupted',
                'System restart cleared sessions'
            ],
            'solutions': [
                'Run: python main.py login <username> <password>',
                'Use interactive mode: python main.py interactive',
                'Check session status: python main.py status'
            ],
            'prevention': [
                'Stay active within the 30-minute window',
                'Use interactive mode for multiple operations',
                'Save work frequently (automatic in most cases)'
            ]
        },
        
        'insufficient_funds': {
            'problem': 'Not enough money for the transaction',
            'causes': [
                'Account balance is too low',
                'Overdraft limit exceeded',
                'Incorrect amount entered'
            ],
            'solutions': [
                'Check balance: python main.py view_balance <account>',
                'Deposit money first: python main.py deposit <account> <amount>',
                'Transfer from another account: python main.py transfer <from> <to> <amount>',
                'Use a smaller amount'
            ],
            'prevention': [
                'Check balances before large transactions',
                'Set up overdraft limits on current accounts',
                'Keep track of spending with transaction history'
            ]
        },
        
        'account_not_found': {
            'problem': 'The specified account does not exist',
            'causes': [
                'Account name typed incorrectly',
                'Account has not been created yet',
                'Using wrong account type or nickname'
            ],
            'solutions': [
                'List accounts: python main.py list_accounts',
                'Create account: python main.py add_account <type> <balance>',
                'Check spelling of account name or nickname',
                'Use account summary: python main.py account_summary'
            ],
            'prevention': [
                'Use tab completion if available',
                'Set memorable nicknames for accounts',
                'List accounts before referencing them'
            ]
        },
        
        'invalid_amount': {
            'problem': 'The amount format is not valid',
            'causes': [
                'Using currency symbols ($, €, etc.)',
                'Using commas as decimal separators',
                'Negative amounts where not allowed',
                'Non-numeric characters in amount'
            ],
            'solutions': [
                'Use format: 100 or 100.50',
                'Remove currency symbols',
                'Use dots for decimals, not commas',
                'Ensure amount is positive'
            ],
            'prevention': [
                'Always use numeric format only',
                'Double-check amounts before submitting',
                'Use decimal points for cents'
            ]
        },
        
        'command_not_found': {
            'problem': 'The command is not recognized',
            'causes': [
                'Command name typed incorrectly',
                'Using old or deprecated command',
                'Missing required arguments'
            ],
            'solutions': [
                'Check available commands: python main.py --help',
                'Use command help: python main.py <command> --help',
                'Try interactive mode: python main.py interactive',
                'Check command spelling'
            ],
            'prevention': [
                'Use --help flag to see available commands',
                'Bookmark commonly used commands',
                'Use interactive mode for guided operations'
            ]
        }
    }

    @classmethod
    def get_command_help(cls, command: str, detailed: bool = True) -> str:
        """
        Get comprehensive help text for a command
        
        Args:
            command: Command name
            detailed: Whether to include detailed information
            
        Returns:
            Formatted help text
        """
        if command not in cls.COMMAND_HELP:
            return cls._get_generic_help(command)
        
        help_info = cls.COMMAND_HELP[command]
        
        # Build help text
        lines = []
        lines.append(f"🔧 {command.upper()} COMMAND")
        lines.append("=" * 60)
        lines.append(f"Description: {help_info['description']}")
        lines.append("")
        lines.append(f"Usage: {help_info['usage']}")
        lines.append("")
        
        # Arguments section
        if help_info['arguments']:
            lines.append("Arguments:")
            for arg_name, arg_desc, required in help_info['arguments']:
                req_text = "required" if required else "optional"
                lines.append(f"  {arg_name:<20} {arg_desc} ({req_text})")
            lines.append("")
        
        # Examples section
        if help_info['examples']:
            lines.append("Examples:")
            for example in help_info['examples']:
                lines.append(f"  {example}")
            lines.append("")
        
        if detailed:
            # Notes section
            if help_info['notes']:
                lines.append("Notes:")
                for note in help_info['notes']:
                    lines.append(f"  • {note}")
                lines.append("")
            
            # Related commands
            if help_info['related_commands']:
                lines.append("Related commands:")
                for related in help_info['related_commands']:
                    lines.append(f"  • {related}")
                lines.append("")
            
            # Common errors
            if help_info['common_errors']:
                lines.append("Common errors and solutions:")
                for error, solution in help_info['common_errors']:
                    lines.append(f"  ❌ {error}")
                    lines.append(f"     💡 {solution}")
                lines.append("")
        
        lines.append("=" * 60)
        lines.append("For more help: python main.py --help")
        lines.append("Interactive mode: python main.py interactive")
        
        return "\n".join(lines)

    @classmethod
    def get_interactive_help(cls, context: str) -> str:
        """
        Get context-sensitive help for interactive mode
        
        Args:
            context: Interactive mode context (main_menu, account_management, etc.)
            
        Returns:
            Formatted help text for the context
        """
        if context not in cls.INTERACTIVE_HELP:
            return cls._get_generic_interactive_help()
        
        help_info = cls.INTERACTIVE_HELP[context]
        
        lines = []
        lines.append(f"📚 {help_info['title']}")
        lines.append("=" * 60)
        lines.append(help_info['description'])
        lines.append("")
        
        # Menu options
        if help_info['options']:
            lines.append("Available options:")
            for option, name, desc in help_info['options']:
                lines.append(f"  {option}. {name}")
                lines.append(f"     {desc}")
            lines.append("")
        
        # Tips
        if help_info['tips']:
            lines.append("💡 Tips:")
            for tip in help_info['tips']:
                lines.append(f"  • {tip}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append("Type 'help' at any prompt for assistance")
        lines.append("Type 'exit' or use Ctrl+C to logout")
        
        return "\n".join(lines)

    @classmethod
    def get_error_solution(cls, error_type: str) -> str:
        """
        Get detailed solution for common errors
        
        Args:
            error_type: Type of error (session_expired, insufficient_funds, etc.)
            
        Returns:
            Formatted solution text
        """
        if error_type not in cls.ERROR_SOLUTIONS:
            return "No specific solution available for this error."
        
        solution_info = cls.ERROR_SOLUTIONS[error_type]
        
        lines = []
        lines.append(f"🔧 SOLUTION: {solution_info['problem']}")
        lines.append("=" * 60)
        
        # Possible causes
        lines.append("Possible causes:")
        for cause in solution_info['causes']:
            lines.append(f"  • {cause}")
        lines.append("")
        
        # Solutions
        lines.append("Solutions:")
        for solution in solution_info['solutions']:
            lines.append(f"  ✓ {solution}")
        lines.append("")
        
        # Prevention
        lines.append("Prevention tips:")
        for prevention in solution_info['prevention']:
            lines.append(f"  💡 {prevention}")
        lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)

    @classmethod
    def get_command_suggestions(cls, partial_command: str) -> List[str]:
        """
        Get command suggestions based on partial input
        
        Args:
            partial_command: Partial command string
            
        Returns:
            List of suggested commands
        """
        suggestions = []
        partial_lower = partial_command.lower()
        
        # Check exact matches first
        for command in cls.COMMAND_HELP.keys():
            if command.startswith(partial_lower):
                suggestions.append(command)
        
        # Check fuzzy matches
        if not suggestions:
            for command in cls.COMMAND_HELP.keys():
                if partial_lower in command or command in partial_lower:
                    suggestions.append(command)
        
        # Use error handler for additional suggestions
        if not suggestions:
            error_suggestions = ErrorHandler._find_similar_commands(partial_command)
            suggestions.extend(error_suggestions)
        
        return suggestions[:5]  # Return top 5 suggestions

    @classmethod
    def get_usage_examples(cls, command: str, scenario: str = None) -> List[str]:
        """
        Get usage examples for specific scenarios
        
        Args:
            command: Command name
            scenario: Specific scenario (beginner, advanced, error_recovery)
            
        Returns:
            List of usage examples
        """
        if command not in cls.COMMAND_HELP:
            return []
        
        examples = cls.COMMAND_HELP[command]['examples'].copy()
        
        # Add scenario-specific examples
        if scenario == 'beginner':
            # Add more basic examples with explanations
            if command == 'login':
                examples.insert(0, '# First time login\npython main.py login myusername mypassword')
            elif command == 'add_account':
                examples.insert(0, '# Create your first savings account\npython main.py add_account savings 100')
        
        elif scenario == 'advanced':
            # Add complex examples
            if command == 'transaction_history':
                examples.extend([
                    '# Complex filtering with export\npython main.py transaction_history --start-date 2024-01-01 --type deposit --min-amount 100 --export-format csv',
                    '# Paginated results with sorting\npython main.py transaction_history --page 2 --page-size 10 --sort-by amount'
                ])
        
        elif scenario == 'error_recovery':
            # Add examples for error recovery
            if command == 'login':
                examples.extend([
                    '# After session expired\npython main.py status  # Check current status first\npython main.py login username password'
                ])
        
        return examples

    @classmethod
    def _get_generic_help(cls, command: str) -> str:
        """Get generic help for unknown commands"""
        suggestions = cls.get_command_suggestions(command)
        
        lines = []
        lines.append(f"❓ Unknown command: '{command}'")
        lines.append("=" * 50)
        
        if suggestions:
            lines.append("Did you mean:")
            for suggestion in suggestions:
                lines.append(f"  • {suggestion}")
            lines.append("")
        
        lines.append("Available commands:")
        for cmd in sorted(cls.COMMAND_HELP.keys()):
            lines.append(f"  • {cmd}")
        lines.append("")
        lines.append("For detailed help: python main.py <command> --help")
        lines.append("For interactive mode: python main.py interactive")
        
        return "\n".join(lines)

    @classmethod
    def _get_generic_interactive_help(cls) -> str:
        """Get generic interactive help"""
        lines = []
        lines.append("📚 Interactive Mode Help")
        lines.append("=" * 50)
        lines.append("Navigate using numbered menu options")
        lines.append("Type 'help' for context-specific assistance")
        lines.append("Type 'exit' or use Ctrl+C to logout")
        lines.append("")
        lines.append("Available help contexts:")
        for context in cls.INTERACTIVE_HELP.keys():
            lines.append(f"  • {context}")
        
        return "\n".join(lines)

    @classmethod
    def get_all_commands(cls) -> List[str]:
        """Get list of all available commands"""
        return list(cls.COMMAND_HELP.keys())

    @classmethod
    def validate_command_usage(cls, command: str, args: List[str]) -> Tuple[bool, str]:
        """
        Validate command usage and provide helpful error messages
        
        Args:
            command: Command name
            args: List of arguments provided
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if command not in cls.COMMAND_HELP:
            return False, f"Unknown command: {command}"
        
        help_info = cls.COMMAND_HELP[command]
        required_args = [arg for arg, _, required in help_info['arguments'] if required]
        
        if len(args) < len(required_args):
            missing_args = required_args[len(args):]
            error_msg = f"Missing required arguments: {', '.join([arg[0] for arg in missing_args])}\n"
            error_msg += f"Usage: {help_info['usage']}\n"
            error_msg += f"For help: python main.py {command} --help"
            return False, error_msg
        
        return True, ""