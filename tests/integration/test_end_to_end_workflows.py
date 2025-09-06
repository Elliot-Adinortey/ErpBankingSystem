"""
End-to-End Workflow Tests

This module tests complete user workflows from start to finish,
simulating real-world usage scenarios.
"""

import unittest
import sys
import os
import tempfile
import json
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.user import User, register_user, login_user
from src.ui.interactive_session import InteractiveSession
from src.utils.data_storage import save_users_to_file, load_users_from_file
from src.utils.audit_logger import get_audit_logger
from src.utils.security_utils import SessionManager


class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete end-to-end user workflows"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = tempfile.mkdtemp()
        cls.original_dir = os.getcwd()
        os.chdir(cls.test_dir)
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.chdir(cls.original_dir)
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def setUp(self):
        """Set up each test"""
        self.users = {}
        
    def test_new_user_complete_workflow(self):
        """Test complete workflow for a new user from registration to advanced operations"""
        
        # Step 1: User Registration
        success = register_user(self.users, "newuser", "SecurePass123", "newuser@example.com")
        self.assertTrue(success, "User registration should succeed")
        
        # Step 2: User Login
        user = login_user(self.users, "newuser", "SecurePass123")
        self.assertIsNotNone(user, "User login should succeed")
        self.assertEqual(user.username, "newuser")
        
        # Step 3: Create Multiple Accounts
        # Create savings account with nickname
        savings_account = user.create_account_with_nickname(
            "savings", 2000.0, 0, "Emergency Fund"
        )
        self.assertEqual(savings_account.nickname, "Emergency Fund")
        self.assertEqual(savings_account.balance, 2000.0)
        
        # Create current account with overdraft
        current_account = user.create_account_with_nickname(
            "current", 1000.0, 500.0, "Daily Expenses"
        )
        self.assertEqual(current_account.overdraft_limit, 500.0)
        
        # Create salary account
        salary_account = user.create_account_with_nickname(
            "salary", 0.0, 0, "Work Account"
        )
        
        # Step 4: Simulate Monthly Salary Deposit
        salary_account.deposit(3500.0)
        self.assertEqual(salary_account.balance, 3500.0)
        
        # Step 5: Budget Allocation Transfers
        # Transfer to savings (emergency fund)
        success, message, transfer_id1 = user.transfer_between_accounts(
            "Work Account", "Emergency Fund", 500.0, "Monthly savings"
        )
        self.assertTrue(success)
        
        # Transfer to current account (living expenses)
        success, message, transfer_id2 = user.transfer_between_accounts(
            "Work Account", "Daily Expenses", 2500.0, "Monthly budget"
        )
        self.assertTrue(success)
        
        # Step 6: Daily Banking Operations
        # Withdraw cash from current account
        current_account.withdraw(200.0)
        
        # Make a purchase (withdrawal)
        current_account.withdraw(150.0)
        
        # Receive a refund (deposit)
        current_account.deposit(75.0)
        
        # Step 7: Emergency Expense (using overdraft)
        current_account.withdraw(1800.0)  # This should use overdraft
        
        # Verify overdraft was used
        self.assertLess(current_account.balance, 0)
        self.assertGreaterEqual(
            current_account.balance + current_account.overdraft_limit, 0
        )
        
        # Step 8: Cover overdraft from savings
        success, message, transfer_id3 = user.transfer_between_accounts(
            "Emergency Fund", "Daily Expenses", 500.0, "Cover overdraft"
        )
        self.assertTrue(success)
        
        # Step 9: Verify Final Balances
        expected_salary = 3500.0 - 500.0 - 2500.0  # 500
        expected_savings = 2000.0 + 500.0 - 500.0  # 2000
        expected_current = 1000.0 + 2500.0 - 200.0 - 150.0 + 75.0 - 1800.0 + 500.0  # 1925
        
        self.assertEqual(salary_account.balance, expected_salary)
        self.assertEqual(savings_account.balance, expected_savings)
        self.assertEqual(current_account.balance, expected_current)
        
        # Step 10: Generate Account Summary
        summary = user.get_enhanced_summary()
        self.assertEqual(summary['total_accounts'], 3)
        self.assertEqual(summary['total_balance'], expected_salary + expected_savings + expected_current)
        
        # Step 11: Review Transaction History
        transaction_manager = user.transaction_manager
        history = transaction_manager.get_transaction_history()
        
        # Should have multiple transactions
        self.assertGreater(history['total_count'], 8)
        
        # Step 12: Export Data for Records
        export_manager = user.data_export_manager
        csv_file = export_manager.export_data('transactions', 'csv')
        self.assertTrue(os.path.exists(csv_file))
        
        # Step 13: Generate Statement
        statement_generator = user.statement_generator
        statement = statement_generator.generate_statement("Daily Expenses")
        self.assertIn('Daily Expenses', statement['formatted_content'])
        
        print("✓ Complete new user workflow test passed")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_session_workflow(self, mock_print, mock_input):
        """Test complete interactive session workflow"""
        
        # Set up user with accounts
        register_user(self.users, "interactive_user", "TestPass123", "interactive@example.com")
        user = self.users["interactive_user"]
        
        user.create_account_with_nickname("savings", 1500.0, 0, "Vacation Fund")
        user.create_account_with_nickname("current", 800.0, 300.0, "Main Account")
        
        # Create interactive session
        session = InteractiveSession(user, self.users)
        
        # Test account management workflow
        mock_input.side_effect = ['']  # Press Enter to continue
        session._list_accounts()
        
        # Verify accounts were displayed
        print_calls = [str(call) for call in mock_print.call_args_list]
        account_output = ''.join(print_calls)
        self.assertIn("Vacation Fund", account_output)
        self.assertIn("Main Account", account_output)
        
        # Reset mocks
        mock_print.reset_mock()
        mock_input.reset_mock()
        
        # Test banking operations workflow
        mock_input.side_effect = [
            '1',    # Select first account (savings)
            '200',  # Deposit amount
            ''      # Press Enter to continue
        ]
        
        original_balance = user.get_account("savings").balance
        session._deposit_money()
        new_balance = user.get_account("savings").balance
        
        self.assertEqual(new_balance, original_balance + 200.0)
        
        # Reset mocks
        mock_print.reset_mock()
        mock_input.reset_mock()
        
        # Test transfer workflow
        mock_input.side_effect = [
            '1',    # From savings (first account)
            '1',    # To current (first in remaining)
            '300',  # Transfer amount
            'Budget transfer',  # Memo
            ''      # Press Enter to continue
        ]
        
        savings_balance = user.get_account("savings").balance
        current_balance = user.get_account("current").balance
        
        session._transfer_money()
        
        new_savings = user.get_account("savings").balance
        new_current = user.get_account("current").balance
        
        self.assertEqual(new_savings, savings_balance - 300.0)
        self.assertEqual(new_current, current_balance + 300.0)
        
        print("✓ Interactive session workflow test passed")
    
    def test_business_scenario_workflow(self):
        """Test realistic business scenario workflow"""
        
        # Scenario: Small business owner managing business and personal accounts
        
        # Step 1: Create business owner user
        register_user(self.users, "business_owner", "BusinessPass123", "owner@business.com")
        user = self.users["business_owner"]
        
        # Step 2: Set up business accounts
        business_checking = user.create_account_with_nickname(
            "current", 10000.0, 2000.0, "Business Checking"
        )
        business_savings = user.create_account_with_nickname(
            "savings", 25000.0, 0, "Business Savings"
        )
        personal_account = user.create_account_with_nickname(
            "salary", 5000.0, 0, "Personal Account"
        )
        
        # Step 3: Monthly business operations
        # Receive customer payments
        business_checking.deposit(8500.0)  # Customer payments
        business_checking.deposit(3200.0)  # More payments
        
        # Pay business expenses
        business_checking.withdraw(2500.0)  # Rent
        business_checking.withdraw(1200.0)  # Utilities
        business_checking.withdraw(800.0)   # Supplies
        
        # Step 4: Pay owner salary
        success, message, _ = user.transfer_between_accounts(
            "Business Checking", "Personal Account", 4000.0, "Owner salary"
        )
        self.assertTrue(success)
        
        # Step 5: Build business reserves
        success, message, _ = user.transfer_between_accounts(
            "Business Checking", "Business Savings", 5000.0, "Monthly reserves"
        )
        self.assertTrue(success)
        
        # Step 6: Emergency business expense (using overdraft)
        business_checking.withdraw(8000.0)  # Large unexpected expense
        
        # Verify overdraft was used appropriately
        self.assertLess(business_checking.balance, 0)
        
        # Step 7: Cover overdraft from savings
        success, message, _ = user.transfer_between_accounts(
            "Business Savings", "Business Checking", 3000.0, "Cover emergency expense"
        )
        self.assertTrue(success)
        
        # Step 8: Generate business reports
        transaction_manager = user.transaction_manager
        
        # Get business checking transactions
        business_history = transaction_manager.get_transaction_history(
            account="Business Checking"
        )
        self.assertGreater(business_history['total_count'], 8)
        
        # Get transaction summary for tax purposes
        summary = transaction_manager.get_transaction_summary(
            account="Business Checking"
        )
        self.assertGreater(summary['total_deposits'], 10000.0)
        self.assertGreater(summary['total_withdrawals'], 5000.0)
        
        # Step 9: Export business data for accounting
        export_manager = user.data_export_manager
        business_csv = export_manager.export_data(
            'transactions', 'csv', account_identifier="Business Checking"
        )
        self.assertTrue(os.path.exists(business_csv))
        
        # Step 10: Verify final business position
        total_business_assets = business_checking.balance + business_savings.balance
        self.assertGreater(total_business_assets, 20000.0)
        
        print("✓ Business scenario workflow test passed")
    
    def test_family_budget_workflow(self):
        """Test family budget management workflow"""
        
        # Scenario: Family managing household budget with multiple accounts
        
        # Step 1: Create family account
        register_user(self.users, "family_head", "FamilyPass123", "family@example.com")
        user = self.users["family_head"]
        
        # Step 2: Set up family accounts
        joint_checking = user.create_account_with_nickname(
            "current", 3000.0, 500.0, "Joint Checking"
        )
        emergency_fund = user.create_account_with_nickname(
            "savings", 8000.0, 0, "Emergency Fund"
        )
        vacation_fund = user.create_account_with_nickname(
            "salary", 2000.0, 0, "Vacation Savings"
        )
        
        # Step 3: Monthly income deposits
        joint_checking.deposit(4500.0)  # Salary 1
        joint_checking.deposit(3200.0)  # Salary 2
        
        # Step 4: Automatic savings transfers
        # Emergency fund contribution
        success, message, _ = user.transfer_between_accounts(
            "Joint Checking", "Emergency Fund", 800.0, "Monthly emergency savings"
        )
        self.assertTrue(success)
        
        # Vacation fund contribution
        success, message, _ = user.transfer_between_accounts(
            "Joint Checking", "Vacation Savings", 400.0, "Monthly vacation savings"
        )
        self.assertTrue(success)
        
        # Step 5: Monthly expenses
        expenses = [
            (1200.0, "Mortgage payment"),
            (800.0, "Groceries"),
            (300.0, "Utilities"),
            (200.0, "Insurance"),
            (150.0, "Gas"),
            (100.0, "Phone bill")
        ]
        
        for amount, description in expenses:
            joint_checking.withdraw(amount)
        
        # Step 6: Unexpected expense (car repair)
        joint_checking.withdraw(1500.0)  # Uses overdraft
        
        # Step 7: Cover overdraft from emergency fund
        success, message, _ = user.transfer_between_accounts(
            "Emergency Fund", "Joint Checking", 1000.0, "Car repair coverage"
        )
        self.assertTrue(success)
        
        # Step 8: Plan vacation expense
        success, message, _ = user.transfer_between_accounts(
            "Vacation Savings", "Joint Checking", 1200.0, "Vacation expenses"
        )
        self.assertTrue(success)
        
        # Step 9: Review family finances
        financial_overview = user.get_financial_overview()
        
        # Should have positive total balance
        self.assertGreater(financial_overview['total_balance'], 0)
        
        # Step 10: Generate family budget report
        transaction_manager = user.transaction_manager
        
        # Get last 30 days of transactions
        recent_date = datetime.now() - timedelta(days=30)
        recent_transactions = transaction_manager.get_transaction_history(
            start_date=recent_date
        )
        
        self.assertGreater(recent_transactions['total_count'], 10)
        
        # Step 11: Export for budget tracking
        export_manager = user.data_export_manager
        family_budget_file = export_manager.export_data('full_backup', 'json')
        self.assertTrue(os.path.exists(family_budget_file))
        
        print("✓ Family budget workflow test passed")
    
    def test_student_account_workflow(self):
        """Test student account management workflow"""
        
        # Scenario: Student managing limited finances with careful budgeting
        
        # Step 1: Create student account
        register_user(self.users, "student", "StudentPass123", "student@university.edu")
        user = self.users["student"]
        
        # Step 2: Set up student accounts
        checking = user.create_account_with_nickname(
            "current", 500.0, 100.0, "Student Checking"
        )
        savings = user.create_account_with_nickname(
            "savings", 1200.0, 0, "Textbook Fund"
        )
        
        # Step 3: Receive financial aid
        checking.deposit(2500.0)  # Scholarship payment
        
        # Step 4: Pay tuition (large expense)
        checking.withdraw(2000.0)
        
        # Step 5: Budget for textbooks
        success, message, _ = user.transfer_between_accounts(
            "Textbook Fund", "Student Checking", 400.0, "Textbook purchase"
        )
        self.assertTrue(success)
        
        # Step 6: Monthly living expenses
        monthly_expenses = [
            (300.0, "Rent"),
            (200.0, "Groceries"),
            (50.0, "Phone"),
            (30.0, "Transportation")
        ]
        
        for amount, description in monthly_expenses:
            checking.withdraw(amount)
        
        # Step 7: Part-time job income
        checking.deposit(600.0)  # Part-time work
        
        # Step 8: Emergency expense (medical)
        checking.withdraw(250.0)  # Uses some overdraft
        
        # Step 9: Monitor account closely
        balance = checking.get_balance()
        available = balance + checking.overdraft_limit if balance < 0 else balance
        
        # Should still have some funds available
        self.assertGreater(available, 0)
        
        # Step 10: Review spending patterns
        transaction_manager = user.transaction_manager
        summary = transaction_manager.get_transaction_summary()
        
        # Should have both income and expenses
        self.assertGreater(summary['total_deposits'], 0)
        self.assertGreater(summary['total_withdrawals'], 0)
        
        # Step 11: Plan for next semester
        remaining_savings = savings.balance
        self.assertGreater(remaining_savings, 0)
        
        print("✓ Student account workflow test passed")
    
    def test_audit_and_security_workflow(self):
        """Test audit logging and security features throughout workflows"""
        
        # Step 1: Create user with audit logging
        register_user(self.users, "audit_user", "AuditPass123", "audit@example.com")
        user = self.users["audit_user"]
        
        # Step 2: Create session for tracking
        token = SessionManager.create_session("audit_user")
        self.assertIsNotNone(token)
        
        # Step 3: Perform audited operations
        audit_logger = get_audit_logger()
        
        # Log account creation
        account = user.create_account_with_nickname("savings", 1000.0, 0, "Audit Test")
        
        # Log banking operations
        account.deposit(500.0)
        account.withdraw(200.0)
        
        # Log transfer
        current_account = user.create_account_with_nickname("current", 800.0, 200.0)
        success, message, transfer_id = user.transfer_between_accounts(
            "savings", "current", 300.0, "Audit transfer"
        )
        self.assertTrue(success)
        
        # Step 4: Verify session is still valid
        username = SessionManager.validate_session(token)
        self.assertEqual(username, "audit_user")
        
        # Step 5: Test session timeout
        # Simulate expired session
        SessionManager.cleanup_expired_sessions()
        
        # Step 6: Test security validation
        # Attempt invalid operations
        invalid_success, invalid_message, _ = user.transfer_between_accounts(
            "nonexistent", "current", 100.0
        )
        self.assertFalse(invalid_success)
        
        # Step 7: Invalidate session
        success = SessionManager.invalidate_session(token)
        self.assertTrue(success)
        
        # Verify session is now invalid
        username = SessionManager.validate_session(token)
        self.assertIsNone(username)
        
        print("✓ Audit and security workflow test passed")
    
    def test_data_persistence_workflow(self):
        """Test data persistence across operations and sessions"""
        
        # Step 1: Create user and perform operations
        register_user(self.users, "persist_user", "PersistPass123", "persist@example.com")
        user = self.users["persist_user"]
        
        # Create accounts and perform transactions
        savings = user.create_account_with_nickname("savings", 2000.0, 0, "Persistent Savings")
        current = user.create_account_with_nickname("current", 1000.0, 500.0, "Persistent Current")
        
        # Perform various operations
        savings.deposit(300.0)
        current.withdraw(150.0)
        user.transfer_between_accounts("savings", "current", 400.0, "Test transfer")
        
        # Step 2: Save data
        save_users_to_file(self.users)
        
        # Step 3: Clear memory and reload
        original_savings_balance = savings.balance
        original_current_balance = current.balance
        original_transaction_count = len(savings.transactions) + len(current.transactions)
        
        # Clear users dictionary
        self.users.clear()
        
        # Step 4: Load data from file
        loaded_users = load_users_from_file()
        loaded_user = loaded_users["persist_user"]
        
        # Step 5: Verify data persistence
        loaded_savings = loaded_user.get_account("Persistent Savings")
        loaded_current = loaded_user.get_account("Persistent Current")
        
        self.assertEqual(loaded_savings.balance, original_savings_balance)
        self.assertEqual(loaded_current.balance, original_current_balance)
        self.assertEqual(loaded_savings.nickname, "Persistent Savings")
        self.assertEqual(loaded_current.nickname, "Persistent Current")
        
        # Verify transaction history persisted
        loaded_transaction_count = len(loaded_savings.transactions) + len(loaded_current.transactions)
        self.assertEqual(loaded_transaction_count, original_transaction_count)
        
        # Step 6: Continue operations with loaded data
        loaded_savings.deposit(100.0)
        new_balance = loaded_savings.balance
        
        # Step 7: Save again and verify
        save_users_to_file(loaded_users)
        
        final_users = load_users_from_file()
        final_user = final_users["persist_user"]
        final_savings = final_user.get_account("Persistent Savings")
        
        self.assertEqual(final_savings.balance, new_balance)
        
        print("✓ Data persistence workflow test passed")


if __name__ == '__main__':
    unittest.main()