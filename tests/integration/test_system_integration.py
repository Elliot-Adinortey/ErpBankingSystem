"""
Comprehensive System Integration Tests

This module contains integration tests that verify all components work together
correctly and test complete user workflows end-to-end.
"""

import unittest
import sys
import os
import tempfile
import json
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.user import User, register_user, login_user
from src.core.account import Account
from src.ui.interactive_session import InteractiveSession
from src.managers.transfer_manager import TransferManager
from src.managers.transaction_manager import TransactionManager
from src.managers.batch_manager import BatchManager
from src.utils.audit_logger import AuditLogger, AuditEventType
from src.utils.data_export_import import DataExportImportManager
from src.utils.statement_generator import StatementGenerator
from src.utils.error_handler import ErrorHandler
from src.utils.help_system import HelpSystem
from src.utils.security_utils import SessionManager
from src.utils.data_storage import save_users_to_file, load_users_from_file


class TestSystemIntegration(unittest.TestCase):
    """Comprehensive system integration tests"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = tempfile.mkdtemp()
        cls.original_dir = os.getcwd()
        
        # Create test files
        cls.test_users_file = os.path.join(cls.test_dir, 'users_data.json')
        cls.test_audit_file = os.path.join(cls.test_dir, 'audit.log')
        cls.test_session_file = os.path.join(cls.test_dir, '.session')
        
        # Change to test directory
        os.chdir(cls.test_dir)
        
        # Initialize test data
        cls.users = {}
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.chdir(cls.original_dir)
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def setUp(self):
        """Set up each test"""
        # Clear users for each test
        self.users = {}
        
        # Create test user
        register_user(self.users, "testuser", "TestPass123", "test@example.com")
        self.user = self.users["testuser"]
        
        # Create test accounts with different configurations
        self.user.create_account_with_nickname("savings", 1000.0, 0, "Emergency Fund")
        self.user.create_account_with_nickname("current", 500.0, 200.0, "Daily Spending")
        self.user.create_account_with_nickname("salary", 2000.0, 0, "Work Account")
        
        # Add some initial transactions
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        
        savings_account.deposit(100.0)
        savings_account.withdraw(50.0)
        current_account.deposit(200.0)
        
    def test_complete_user_workflow(self):
        """Test complete user workflow from registration to complex operations"""
        # 1. User Registration and Login
        new_users = {}
        success = register_user(new_users, "newuser", "NewPass123", "new@example.com")
        self.assertTrue(success)
        
        user = login_user(new_users, "newuser", "NewPass123")
        self.assertIsNotNone(user)
        
        # 2. Account Creation with Enhanced Features
        account1 = user.create_account_with_nickname("savings", 1500.0, 0, "Vacation Fund")
        account2 = user.create_account_with_nickname("current", 800.0, 300.0, "Main Account")
        
        self.assertEqual(account1.nickname, "Vacation Fund")
        self.assertEqual(account2.overdraft_limit, 300.0)
        
        # 3. Banking Operations
        account1.deposit(200.0)
        account2.withdraw(100.0)
        
        # 4. Account-to-Account Transfer
        success, message, transfer_id = user.transfer_between_accounts(
            "Vacation Fund", "Main Account", 300.0, "Monthly budget transfer"
        )
        self.assertTrue(success)
        self.assertIsNotNone(transfer_id)
        
        # 5. Verify Final State
        self.assertEqual(account1.balance, 1400.0)  # 1500 + 200 - 300
        self.assertEqual(account2.balance, 1000.0)  # 800 - 100 + 300
        
        # 6. Transaction History
        transaction_manager = TransactionManager(user)
        history = transaction_manager.get_transaction_history()
        self.assertGreater(history['total_count'], 0)
        
        # 7. Account Summary
        summary = user.get_enhanced_summary()
        self.assertEqual(summary['total_accounts'], 2)
        self.assertEqual(summary['total_balance'], 2400.0)
    
    def test_interactive_session_integration(self):
        """Test interactive session with all menu operations"""
        session = InteractiveSession(self.user, self.users)
        
        # Test session initialization
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.session_active)
        
        # Test timeout checking
        self.assertTrue(session._check_session_timeout())
        
        # Test activity tracking
        original_activity = session.last_activity
        session._update_activity()
        self.assertGreater(session.last_activity, original_activity)
        
        # Test menu operations (without user input)
        with patch('builtins.input'), patch('builtins.print'):
            # Test account listing
            session._list_accounts()
            
            # Test financial overview
            session._financial_overview()
            
            # Test account details
            session._account_details()
            
            # Test transaction summary
            session._transaction_summary()
    
    def test_transfer_system_integration(self):
        """Test complete transfer system integration"""
        transfer_manager = TransferManager(self.user)
        
        # Test validation
        is_valid, message, from_acc, to_acc = transfer_manager.validate_transfer(
            "Emergency Fund", "Daily Spending", 200.0
        )
        self.assertTrue(is_valid)
        self.assertIsNotNone(from_acc)
        self.assertIsNotNone(to_acc)
        
        # Test execution
        success, exec_message, transfer_id = transfer_manager.execute_transfer(
            "Emergency Fund", "Daily Spending", 200.0, "Test transfer"
        )
        self.assertTrue(success)
        self.assertIsNotNone(transfer_id)
        
        # Test history retrieval
        transfers = transfer_manager.get_transfer_history()
        self.assertGreater(len(transfers), 0)
        
        # Test transfer by ID
        retrieved = transfer_manager.get_transfer_by_id(transfer_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.memo, "Test transfer")
    
    def test_transaction_management_integration(self):
        """Test transaction management system integration"""
        transaction_manager = TransactionManager(self.user)
        
        # Add more transactions for testing
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        
        savings_account.deposit(300.0)
        current_account.withdraw(150.0)
        
        # Test transaction history with pagination
        history = transaction_manager.get_transaction_history(page_size=5)
        self.assertLessEqual(len(history['transactions']), 5)
        self.assertGreater(history['total_count'], 0)
        
        # Test filtering by account
        savings_history = transaction_manager.get_transaction_history(account="savings")
        for transaction in savings_history['transactions']:
            self.assertIn("Emergency Fund", transaction['account'])
        
        # Test date filtering
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)
        
        date_filtered = transaction_manager.get_transaction_history(
            start_date=yesterday, end_date=tomorrow
        )
        self.assertGreater(date_filtered['total_count'], 0)
        
        # Test transaction summary
        summary = transaction_manager.get_transaction_summary()
        self.assertGreater(summary['total_transactions'], 0)
        self.assertGreater(summary['total_deposits'], 0)
        
        # Test export functionality
        csv_export = transaction_manager.export_transactions(
            history['transactions'], 'csv'
        )
        self.assertIn('Date,Account,Account Type', csv_export)
        
        json_export = transaction_manager.export_transactions(
            history['transactions'], 'json'
        )
        self.assertIn('"date":', json_export)
    
    def test_audit_logging_integration(self):
        """Test audit logging integration across all operations"""
        audit_logger = AuditLogger(self.test_audit_file)
        
        # Test login logging
        audit_logger.log_login_attempt("testuser", True, "test_session_123")
        
        # Test banking operation logging
        audit_logger.log_banking_operation(
            operation_type="deposit",
            user="testuser",
            account_identifier="savings",
            amount=100.0,
            success=True,
            session_id="test_session_123"
        )
        
        # Test error logging
        test_error = ValueError("Test error")
        audit_logger.log_error(
            error=test_error,
            context={"operation": "test"},
            user="testuser"
        )
        
        # Test operation logging
        audit_logger.log_operation(
            event_type=AuditEventType.ACCOUNT_CREATE,
            user="testuser",
            operation="Account creation test",
            success=True
        )
        
        # Verify logs were created
        self.assertTrue(os.path.exists(self.test_audit_file))
        
        with open(self.test_audit_file, 'r') as f:
            log_content = f.read()
            self.assertIn("LOGIN_ATTEMPT", log_content)
            self.assertIn("BANKING_OPERATION", log_content)
            self.assertIn("ERROR", log_content)
            self.assertIn("ACCOUNT_CREATE", log_content)
    
    def test_data_export_import_integration(self):
        """Test data export and import system integration"""
        export_manager = DataExportImportManager(self.user)
        
        # Test transaction export
        csv_file = export_manager.export_data('transactions', 'csv')
        self.assertTrue(os.path.exists(csv_file))
        
        json_file = export_manager.export_data('accounts', 'json')
        self.assertTrue(os.path.exists(json_file))
        
        # Test full backup
        backup_file = export_manager.export_data('full_backup', 'json')
        self.assertTrue(os.path.exists(backup_file))
        
        # Verify backup content
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
            self.assertIn('user_info', backup_data)
            self.assertIn('accounts', backup_data)
            self.assertIn('transactions', backup_data)
    
    def test_statement_generation_integration(self):
        """Test statement generation integration"""
        statement_generator = StatementGenerator(self.user)
        
        # Generate statement for savings account
        result = statement_generator.generate_statement("savings")
        
        self.assertIn('formatted_content', result)
        self.assertIn('metadata', result)
        self.assertIn('Emergency Fund', result['formatted_content'])
        
        # Test statement export
        filepath = statement_generator.export_statement_to_file(result)
        self.assertTrue(os.path.exists(filepath))
    
    def test_batch_operations_integration(self):
        """Test batch operations integration"""
        batch_manager = BatchManager(self.user)
        
        # Create test batch file
        batch_operations = [
            {"operation": "deposit", "account": "savings", "amount": 100.0},
            {"operation": "withdraw", "account": "current", "amount": 50.0},
            {"operation": "transfer", "from_account": "savings", "to_account": "current", "amount": 75.0}
        ]
        
        batch_file = os.path.join(self.test_dir, 'test_batch.json')
        with open(batch_file, 'w') as f:
            json.dump(batch_operations, f)
        
        # Execute batch operations
        results = batch_manager.execute_batch_file(batch_file)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(all(result['success'] for result in results))
        
        # Verify operations were executed
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        
        # Original: savings=1000, current=500
        # After initial transactions in setUp: savings=1050, current=700
        # After batch: deposit 100 to savings, withdraw 50 from current, transfer 75 savings->current
        # Expected: savings=1075, current=725
        self.assertEqual(savings_account.balance, 1075.0)
        self.assertEqual(current_account.balance, 725.0)
    
    def test_error_handling_integration(self):
        """Test error handling integration across components"""
        # Test insufficient funds error
        success, message, _ = self.user.transfer_between_accounts(
            "savings", "current", 5000.0
        )
        self.assertFalse(success)
        self.assertIn("Insufficient funds", message)
        
        # Test invalid account error
        success, message, _ = self.user.transfer_between_accounts(
            "nonexistent", "current", 100.0
        )
        self.assertFalse(success)
        self.assertIn("not found", message)
        
        # Test error handler suggestions
        suggestion = ErrorHandler.suggest_command_fix("depositt")
        self.assertIn("deposit", suggestion.lower())
    
    def test_help_system_integration(self):
        """Test help system integration"""
        # Test command help
        help_text = HelpSystem.get_command_help("transfer", detailed=True)
        self.assertIn("TRANSFER COMMAND", help_text)
        self.assertIn("Examples:", help_text)
        
        # Test interactive help
        interactive_help = HelpSystem.get_interactive_help("main_menu")
        self.assertIn("Interactive Mode Help", interactive_help)
        
        # Test all commands listing
        all_commands = HelpSystem.get_all_commands()
        self.assertIn("transfer", all_commands)
        self.assertIn("account_summary", all_commands)
    
    def test_session_management_integration(self):
        """Test session management integration"""
        # Create session
        token = SessionManager.create_session("testuser")
        self.assertIsNotNone(token)
        
        # Validate session
        username = SessionManager.validate_session(token)
        self.assertEqual(username, "testuser")
        
        # Test session cleanup
        SessionManager.cleanup_expired_sessions()
        
        # Invalidate session
        success = SessionManager.invalidate_session(token)
        self.assertTrue(success)
        
        # Verify session is invalid
        username = SessionManager.validate_session(token)
        self.assertIsNone(username)
    
    def test_data_persistence_integration(self):
        """Test data persistence across operations"""
        # Save initial state
        save_users_to_file(self.users)
        
        # Perform operations
        self.user.transfer_between_accounts("savings", "current", 100.0)
        self.user.get_account("savings").deposit(50.0)
        
        # Save changes
        save_users_to_file(self.users)
        
        # Load data and verify persistence
        loaded_users = load_users_from_file()
        loaded_user = loaded_users["testuser"]
        
        # Verify account balances persisted
        savings_balance = loaded_user.get_account("savings").balance
        current_balance = loaded_user.get_account("current").balance
        
        self.assertEqual(savings_balance, 1000.0)  # 1050 - 100 + 50
        self.assertEqual(current_balance, 800.0)   # 700 + 100
    
    def test_cross_component_data_consistency(self):
        """Test data consistency across all components"""
        # Perform operations through different managers
        transfer_manager = TransferManager(self.user)
        transaction_manager = TransactionManager(self.user)
        
        # Execute transfer
        success, message, transfer_id = transfer_manager.execute_transfer(
            "savings", "current", 150.0, "Consistency test"
        )
        self.assertTrue(success)
        
        # Verify through transaction manager
        history = transaction_manager.get_transaction_history()
        transfer_transactions = [
            t for t in history['transactions'] 
            if hasattr(t.get('transaction_obj'), 'transfer_id') and 
               t['transaction_obj'].transfer_id == transfer_id
        ]
        self.assertEqual(len(transfer_transactions), 2)  # One for each account
        
        # Verify balances are consistent
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        
        # Calculate expected balances
        # Initial: savings=1050 (after setUp), current=700 (after setUp)
        # After transfer: savings=900, current=850
        self.assertEqual(savings_account.balance, 900.0)
        self.assertEqual(current_account.balance, 850.0)
        
        # Verify transaction counts match
        savings_transactions = len(savings_account.transactions)
        current_transactions = len(current_account.transactions)
        
        # Should have initial transactions plus transfer transactions
        self.assertGreater(savings_transactions, 2)
        self.assertGreater(current_transactions, 1)
    
    def test_security_measures_integration(self):
        """Test security measures across all features"""
        # Test session timeout simulation
        session = InteractiveSession(self.user, self.users)
        
        # Simulate expired session
        session.last_activity = datetime.now() - timedelta(minutes=35)
        self.assertFalse(session._check_session_timeout())
        
        # Test account ownership validation in transfers
        other_user = User("otheruser", "password", "other@test.com")
        other_user.create_account_with_nickname("savings", 1000.0)
        
        # Should not be able to transfer to accounts not owned by user
        success, message, _ = self.user.transfer_between_accounts(
            "savings", "nonexistent", 100.0
        )
        self.assertFalse(success)
        
        # Test input validation
        transfer_manager = TransferManager(self.user)
        is_valid, message, _, _ = transfer_manager.validate_transfer(
            "savings", "current", -100.0  # Negative amount
        )
        self.assertFalse(is_valid)
    
    def test_performance_with_large_datasets(self):
        """Test system performance with larger datasets"""
        # Add many transactions
        savings_account = self.user.get_account("savings")
        
        for i in range(100):
            if i % 2 == 0:
                savings_account.deposit(10.0)
            else:
                savings_account.withdraw(5.0)
        
        # Test transaction history performance
        transaction_manager = TransactionManager(self.user)
        start_time = datetime.now()
        
        history = transaction_manager.get_transaction_history(page_size=50)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (1 second)
        self.assertLess(processing_time, 1.0)
        self.assertGreater(history['total_count'], 100)
        
        # Test filtering performance
        start_time = datetime.now()
        
        filtered = transaction_manager.get_transaction_history(
            account="savings",
            start_date=datetime.now() - timedelta(days=1)
        )
        
        end_time = datetime.now()
        filtering_time = (end_time - start_time).total_seconds()
        
        self.assertLess(filtering_time, 1.0)
        self.assertGreater(filtered['total_count'], 0)


if __name__ == '__main__':
    unittest.main()