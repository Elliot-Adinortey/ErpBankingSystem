"""
Unit tests for StatementGenerator class
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import os
import tempfile
import shutil

from src.core.user import User
from src.core.account import Account
from src.core.transaction import Transaction
from src.managers.transfer_manager import TransferTransaction
from src.utils.statement_generator import StatementGenerator


class TestStatementGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create test accounts
        self.savings_account = Account("savings", 1000.0, 0, "My Savings")
        self.current_account = Account("current", 500.0, 200.0, "Daily Account")
        
        self.user.accounts = [self.savings_account, self.current_account]
        
        # Create test transactions
        base_date = datetime.now() - timedelta(days=15)
        
        # Savings account transactions
        self.savings_account.transactions = [
            Transaction(100.0, "deposit", base_date - timedelta(days=10)),
            Transaction(50.0, "withdrawal", base_date - timedelta(days=5)),
            Transaction(25.0, "interest", base_date - timedelta(days=2))
        ]
        
        # Current account transactions
        transfer_tx = TransferTransaction(200.0, "savings", "current", "Test transfer")
        transfer_tx.is_outgoing = False
        transfer_tx.date = base_date - timedelta(days=3)
        
        self.current_account.transactions = [
            Transaction(300.0, "deposit", base_date - timedelta(days=8)),
            Transaction(150.0, "withdrawal", base_date - timedelta(days=6)),
            transfer_tx
        ]
        
        self.statement_generator = StatementGenerator(self.user)
        
        # Create temporary directory for file tests
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_generate_statement_basic(self):
        """Test basic statement generation"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("savings", start_date, end_date)
        
        self.assertIn('account', result)
        self.assertIn('statement_data', result)
        self.assertIn('formatted_content', result)
        self.assertEqual(result['format'], 'text')
        self.assertEqual(result['account'], self.savings_account)
    
    def test_generate_statement_invalid_account(self):
        """Test statement generation with invalid account"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        with self.assertRaises(ValueError) as context:
            self.statement_generator.generate_statement("invalid", start_date, end_date)
        
        self.assertIn("Account 'invalid' not found", str(context.exception))
    
    def test_generate_statement_with_nickname(self):
        """Test statement generation using account nickname"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("My Savings", start_date, end_date)
        
        self.assertEqual(result['account'], self.savings_account)
        self.assertIn('My Savings', result['formatted_content'])
    
    def test_statement_data_calculation(self):
        """Test statement data calculation accuracy"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("savings", start_date, end_date)
        statement_data = result['statement_data']
        
        # Check account info
        account_info = statement_data['account_info']
        self.assertEqual(account_info['type'], 'savings')
        self.assertEqual(account_info['nickname'], 'My Savings')
        self.assertEqual(account_info['display_name'], 'My Savings (savings)')
        
        # Check balances
        balances = statement_data['balances']
        self.assertEqual(balances['closing_balance'], 1000.0)
        self.assertIsInstance(balances['opening_balance'], float)
        
        # Check transaction summary
        summary = statement_data['transaction_summary']
        self.assertEqual(summary['total_transactions'], 3)
        self.assertEqual(summary['total_deposits'], 100.0)
        self.assertEqual(summary['total_withdrawals'], 50.0)
        self.assertEqual(summary['total_interest'], 25.0)
    
    def test_opening_balance_calculation(self):
        """Test opening balance calculation"""
        # Create account with known transactions
        account = Account("test", 1000.0)
        account.transactions = [
            Transaction(200.0, "deposit", datetime.now() - timedelta(days=5)),
            Transaction(100.0, "withdrawal", datetime.now() - timedelta(days=3))
        ]
        
        # Opening balance should be current balance minus net transactions
        # 1000 - 200 + 100 = 900
        opening_balance = self.statement_generator._calculate_opening_balance(
            account, account.transactions, datetime.now() - timedelta(days=10)
        )
        
        self.assertEqual(opening_balance, 900.0)
    
    def test_text_statement_format(self):
        """Test text statement formatting"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("savings", start_date, end_date, "text")
        content = result['formatted_content']
        
        # Check for required sections
        self.assertIn("ACCOUNT STATEMENT", content)
        self.assertIn("ACCOUNT INFORMATION", content)
        self.assertIn("ACCOUNT HOLDER", content)
        self.assertIn("STATEMENT PERIOD", content)
        self.assertIn("BALANCE SUMMARY", content)
        self.assertIn("TRANSACTION SUMMARY", content)
        self.assertIn("TRANSACTION DETAILS", content)
        
        # Check for account details
        self.assertIn("My Savings (savings)", content)
        self.assertIn("testuser", content)
        self.assertIn("test@example.com", content)
    
    def test_pdf_statement_format(self):
        """Test PDF statement formatting (HTML markup)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("savings", start_date, end_date, "pdf")
        content = result['formatted_content']
        
        # Check for HTML structure
        self.assertIn("<html>", content)
        self.assertIn("<h1>Account Statement</h1>", content)
        self.assertIn("<table border='1'>", content)
        self.assertIn("</html>", content)
        
        # Check for account details
        self.assertIn("My Savings (savings)", content)
        self.assertIn("testuser", content)
    
    def test_unsupported_format(self):
        """Test error handling for unsupported format"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        with self.assertRaises(ValueError) as context:
            self.statement_generator.generate_statement("savings", start_date, end_date, "xml")
        
        self.assertIn("Unsupported format: xml", str(context.exception))
    
    def test_default_date_range(self):
        """Test default date range (30 days)"""
        result = self.statement_generator.generate_statement("savings")
        
        period = result['statement_data']['period']
        date_diff = period['end_date'] - period['start_date']
        
        # Should be approximately 30 days
        self.assertAlmostEqual(date_diff.days, 30, delta=1)
    
    def test_export_statement_to_file(self):
        """Test exporting statement to file"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("savings", start_date, end_date)
        filepath = self.statement_generator.export_statement_to_file(result)
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.txt'))
        
        # Check file content
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn("ACCOUNT STATEMENT", content)
            self.assertIn("My Savings", content)
    
    def test_export_statement_custom_filename(self):
        """Test exporting statement with custom filename"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("savings", start_date, end_date)
        custom_filename = "custom_statement.txt"
        filepath = self.statement_generator.export_statement_to_file(result, custom_filename)
        
        self.assertTrue(filepath.endswith(custom_filename))
        self.assertTrue(os.path.exists(filepath))
    
    def test_generate_multi_account_statement(self):
        """Test consolidated multi-account statement generation"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_multi_account_statement(start_date, end_date)
        
        self.assertIn('consolidated_data', result)
        self.assertIn('formatted_content', result)
        
        consolidated_data = result['consolidated_data']
        self.assertEqual(consolidated_data['summary']['total_accounts'], 2)
        self.assertGreater(consolidated_data['summary']['total_closing_balance'], 0)
    
    def test_multi_account_statement_no_accounts(self):
        """Test multi-account statement with no accounts"""
        empty_user = User("empty", "TestPass123", "empty@example.com")
        empty_generator = StatementGenerator(empty_user)
        
        with self.assertRaises(ValueError) as context:
            empty_generator.generate_multi_account_statement()
        
        self.assertIn("No accounts found for user", str(context.exception))
    
    def test_consolidated_text_format(self):
        """Test consolidated statement text formatting"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_multi_account_statement(start_date, end_date, "text")
        content = result['formatted_content']
        
        # Check for consolidated sections
        self.assertIn("CONSOLIDATED ACCOUNT STATEMENT", content)
        self.assertIn("CONSOLIDATED SUMMARY", content)
        self.assertIn("ACCOUNT BREAKDOWN", content)
        
        # Check for both accounts
        self.assertIn("My Savings", content)
        self.assertIn("Daily Account", content)
    
    def test_transaction_filtering_by_period(self):
        """Test transaction filtering by date period"""
        # Create account with transactions outside the period
        account = Account("test", 1000.0)
        old_transaction = Transaction(100.0, "deposit", datetime.now() - timedelta(days=45))
        recent_transaction = Transaction(50.0, "withdrawal", datetime.now() - timedelta(days=5))
        account.transactions = [old_transaction, recent_transaction]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        filtered_transactions = self.statement_generator._get_transactions_for_period(
            account, start_date, end_date
        )
        
        # Should only include the recent transaction
        self.assertEqual(len(filtered_transactions), 1)
        self.assertEqual(filtered_transactions[0], recent_transaction)
    
    def test_transfer_transaction_handling(self):
        """Test proper handling of transfer transactions in statements"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = self.statement_generator.generate_statement("current", start_date, end_date)
        statement_data = result['statement_data']
        
        # Check transfer amounts are calculated correctly
        summary = statement_data['transaction_summary']
        self.assertEqual(summary['transfer_in'], 200.0)  # Transfer into current account
        self.assertEqual(summary['transfer_out'], 0.0)   # No transfers out from current account


if __name__ == '__main__':
    unittest.main()