"""
Unit tests for Data Export/Import System
"""

import unittest
import os
import tempfile
import shutil
import json
import csv
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.core.user import User
from src.core.account import Account
from src.core.transaction import Transaction
from src.managers.transfer_manager import TransferTransaction
from src.utils.data_export_import import DataExporter, DataImporter, DataExportImportManager


class TestDataExporter(unittest.TestCase):
    
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
        
        self.exporter = DataExporter(self.user)
        
        # Create temporary directory for file tests
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_export_transactions_csv_all_accounts(self):
        """Test exporting all transactions to CSV"""
        filepath = self.exporter.export_transactions_csv()
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.csv'))
        
        # Check CSV content
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should have transactions from both accounts
            self.assertGreater(len(rows), 0)
            
            # Check required columns exist
            expected_columns = ['date', 'account', 'account_type', 'transaction_type', 
                              'amount', 'balance_after', 'transfer_id', 'memo', 'description']
            self.assertEqual(set(reader.fieldnames), set(expected_columns))
            
            # Check for both account types
            account_types = {row['account_type'] for row in rows}
            self.assertIn('savings', account_types)
            self.assertIn('current', account_types)
    
    def test_export_transactions_csv_specific_account(self):
        """Test exporting transactions for specific account"""
        filepath = self.exporter.export_transactions_csv("savings")
        
        # Check CSV content
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should only have savings account transactions
            account_types = {row['account_type'] for row in rows}
            self.assertEqual(account_types, {'savings'})
            
            # Check transaction types
            tx_types = {row['transaction_type'] for row in rows}
            expected_types = {'deposit', 'withdrawal', 'interest'}
            self.assertEqual(tx_types, expected_types)
    
    def test_export_transactions_csv_with_date_filter(self):
        """Test exporting transactions with date filtering"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)
        
        filepath = self.exporter.export_transactions_csv(
            start_date=start_date, end_date=end_date
        )
        
        # Check that only recent transactions are included
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            for row in rows:
                tx_date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
                self.assertGreaterEqual(tx_date, start_date)
                self.assertLessEqual(tx_date, end_date)
    
    def test_export_transactions_csv_invalid_account(self):
        """Test error handling for invalid account"""
        with self.assertRaises(ValueError) as context:
            self.exporter.export_transactions_csv("invalid_account")
        
        self.assertIn("Account 'invalid_account' not found", str(context.exception))
    
    def test_export_accounts_json(self):
        """Test exporting account data to JSON"""
        filepath = self.exporter.export_accounts_json()
        
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
            
            # Check account details
            account_types = {acc['account_type'] for acc in accounts}
            self.assertEqual(account_types, {'savings', 'current'})
            
            # Check transactions are included
            for account in accounts:
                self.assertIn('transactions', account)
                self.assertIsInstance(account['transactions'], list)
    
    def test_export_full_backup(self):
        """Test exporting full backup"""
        filepath = self.exporter.export_full_backup()
        
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
            
            # Check backup info
            backup_info = data['backup_info']
            self.assertEqual(backup_info['username'], 'testuser')
            self.assertEqual(backup_info['version'], '1.0')
            
            # Check user data includes password hash
            user_data = data['user_data']
            self.assertIn('password_hash', user_data)
            self.assertIn('accounts', user_data)
    
    def test_custom_filename(self):
        """Test exporting with custom filename"""
        custom_filename = "my_custom_export.csv"
        filepath = self.exporter.export_transactions_csv(filename=custom_filename)
        
        self.assertTrue(filepath.endswith(custom_filename))
        self.assertTrue(os.path.exists(filepath))


class TestDataImporter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test account for import validation
        self.test_account = Account("savings", 500.0, 0, "Test Account")
        self.user.accounts = [self.test_account]
        
        self.importer = DataImporter(self.user)
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_import_transactions_csv_valid(self):
        """Test importing valid transaction CSV"""
        # Create test CSV file
        csv_content = """date,account,account_type,transaction_type,amount,memo
