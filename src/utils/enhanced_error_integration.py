"""
Enhanced Error Integration Module

This module provides integration functions to replace existing error handling
with the new comprehensive error handling system.
"""

import sys
import os
from typing import Optional, List, Dict, Any
from src.utils.error_handler import ErrorHandler, ErrorContext, CommandValidator


class EnhancedErrorIntegration:
    """
    Integration class to enhance existing error handling throughout the application
    """
    
    @staticmethod
    def handle_authentication_error(token: Optional[str] = None, username: Optional[str] = None) -> str:
        """
        Enhanced authentication error handling
        
        Args:
            token: Session token if available
            username: Username if available
            
        Returns:
            Formatted error message
        """
        if not token:
            message = "🔐 Authentication Required\n"
            message += "=" * 40 + "\n"
            message += "No session token found. You must login first.\n"
            message += "\n💡 To login:\n"
            message += "python main.py login <username> <password>\n"
            message += "\n📱 For interactive mode:\n"
            message += "python main.py interactive\n"
            return message
        else:
            return ErrorHandler.handle_session_expired(username)
    
    @staticmethod
    def handle_account_operation_error(operation: str, account_name: str, 
                                     available_accounts: List[str], 
                                     additional_context: Dict[str, Any] = None) -> str:
        """
        Enhanced account operation error handling
        
        Args:
            operation: The operation being attempted
            account_name: The invalid account name
            available_accounts: List of user's accounts
            additional_context: Additional error context
            
        Returns:
            Formatted error message with operation-specific suggestions
        """
        base_error = ErrorHandler.handle_invalid_account(account_name, available_accounts)
        
        # Add operation-specific suggestions
        operation_suggestions = {
            'deposit': [
                "💰 For deposits, you can use any existing account",
                "Example: python main.py deposit savings 100"
            ],
            'withdraw': [
                "💸 For withdrawals, ensure the account has sufficient funds",
                "Check balance first: python main.py view_balance <account>"
            ],
            'transfer': [
                "🔄 For transfers, you need at least 2 accounts",
                "Both source and destination accounts must exist"
            ],
            'view_balance': [
                "👁️  To view balance, specify an existing account",
                "Example: python main.py view_balance savings"
            ]
        }
        
        if operation in operation_suggestions:
            base_error += f"\n\n🎯 {operation.capitalize()} Tips:\n"
            for suggestion in operation_suggestions[operation]:
                base_error += f"• {suggestion}\n"
        
        return base_error
    
    @staticmethod
    def handle_transaction_error(transaction_type: str, amount: str, 
                               account_name: str = None, 
                               balance: float = None) -> str:
        """
        Enhanced transaction error handling
        
        Args:
            transaction_type: Type of transaction (deposit, withdraw, transfer)
            amount: The invalid amount string
            account_name: Account name if relevant
            balance: Current balance if relevant
            
        Returns:
            Formatted error message with transaction-specific guidance
        """
        # Validate amount first
        is_valid, parsed_amount, amount_error = CommandValidator.validate_amount(amount)
        
        if not is_valid:
            # Add transaction-specific context to amount error
            enhanced_error = amount_error.replace("transaction", transaction_type)
            
            # Add balance context if available
            if balance is not None and account_name:
                enhanced_error += f"\n\n💰 Current Balance Information:\n"
                enhanced_error += f"Account: {account_name}\n"
                enhanced_error += f"Available: ${balance:.2f}\n"
            
            return enhanced_error
        
        return ""
    
    @staticmethod
    def handle_transfer_error(from_account: str, to_account: str, amount: float,
                            available_balance: float, user_accounts: List[str]) -> str:
        """
        Enhanced transfer-specific error handling
        
        Args:
            from_account: Source account name
            to_account: Destination account name  
            amount: Transfer amount
            available_balance: Available balance in source account
            user_accounts: List of user's account names
            
        Returns:
            Formatted error message with transfer-specific guidance
        """
        # Check for insufficient funds
        if amount > available_balance:
            error_msg = ErrorHandler.handle_insufficient_funds(
                available_balance, amount, from_account
            )
            
            # Add transfer-specific suggestions
            error_msg += f"\n\n🔄 Transfer Alternatives:\n"
            error_msg += f"• Transfer smaller amount: ${available_balance:.2f} or less\n"
            error_msg += f"• Deposit to {from_account} first\n"
            error_msg += f"• Use a different source account\n"
            
            return error_msg
        
        # Check for same account transfer
        if from_account == to_account:
            message = "🔄 Invalid Transfer\n"
            message += "=" * 30 + "\n"
            message += "Cannot transfer to the same account.\n"
            message += f"Source and destination are both: {from_account}\n"
            
            message += "\n💡 Available accounts for transfer:\n"
            other_accounts = [acc for acc in user_accounts if acc != from_account]
            for account in other_accounts:
                message += f"• {account}\n"
            
            return message
        
        return ""
    
    @staticmethod
    def handle_command_parsing_error(command: str, args: List[str], 
                                   expected_args: List[str]) -> str:
        """
        Enhanced command parsing error handling
        
        Args:
            command: The command being executed
            args: Arguments provided
            expected_args: Expected arguments
            
        Returns:
            Formatted error message with usage examples
        """
        message = f"⚙️  Command Usage Error: {command}\n"
        message += "=" * 50 + "\n"
        
        if len(args) < len(expected_args):
            message += f"Missing arguments. Provided {len(args)}, expected {len(expected_args)}.\n"
        elif len(args) > len(expected_args):
            message += f"Too many arguments. Provided {len(args)}, expected {len(expected_args)}.\n"
        
        message += f"\n📋 Expected format:\n"
        message += f"python main.py {command}"
        for arg in expected_args:
            message += f" <{arg}>"
        message += "\n"
        
        # Get detailed help for the command
        help_text = ErrorHandler.get_help_text(command)
        if "No detailed help available" not in help_text:
            message += f"\n{help_text}"
        
        return message
    
    @staticmethod
    def handle_file_operation_error(operation: str, filename: str, 
                                  error_details: str) -> str:
        """
        Enhanced file operation error handling
        
        Args:
            operation: File operation (save, load, backup)
            filename: Name of the file
            error_details: Specific error details
            
        Returns:
            Formatted error message with recovery suggestions
        """
        message = f"📁 File Operation Error: {operation}\n"
        message += "=" * 45 + "\n"
        message += f"File: {filename}\n"
        message += f"Error: {error_details}\n"
        
        message += "\n🔧 Troubleshooting:\n"
        
        if "permission" in error_details.lower():
            message += "• Check file permissions\n"
            message += "• Ensure you have write access to the directory\n"
            message += "• Try running with appropriate permissions\n"
        elif "not found" in error_details.lower():
            message += "• Verify the file path is correct\n"
            message += "• Check if the directory exists\n"
            message += "• Ensure the file hasn't been moved or deleted\n"
        elif "space" in error_details.lower():
            message += "• Check available disk space\n"
            message += "• Clean up temporary files\n"
            message += "• Try saving to a different location\n"
        else:
            message += "• Check file is not open in another application\n"
            message += "• Verify file is not corrupted\n"
            message += "• Try restarting the application\n"
        
        message += f"\n💾 Recovery options:\n"
        if operation == "save":
            message += "• Try saving with a different filename\n"
            message += "• Create a backup before retrying\n"
        elif operation == "load":
            message += "• Check if backup files exist\n"
            message += "• Verify file format is correct\n"
        
        return message
    
    @staticmethod
    def wrap_operation_with_error_handling(operation_name: str, user: str = None):
        """
        Decorator factory for wrapping operations with error handling
        
        Args:
            operation_name: Name of the operation for context
            user: Username for context
            
        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                with ErrorContext(operation_name, user):
                    try:
                        return func(*args, **kwargs)
                    except ValueError as e:
                        if "amount" in str(e).lower():
                            print(ErrorHandler.handle_invalid_amount(str(e), operation_name))
                        else:
                            print(f"❌ {operation_name} failed: {e}")
                        return None
                    except KeyError as e:
                        print(ErrorHandler.handle_invalid_account(str(e), []))
                        return None
                    except Exception as e:
                        print(f"❌ Unexpected error in {operation_name}: {e}")
                        return None
            return wrapper
        return decorator


def replace_print_errors_with_enhanced_handling():
    """
    Utility function to demonstrate how existing print statements 
    can be replaced with enhanced error handling
    """
    
    # Example replacements for common error patterns
    replacements = {
        # Authentication errors
        'print("Error: No session token found. Please login first.")': 
            'print(EnhancedErrorIntegration.handle_authentication_error())',
        
        'print("Error: Invalid or expired session. Please login again.")':
            'print(EnhancedErrorIntegration.handle_authentication_error(token, username))',
        
        # Account errors  
        'print(f"Error: Account \'{account_identifier}\' not found.")':
            'print(EnhancedErrorIntegration.handle_account_operation_error("operation", account_identifier, user.get_account_names()))',
        
        # Amount errors
        'print("❌ Please enter a valid number.")':
            'print(ErrorHandler.handle_invalid_amount(amount_str, "transaction"))',
        
        # Command errors
        'print("Invalid command. Use -h for help.")':
            'print(ErrorHandler.handle_command_not_found(command))'
    }
    
    return replacements


# Example usage functions for integration
def enhanced_login_error_handling(username: str, password: str, users: dict) -> Optional[Any]:
    """
    Example of enhanced login with better error handling
    
    Args:
        username: Username to login
        password: Password to verify
        users: Users dictionary
        
    Returns:
        User object if successful, None if failed
    """
    if username not in users:
        error_msg = "👤 User Not Found\n"
        error_msg += "=" * 30 + "\n"
        error_msg += f"Username '{username}' is not registered.\n"
        error_msg += "\n💡 Options:\n"
        error_msg += "• Check spelling of username\n"
        error_msg += "• Register new account: python main.py register <username> <password> <email>\n"
        error_msg += "• Contact administrator if you believe this is an error\n"
        print(error_msg)
        return None
    
    user = users[username]
    if not user.check_password(password):
        error_msg = "🔒 Authentication Failed\n"
        error_msg += "=" * 35 + "\n"
        error_msg += "Incorrect password for this account.\n"
        error_msg += "\n🔐 Security tips:\n"
        error_msg += "• Passwords are case-sensitive\n"
        error_msg += "• Check for caps lock\n"
        error_msg += "• Use password reset if forgotten\n"
        error_msg += "\n🆘 Forgot password?\n"
        error_msg += f"python main.py reset_password_init {username}\n"
        print(error_msg)
        return None
    
    return user


def enhanced_account_creation_error_handling(user, account_type: str, balance: str, overdraft_limit: float = 0) -> bool:
    """
    Example of enhanced account creation with better error handling
    
    Args:
        user: User object
        account_type: Type of account to create
        balance: Initial balance as string
        overdraft_limit: Overdraft limit
        
    Returns:
        True if successful, False if failed
    """
    # Validate account type
    is_valid_type, type_error = CommandValidator.validate_account_type(account_type)
    if not is_valid_type:
        print(type_error)
        return False
    
    # Validate balance amount
    is_valid_amount, parsed_balance, amount_error = CommandValidator.validate_amount(balance)
    if not is_valid_amount:
        print(amount_error.replace("transaction", "initial balance"))
        return False
    
    # Check if account already exists
    existing_account = user.get_account(account_type)
    if existing_account:
        error_msg = f"🏦 Account Already Exists\n"
        error_msg += "=" * 40 + "\n"
        error_msg += f"You already have a {account_type} account.\n"
        error_msg += f"Current balance: ${existing_account.balance:.2f}\n"
        error_msg += "\n💡 Options:\n"
        error_msg += f"• Deposit to existing account: python main.py deposit {account_type} <amount>\n"
        error_msg += "• Create a different account type\n"
        error_msg += "• View all accounts: python main.py list_accounts\n"
        print(error_msg)
        return False
    
    try:
        # Create account with enhanced error context
        with ErrorContext("account_creation", user.username, {"account_type": account_type, "balance": parsed_balance}):
            user.add_account(Account(account_type, balance=parsed_balance, overdraft_limit=overdraft_limit))
            
            success_msg = f"✅ Account Created Successfully!\n"
            success_msg += "=" * 40 + "\n"
            success_msg += f"Type: {account_type.capitalize()}\n"
            success_msg += f"Initial Balance: ${parsed_balance:.2f}\n"
            if overdraft_limit > 0:
                success_msg += f"Overdraft Limit: ${overdraft_limit:.2f}\n"
            success_msg += "\n🎯 Next steps:\n"
            success_msg += "• Make a deposit: python main.py deposit <account> <amount>\n"
            success_msg += "• View balance: python main.py view_balance <account>\n"
            success_msg += "• See all accounts: python main.py list_accounts\n"
            print(success_msg)
            return True
            
    except Exception as e:
        error_msg = EnhancedErrorIntegration.handle_file_operation_error(
            "account_creation", "users_data.json", str(e)
        )
        print(error_msg)
        return False