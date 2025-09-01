#!/usr/bin/env python3
"""
Integration Example: Before and After Error Handling

This example shows how to replace existing error handling
with the new comprehensive error handling system.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.error_handler import ErrorHandler, CommandValidator
from src.utils.enhanced_error_integration import EnhancedErrorIntegration


def old_authentication_error():
    """Example of old error handling"""
    print("Error: No session token found. Please login first.")


def new_authentication_error():
    """Example of new error handling"""
    print(EnhancedErrorIntegration.handle_authentication_error())


def old_insufficient_funds_error():
    """Example of old error handling"""
    print("Error: Insufficient funds")


def new_insufficient_funds_error():
    """Example of new error handling"""
    print(ErrorHandler.handle_insufficient_funds(75.50, 100.00, "savings"))


def old_invalid_account_error():
    """Example of old error handling"""
    print("Error: Account 'saving' not found.")


def new_invalid_account_error():
    """Example of new error handling"""
    available_accounts = ["savings", "current", "My Salary Account"]
    print(ErrorHandler.handle_invalid_account("saving", available_accounts))


def old_invalid_amount_error():
    """Example of old error handling"""
    print("Error: Please enter a valid number.")


def new_invalid_amount_error():
    """Example of new error handling"""
    print(ErrorHandler.handle_invalid_amount("abc", "deposit"))


def old_command_error():
    """Example of old error handling"""
    print("Invalid command. Use -h for help.")


def new_command_error():
    """Example of new error handling"""
    print(ErrorHandler.handle_command_not_found("loginn"))


def demonstrate_improvements():
    """Demonstrate the improvements in error handling"""
    
    examples = [
        ("Authentication Error", old_authentication_error, new_authentication_error),
        ("Insufficient Funds", old_insufficient_funds_error, new_insufficient_funds_error),
        ("Invalid Account", old_invalid_account_error, new_invalid_account_error),
        ("Invalid Amount", old_invalid_amount_error, new_invalid_amount_error),
        ("Unknown Command", old_command_error, new_command_error),
    ]
    
    for title, old_func, new_func in examples:
        print("=" * 80)
        print(f"EXAMPLE: {title}")
        print("=" * 80)
        
        print("BEFORE (Old Error Handling):")
        print("-" * 40)
        old_func()
        
        print("\nAFTER (New Error Handling):")
        print("-" * 40)
        new_func()
        
        print("\n")


def show_validation_improvements():
    """Show validation improvements"""
    print("=" * 80)
    print("VALIDATION IMPROVEMENTS")
    print("=" * 80)
    
    # Old way - basic validation
    print("OLD WAY - Basic validation:")
    print("-" * 40)
    
    def old_validate_amount(amount_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("Error: Amount must be positive")
                return False
            return True
        except ValueError:
            print("Error: Invalid amount")
            return False
    
    print("Testing 'abc':")
    old_validate_amount("abc")
    
    print("\nNEW WAY - Comprehensive validation:")
    print("-" * 40)
    
    print("Testing 'abc':")
    is_valid, amount, error = CommandValidator.validate_amount("abc")
    if not is_valid:
        print(error)


def show_help_integration():
    """Show help text integration"""
    print("=" * 80)
    print("HELP TEXT INTEGRATION")
    print("=" * 80)
    
    print("OLD WAY - Generic help:")
    print("-" * 40)
    print("Use -h for help")
    
    print("\nNEW WAY - Context-aware help:")
    print("-" * 40)
    help_text = ErrorHandler.get_help_text("login")
    # Show first 15 lines
    lines = help_text.split('\n')[:15]
    print('\n'.join(lines))
    print("... (and more detailed examples)")


def main():
    """Run integration examples"""
    print("🏦 ERROR HANDLING INTEGRATION EXAMPLES")
    print("=" * 80)
    print("This demonstrates how the new error handling system")
    print("improves upon the existing error messages.")
    print()
    
    demonstrate_improvements()
    show_validation_improvements()
    show_help_integration()
    
    print("=" * 80)
    print("INTEGRATION SUMMARY")
    print("=" * 80)
    print("Benefits of the new error handling system:")
    print()
    print("✅ SPECIFIC & ACTIONABLE")
    print("   • Clear explanation of what went wrong")
    print("   • Specific steps to fix the problem")
    print("   • Context-aware suggestions")
    print()
    print("✅ USER-FRIENDLY")
    print("   • Formatted output with emojis and sections")
    print("   • Easy to scan and understand")
    print("   • Consistent styling across all errors")
    print()
    print("✅ HELPFUL SUGGESTIONS")
    print("   • Command corrections for typos")
    print("   • Alternative actions when operations fail")
    print("   • Examples of correct usage")
    print()
    print("✅ COMPREHENSIVE VALIDATION")
    print("   • Detailed format requirements")
    print("   • Multiple validation rules")
    print("   • Clear error explanations")
    print()
    print("✅ INTEGRATED HELP")
    print("   • Detailed command documentation")
    print("   • Usage examples and tips")
    print("   • Context-sensitive assistance")
    print()
    print("To integrate into existing code:")
    print("1. Replace print() error statements with ErrorHandler methods")
    print("2. Use CommandValidator for input validation")
    print("3. Add ErrorContext for operation tracking")
    print("4. Use EnhancedErrorIntegration for complex scenarios")


if __name__ == "__main__":
    main()