2024-01-01 10:00:00,Test Account,savings,deposit,100.0,Test deposit
2024-01-02 11:00:00,Test Account,savings,withdrawal,50.0,Test withdrawal"""
        
        csv_file = "test_transactions.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Import transactions
        result = self.importer.import_transactions_csv(csv_file)
        
        # Check results
        self.assertEqual(result['total_rows'], 2)
        self.assertEqual(result['valid_transactions'], 2)
        self.assertEqual(result['invalid_transactions'], 0)
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['imported_transactions']), 2)
        
        # Check transactions were added to account
        self.assertEqual(len(self.test_account.transactions), 2)
    
    def test_import_transactions_csv_validation_only(self):
        """Test CSV validation without importing"""
        # Create test CSV file
        csv_content = """date,account,account_type,transaction_type,amount
2024-01-01 10:00:00,Test Account,savings,deposit,100.0"""
        
        csv_file = "test_transactions.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Validate only
        result = self.importer.import_transactions_csv(csv_file, validate_only=True)
        
        # Check results
        self.assertEqual(result['valid_transactions'], 1)
        self.assertTrue(result['validation_only'])
        self.assertEqual(len(result['imported_transactions']), 0)
        
        # Check no transactions were added
        self.assertEqual(len(self.test_account.transactions), 0)
    
    def test_import_transactions_csv_invalid_data(self):
        """Test importing CSV with invalid data"""
        # Create CSV with invalid data
        csv_content = """date,account,account_type,transaction_type,amount
invalid_date,Test Account,savings,deposit,100.0
2024-01-01 10:00:00,NonExistent,savings,deposit,50.0
2024-01-01 10:00:00,Test Account,savings,invalid_type,25.0
2024-01-01 10:00:00,Test Account,savings,deposit,invalid_amount"""
        
        csv_file = "test_invalid.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        # Import transactions
        result = self.importer.import_transactions_csv(csv_file)
        
        # Check results
        self.assertEqual(result['total_rows'], 4)
        self.assertEqual(result['valid_transactions'], 0)
        self.assertEqual(result['invalid_transactions'], 4)
        self.assertGreater(len(result['errors']), 0)
    
    def test_import_transactions_csv_missing_file(self):
        """Test error handling for missing file"""
        with self.assertRaises(FileNotFoundError):
            self.importer.import_transactions_csv("nonexistent.csv")
    
    def test_import_accounts_json_valid(self):
        """Test importing valid account JSON"""
        # Create test JSON file
        json_data = {
            "accounts": [
                {
                    "account_type": "current",
                    "nickname": "New Account",
                    "balance": 1000.0,
                    "overdraft_limit": 500.0
                }
            ]
        }
        
        json_file = "test_accounts.json"
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        # Import accounts
        result = self.importer.import_accounts_json(json_file)
        
        # Check results
        self.assertEqual(result['total_accounts'], 1)
        self.assertEqual(result['valid_accounts'], 1)
        self.assertEqual(result['invalid_accounts'], 0)
        self.assertEqual(len(result['errors']), 0)
        
        # Check account was added
        self.assertEqual(len(self.user.accounts), 2)  # Original + imported
        new_account = self.user.get_account("current")
        self.assertIsNotNone(new_account)
        self.assertEqual(new_account.nickname, "New Account")
    
    def test_import_accounts_json_duplicate_type(self):
        """Test importing account with duplicate type"""
        # Create JSON with duplicate account type
        json_data = {
            "accounts": [
                {
                    "account_type": "savings",  # Already exists
                    "balance": 1000.0
                }
            ]
        }
        
        json_file = "test_duplicate.json"
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        # Import accounts
        result = self.importer.import_accounts_json(json_file)
        
        # Check results
        self.assertEqual(result['valid_accounts'], 0)
        self.assertEqual(result['invalid_accounts'], 1)
        self.assertGreater(len(result['errors']), 0)
        
        # Check error message
        error_messages = ' '.join(result['errors'])
        self.assertIn("already exists", error_messages)
    
    def test_import_accounts_json_invalid_structure(self):
        """Test importing JSON with invalid structure"""
        # Create JSON without accounts key
        json_data = {"invalid": "structure"}
        
        json_file = "test_invalid_structure.json"
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        # Import accounts
        result = self.importer.import_accounts_json(json_file)
        
        # Check results
        self.assertGreater(len(result['errors']), 0)
        error_messages = ' '.join(result['errors'])
        self.assertIn("'accounts' key not found", error_messages)
    
    def test_import_accounts_json_invalid_json(self):
        """Test importing invalid JSON file"""
        # Create invalid JSON file
        json_file = "test_invalid.json"
        with open(json_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Import accounts
        result = self.importer.import_accounts_json(json_file)
        
        # Check results
        self.assertGreater(len(result['errors']), 0)
        error_messages = ' '.join(result['errors'])
        self.assertIn("Invalid JSON format", error_messages)


class TestDataExportImportManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        self.manager = DataExportImportManager(self.user)
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_export_data_transactions_csv(self):
        """Test exporting transactions via manager"""
        # Add test account and transaction
        account = Account("savings", 1000.0)
        account.transactions = [Transaction(100.0, "deposit")]
        self.user.accounts = [account]
        
        filepath = self.manager.export_data("transactions", "csv")
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.csv'))
    
    def test_export_data_accounts_json(self):
        """Test exporting accounts via manager"""
        # Add test account
        account = Account("savings", 1000.0)
        self.user.accounts = [account]
        
        filepath = self.manager.export_data("accounts", "json")
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.json'))
    
    def test_export_data_full_backup(self):
        """Test exporting full backup via manager"""
        # Add test account
        account = Account("savings", 1000.0)
        self.user.accounts = [account]
        
        filepath = self.manager.export_data("full_backup", "json")
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue('backups' in filepath)
    
    def test_export_data_unsupported_type(self):
        """Test error handling for unsupported data type"""
        with self.assertRaises(ValueError) as context:
            self.manager.export_data("invalid_type", "csv")
        
        self.assertIn("Unsupported data type", str(context.exception))
    
    def test_export_data_unsupported_format(self):
        """Test error handling for unsupported format"""
        with self.assertRaises(ValueError) as context:
            self.manager.export_data("transactions", "xml")
        
        self.assertIn("Unsupported format", str(context.exception))
    
    def test_import_data_transactions(self):
        """Test importing transactions via manager"""
        # Create test account
        account = Account("savings", 500.0)
        self.user.accounts = [account]
        
        # Create test CSV
        csv_content = """date,account,account_type,transaction_type,amount
