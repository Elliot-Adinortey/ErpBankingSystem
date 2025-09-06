"""
Integration tests for Export/Import CLI commands
"""

import unittest
import os
import tempfile
import shutil
import json
import csv
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.core.user import User
from src.core.account import Account
from src.core.transaction import Transaction
from src.managers.transfer_manager import TransferTransaction
from src.utils.statement_generator import StatementGenerator
from src.utils.data_export_import import DataExportImportManager


class TestExportImportCLI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test accounts with transactions
        self.savings_account = Account("savings", 1000.0, 0, "My Savings")
        self.current_account = Account("current", 500.0, 200.0, "Daily Account")
        
        self.user.accounts = [self.savings_account, self.current_account]
        
        # Add test transactions
        base_date = datetime.now() - timedelta(days=10)
        
        self.savings_account.transactions = [
            Transaction(100.0, "deposit", base_date - timedelta(days=5)),
            Transaction(50.0, "withdrawal", base_date - timedelta(days=2)),
            Transaction(25.0, "interest", base_date)
        ]
        
        # Add transfer transaction
        transfer_tx = TransferTransaction(200.0, "savings", "current", "Test transfer")
        transfer_tx.is_outgoing = False
        transfer_tx.date = base_date - timedelta(days=1)
        
        self.current_account.transactions = [
            Transaction(300.0, "deposit", base_date - timedelta(days=3)),
            transfer_tx
        ]
        
        # Create temporary directory for file tests
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_statement_generation_integration(self):
        """Test statement generation functionality"""
        statement_generator = StatementGenerator(self.user)
        
        # Test basic statement generation
        result = statement_generator.generate_statement("savings")
        
        self.assertIn('account', result)
        self.assertIn('statement_data', result)
        self.assertIn('formatted_content', result)
        
        # Check statement content
        content = result['formatted_content']
        self.assertIn("ACCOUNT STATEMENT", content)
        self.assertIn("My Savings", content)
        self.assertIn("testuser", content)
        self.assertIn("TRANSACTION DETAILS", content)
    
    def test_statement_export_to_file(self):
        """Test statement export to file"""
        statement_generator = StatementGenerator(self.user)
        
        # Generate and export statement
        result = statement_generator.generate_statement("savings")
        filepath = statement_generator.export_statement_to_file(result)
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.txt'))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn("ACCOUNT STATEMENT", content)
            self.assertIn("My Savings", content)
    
    def test_multi_account_statement(self):
        """Test consolidated multi-account statement"""
        statement_generator = StatementGenerator(self.user)
        
        # Generate consolidated statement
        result = statement_generator.generate_multi_account_statement()
        
        self.assertIn('consolidated_data', result)
        self.assertIn('formatted_content', result)
        
        # Check consolidated data
        consolidated_data = result['consolidated_data']
        self.assertEqual(consolidated_data['summary']['total_accounts'], 2)
        self.assertGreater(consolidated_data['summary']['total_closing_balance'], 0)
        
        # Check content includes both accounts
        content = result['formatted_content']
        self.assertIn("CONSOLIDATED ACCOUNT STATEMENT", content)
        self.assertIn("My Savings", content)
        self.assertIn("Daily Account", content)
    
    def test_transaction_export_csv(self):
        """Test transaction export to CSV"""
        export_manager = DataExportImportManager(self.user)
        
        # Export all transactions
        filepath = export_manager.export_data("transactions", "csv")
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.csv'))
        
        # Check CSV content
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should have transactions from both accounts
            self.assertGreater(len(rows), 0)
            
            # Check required columns
            expected_columns = ['date', 'account', 'account_type', 'transaction_type', 
                              'amount', 'balance_after', 'transfer_id', 'memo', 'description']
            self.assertEqual(set(reader.fieldnames), set(expected_columns))
            
            # Check data integrity
            for row in rows:
                self.assertIn(row['account_type'], ['savings', 'current'])
                self.assertIn(row['transaction_type'], ['deposit', 'withdrawal', 'interest', 'transfer'])
                self.assertTrue(float(row['amount']) > 0)
    
    def test_account_export_json(self):
        """Test account export to JSON"""
        export_manager = DataExportImportManager(self.user)
        
        # Export account data
        filepath = export_manager.export_data("accounts", "json")
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.json'))
        
        # Check JSON content
        with open(filepath, 'r') as f:
            data = json.load(f)
            
            # Check structure
            self.assertIn('export_info', data)
            self.assertIn('accounts', data)
            
            # Check export info
            export_info = data['export_info']
            self.assertEqual(export_info['username'], 'testuser')
            self.assertEqual(export_info['total_accounts'], 2)
            
            # Check accounts data
            accounts = data['accounts']
            self.assertEqual(len(accounts), 2)
            
            # Verify account details
            account_types = {acc['account_type'] for acc in accounts}
            self.assertEqual(account_types, {'savings', 'current'})
            
            # Check transactions are included
            for account in accounts:
                self.assertIn('transactions', account)
                self.assertIsInstance(account['transactions'], list)
    
    def test_full_backup_export(self):
        """Test full backup export"""
        export_manager = DataExportImportManager(self.user)
        
        # Export full backup
        filepath = export_manager.export_data("full_backup", "json")
        
        # Check file was created in backups directory
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue('backups' in filepath)
        self.assertTrue(filepath.endswith('.json'))
        
        # Check backup content
        with open(filepath, 'r') as f:
            data = json.load(f)
            
            # Check structure
            self.assertIn('backup_info', data)
            self.assertIn('user_data', data)
            
            # Check backup includes password hash for restore
            user_data = data['user_data']
            self.assertIn('password_hash', user_data)
            self.assertIn('accounts', user_data)
            self.assertEqual(len(user_data['accounts']), 2)
    
    def test_transaction_import_csv(self):
        """Test transaction import from CSV"""
        # Create test CSV file
        csv_content = """date,account,account_type,transaction_type,amount,memo
2024-01-01 10:00:00,My Savings,savings,deposit,150.0,Test import deposit
2024-01-02 11:00:00,Daily Account,current,withdrawal,75.0,Test import withdrawal"""
        
        csv_file = "test_import_transactions.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Import transactions
        import_manager = DataExportImportManager(self.user)
        result = import_manager.import_data("transactions", csv_file)
        
        # Check import results
        self.assertEqual(result['total_rows'], 2)
        self.assertEqual(result['valid_transactions'], 2)
        self.assertEqual(result['invalid_transactions'], 0)
        self.assertEqual(len(result['errors']), 0)
        
        # Check transactions were added
        self.assertEqual(len(result['imported_transactions']), 2)
        
        # Verify transactions were added to accounts
        savings_tx_count = len(self.savings_account.transactions)
        current_tx_count = len(self.current_account.transactions)
        
        # Should have original transactions plus imported ones
        self.assertGreater(savings_tx_count, 3)  # Original 3 + imported
        self.assertGreater(current_tx_count, 2)  # Original 2 + imported
    
    def test_account_import_json(self):
        """Test account import from JSON"""
        # Create test JSON file
        json_data = {
            "accounts": [
                {
                    "account_type": "salary",
                    "nickname": "Payroll Account",
                    "balance": 2000.0,
                    "overdraft_limit": 0.0
                }
            ]
        }
        
        json_file = "test_import_accounts.json"
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        # Import accounts
        import_manager = DataExportImportManager(self.user)
        result = import_manager.import_data("accounts", json_file)
        
        # Check import results
        self.assertEqual(result['total_accounts'], 1)
        self.assertEqual(result['valid_accounts'], 1)
        self.assertEqual(result['invalid_accounts'], 0)
        self.assertEqual(len(result['errors']), 0)
        
        # Check account was added
        self.assertEqual(len(self.user.accounts), 3)  # Original 2 + imported 1
        
        # Verify imported account
        salary_account = self.user.get_account("salary")
        self.assertIsNotNone(salary_account)
        self.assertEqual(salary_account.nickname, "Payroll Account")
        self.assertEqual(salary_account.balance, 2000.0)
    
    def test_import_validation_only(self):
        """Test import validation without actual import"""
        # Create test CSV file
        csv_content = """date,account,account_type,transaction_type,amount
2024-01-01 10:00:00,My Savings,savings,deposit,100.0"""
        
        csv_file = "test_validation.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Validate only
        import_manager = DataExportImportManager(self.user)
        result = import_manager.import_data("transactions", csv_file, validate_only=True)
        
        # Check validation results
        self.assertEqual(result['valid_transactions'], 1)
        self.assertTrue(result['validation_only'])
        self.assertEqual(len(result['imported_transactions']), 0)
        
        # Verify no transactions were actually imported
        original_tx_count = len(self.savings_account.transactions)
        self.assertEqual(original_tx_count, 3)  # Should remain unchanged
    
    def test_import_error_handling(self):
        """Test import error handling for invalid data"""
        # Create CSV with invalid data
        csv_content = """date,account,account_type,transaction_type,amount
invalid_date,My Savings,savings,deposit,100.0
2024-01-01 10:00:00,NonExistent,savings,deposit,50.0
2024-01-01 10:00:00,My Savings,savings,invalid_type,25.0"""
        
        csv_file = "test_invalid_import.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Import with errors
        import_manager = DataExportImportManager(self.user)
        result = import_manager.import_data("transactions", csv_file)
        
        # Check error handling
        self.assertEqual(result['total_rows'], 3)
        self.assertEqual(result['valid_transactions'], 0)
        self.assertEqual(result['invalid_transactions'], 3)
        self.assertGreater(len(result['errors']), 0)
        
        # Check specific error types
        error_messages = ' '.join(result['errors'])
        self.assertIn("Invalid date format", error_messages)
        self.assertIn("not found", error_messages)
        self.assertIn("Invalid transaction type", error_messages)
    
    def test_export_with_date_filtering(self):
        """Test export with date range filtering"""
        export_manager = DataExportImportManager(self.user)
        
        # Export transactions with date filter (wider range to include test transactions)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=15)  # Wider range to include test data
        
        filepath = export_manager.export_data(
            "transactions", 
            "csv", 
            start_date=start_date, 
            end_date=end_date
        )
        
        # Check filtered export
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should have fewer transactions due to date filtering
            self.assertGreater(len(rows), 0)
            
            # Verify all transactions are within date range
            for row in rows:
                tx_date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
                self.assertGreaterEqual(tx_date, start_date)
                self.assertLessEqual(tx_date, end_date)
    
    def test_export_specific_account(self):
        """Test export for specific account only"""
        export_manager = DataExportImportManager(self.user)
        
        # Export transactions for savings account only
        filepath = export_manager.export_data(
            "transactions", 
            "csv", 
            account_identifier="savings"
        )
        
        # Check account-specific export
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should only have savings account transactions
            account_types = {row['account_type'] for row in rows}
            self.assertEqual(account_types, {'savings'})
            
            # Should have the expected number of savings transactions
            self.assertEqual(len(rows), 3)  # 3 transactions in savings account


if __name__ == '__main__':
    unittest.main()