#!/usr/bin/env python3
"""
Error Handling System Demonstration

This script demonstrates the comprehensive error handling system
and how it integrates with the existing banking application.
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.error_handler import ErrorHandler, ErrorContext, CommandValidator
from src.utils.enhanced_error_integration import EnhancedErrorIntegration


def demo_session_expired_error():
    """Demonstrate session expired error handling"""
    print("=" * 60)
    print("DEMO: Session Expired Error")
    print("=" * 60)
    
    # Without username
    print("Scenario 1: Session expired without username context")
    print(ErrorHandler.handle_session_expired())
    
    print("\n" + "-" * 40 + "\n")
    
    # With username
    print("Scenario 2: Session expired with username context")
    print(ErrorHandler.handle_session_expired("john_doe"))


def demo_insufficient_funds_error():
    """Demonstrate insufficient funds error handling"""
    print("\n" + "=" * 60)
    print("DEMO: Insufficient Funds Error")
    print("=" * 60)
    
    # Basic insufficient funds
    print("Scenario 1: Basic insufficient funds")
    print(ErrorHandler.handle_insufficient_funds(75.50, 100.00, "savings"))
    
    print("\n" + "-" * 40 + "\n")
    
    # Current account with overdraft
    print("Scenario 2: Current account with overdraft suggestions")
    print(ErrorHandler.handle_insufficient_funds(150.00, 200.00, "current account"))
    
    print("\n" + "-" * 40 + "\n")
    
    # Zero balance
    print("Scenario 3: Zero balance scenario")
    print(ErrorHandler.handle_insufficient_funds(0.00, 50.00, "salary"))


def demo_invalid_account_error():
    """Demonstrate invalid account error handling"""
    print("\n" + "=" * 60)
    print("DEMO: Invalid Account Error")
    print("=" * 60)
    
    # With available accounts
    print("Scenario 1: Invalid account with suggestions")
    available_accounts = ["savings", "current", "My Salary Account"]
    print(ErrorHandler.handle_invalid_account("saving", available_accounts))
    
    print("\n" + "-" * 40 + "\n")
    
    # No accounts available
    print("Scenario 2: No accounts exist")
    print(ErrorHandler.handle_invalid_account("savings", []))


def demo_invalid_amount_error():
    """Demonstrate invalid amount error handling"""
    print("\n" + "=" * 60)
    print("DEMO: Invalid Amount Error")
    print("=" * 60)
    
    # Invalid string
    print("Scenario 1: Non-numeric amount")
    print(ErrorHandler.handle_invalid_amount("abc", "deposit"))
    
    print("\n" + "-" * 40 + "\n")
    
    # Negative amount
    print("Scenario 2: Negative amount")
    print(ErrorHandler.handle_invalid_amount("-50", "withdrawal"))


def demo_command_not_found_error():
    """Demonstrate command not found error handling"""
    print("\n" + "=" * 60)
    print("DEMO: Command Not Found Error")
    print("=" * 60)
    
    # Similar command exists
    print("Scenario 1: Typo in command (similar command exists)")
    print(ErrorHandler.handle_command_not_found("loginn"))
    
    print("\n" + "-" * 40 + "\n")
    
    # No similar command
    print("Scenario 2: Completely unknown command")
    print(ErrorHandler.handle_command_not_found("xyz123"))


def demo_command_suggestions():
    """Demonstrate command suggestion system"""
    print("\n" + "=" * 60)
    print("DEMO: Command Suggestion System")
    print("=" * 60)
    
    test_commands = ["loginn", "depositt", "withdrawl", "transferr", "balanc"]
    
    for cmd in test_commands:
        suggestion = ErrorHandler.suggest_command_fix(cmd)
        print(f"'{cmd}' -> {suggestion}")


def demo_help_text_integration():
    """Demonstrate help text integration"""
    print("\n" + "=" * 60)
    print("DEMO: Help Text Integration")
    print("=" * 60)
    
    commands = ["login", "register", "add_account", "transfer"]
    
    for cmd in commands:
        print(f"\n--- Help for '{cmd}' ---")
        help_text = ErrorHandler.get_help_text(cmd)
        # Show first few lines of help
        lines = help_text.split('\n')[:10]
        print('\n'.join(lines))
        if len(help_text.split('\n')) > 10:
            print("... (truncated)")


def demo_validation_system():
    """Demonstrate validation system"""
    print("\n" + "=" * 60)
    print("DEMO: Validation System")
    print("=" * 60)
    
    # Amount validation
    print("Amount Validation Tests:")
    test_amounts = ["100", "150.75", "-50", "0", "abc", "$100"]
    
    for amount in test_amounts:
        is_valid, parsed, error = CommandValidator.validate_amount(amount)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  '{amount}' -> {status} (parsed: {parsed})")
    
    print("\n" + "-" * 40)
    
    # Account type validation
    print("\nAccount Type Validation Tests:")
    test_types = ["savings", "current", "salary", "checking", "SAVINGS"]
    
    for acc_type in test_types:
        is_valid, error = CommandValidator.validate_account_type(acc_type)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  '{acc_type}' -> {status}")


def demo_error_context():
    """Demonstrate error context system"""
    print("\n" + "=" * 60)
    print("DEMO: Error Context System")
    print("=" * 60)
    
    print("Scenario 1: Operation completes successfully")
    try:
        with ErrorContext("demo_operation", "demo_user", {"test": "data"}):
            # Simulate successful operation
            print("  ✅ Operation completed successfully")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
    
    print("\nScenario 2: Operation fails with error")
    try:
        with ErrorContext("demo_operation", "demo_user", {"test": "data"}):
            # Simulate operation failure
            raise ValueError("Simulated error for demonstration")
    except ValueError:
        print("  ❌ Operation failed as expected (error context logged)")


def demo_enhanced_integration():
    """Demonstrate enhanced integration features"""
    print("\n" + "=" * 60)
    print("DEMO: Enhanced Integration Features")
    print("=" * 60)
    
    # Authentication error
    print("Enhanced Authentication Error:")
    print(EnhancedErrorIntegration.handle_authentication_error())
    
    print("\n" + "-" * 40 + "\n")
    
    # Account operation error
    print("Enhanced Account Operation Error:")
    available_accounts = ["savings", "current"]
    print(EnhancedErrorIntegration.handle_account_operation_error(
        "deposit", "checkng", available_accounts
    ))
    
    print("\n" + "-" * 40 + "\n")
    
    # Transfer error
    print("Enhanced Transfer Error:")
    print(EnhancedErrorIntegration.handle_transfer_error(
        "savings", "current", 200.0, 150.0, ["savings", "current", "salary"]
    ))


def demo_similarity_algorithm():
    """Demonstrate similarity calculation algorithm"""
    print("\n" + "=" * 60)
    print("DEMO: Similarity Algorithm")
    print("=" * 60)
    
    test_pairs = [
        ("login", "loginn"),
        ("deposit", "depositt"),
        ("savings", "saving"),
        ("transfer", "transferr"),
        ("abc", "xyz"),
        ("current", "current"),
    ]
    
    for str1, str2 in test_pairs:
        similarity = ErrorHandler._calculate_similarity(str1, str2)
        print(f"'{str1}' vs '{str2}' -> {similarity:.2f}")


def main():
    """Run all error handling demonstrations"""
    print("🏦 BANKING SYSTEM - ERROR HANDLING DEMONSTRATION")
    print("=" * 60)
    print("This demo shows the comprehensive error handling system")
    print("and how it improves user experience with better messages,")
    print("suggestions, and help integration.")
    
    # Run all demonstrations
    demo_session_expired_error()
    demo_insufficient_funds_error()
    demo_invalid_account_error()
    demo_invalid_amount_error()
    demo_command_not_found_error()
    demo_command_suggestions()
    demo_help_text_integration()
    demo_validation_system()
    demo_error_context()
    demo_enhanced_integration()
    demo_similarity_algorithm()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("The error handling system provides:")
    print("✅ Context-aware error messages")
    print("✅ Actionable suggestions and fixes")
    print("✅ Command similarity detection")
    print("✅ Integrated help text")
    print("✅ Comprehensive validation")
    print("✅ Error context tracking")
    print("✅ Enhanced user experience")
    print("\nTo integrate with existing code, replace print() statements")
    print("with ErrorHandler methods for consistent, helpful error messages.")


if __name__ == "__main__":
    main()