2024-01-01 10:00:00,savings,savings,deposit,100.0"""
        
        csv_file = "test.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        result = self.manager.import_data("transactions", csv_file)
        
        self.assertEqual(result['valid_transactions'], 1)
        self.assertEqual(result['invalid_transactions'], 0)
    
    def test_import_data_unsupported_type(self):
        """Test error handling for unsupported import type"""
        with self.assertRaises(ValueError) as context:
            self.manager.import_data("invalid_type", "test.csv")
        
        self.assertIn("Unsupported import data type", str(context.exception))
    
    def test_get_export_formats(self):
        """Test getting supported export formats"""
        tx_formats = self.manager.get_export_formats("transactions")
        self.assertEqual(tx_formats, ['csv'])
        
        acc_formats = self.manager.get_export_formats("accounts")
        self.assertEqual(acc_formats, ['json'])
        
        backup_formats = self.manager.get_export_formats("full_backup")
        self.assertEqual(backup_formats, ['json'])
        
        invalid_formats = self.manager.get_export_formats("invalid")
        self.assertEqual(invalid_formats, [])
    
    def test_get_import_formats(self):
        """Test getting supported import formats"""
        tx_formats = self.manager.get_import_formats("transactions")
        self.assertEqual(tx_formats, ['csv'])
        
        acc_formats = self.manager.get_import_formats("accounts")
        self.assertEqual(acc_formats, ['json'])
        
        invalid_formats = self.manager.get_import_formats("invalid")
        self.assertEqual(invalid_formats, [])


if __name__ == '__main__':
    unittest.main()