import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from transaction_manager import TransactionManager
from transaction import Transaction
from account import Account
from user import User


class TestTransactionManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock user with accounts and transactions
        self.user = Mock()
        self.user.accounts = []
        
        # Create test accounts
        self.savings_account = Mock()
        self.savings_account.account_type = 'savings'
        self.savings_account.nickname = 'My Savings'
        self.savings_account.get_display_name.return_value = 'My Savings (savings)'
        
        self.current_account = Mock()
        self.current_account.account_type = 'current'
        self.current_account.nickname = None
        self.current_account.get_display_name.return_value = 'current'
        
        # Create test transactions
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        
        self.savings_transactions = [
            Transaction(1000.0, 'deposit', base_date),
            Transaction(-200.0, 'withdrawal', base_date + timedelta(days=1)),
            Transaction(500.0, 'transfer', base_date + timedelta(days=2)),
        ]
        
        self.current_transactions = [
            Transaction(2000.0, 'deposit', base_date + timedelta(days=3)),
            Transaction(-100.0, 'withdrawal', base_date + timedelta(days=4)),
            Transaction(-500.0, 'transfer', base_date + timedelta(days=5)),
        ]
        
        self.savings_account.transaction_history = self.savings_transactions
        self.current_account.transaction_history = self.current_transactions
        
        self.user.accounts = [self.savings_account, self.current_account]
        
        # Mock get_account method
        def mock_get_account(account_id):
            if account_id == 'savings' or account_id == 'My Savings':
                return self.savings_account
            elif account_id == 'current':
                return self.current_account
            return None
        
        self.user.get_account = mock_get_account
        
        self.transaction_manager = TransactionManager(self.user)
    
    def test_get_transaction_history_all_accounts(self):
        """Test getting transaction history for all accounts"""
        result = self.transaction_manager.get_transaction_history()
        
        self.assertEqual(result['total_count'], 6)  # 3 + 3 transactions
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['page_size'], 50)
        self.assertEqual(result['total_pages'], 1)
        self.assertTrue(result['has_next'] is False)
        self.assertTrue(result['has_previous'] is False)
        
        # Check transactions are sorted by date (newest first)
        transactions = result['transactions']
        self.assertEqual(len(transactions), 6)
        
        # Verify first transaction is the newest
        self.assertEqual(transactions[0]['type'], 'transfer')
        self.assertEqual(transactions[0]['amount'], -500.0)
        self.assertEqual(transactions[0]['account'], 'current')
    
    def test_get_transaction_history_specific_account(self):
        """Test getting transaction history for a specific account"""
        result = self.transaction_manager.get_transaction_history(account='savings')
        
        self.assertEqual(result['total_count'], 3)
        self.assertEqual(len(result['transactions']), 3)
        
        # All transactions should be from savings account
        for transaction in result['transactions']:
            self.assertEqual(transaction['account'], 'My Savings (savings)')
    
    def test_get_transaction_history_account_not_found(self):
        """Test getting transaction history for non-existent account"""
        result = self.transaction_manager.get_transaction_history(account='nonexistent')
        
        self.assertEqual(result['total_count'], 0)
        self.assertEqual(len(result['transactions']), 0)
        self.assertIn('error', result)
        self.assertIn('not found', result['error'])
    
    def test_get_transaction_history_with_date_filtering(self):
        """Test transaction history with date range filtering"""
        base_date = datetime(2024, 1, 1)
        start_date = base_date + timedelta(days=2)
        end_date = base_date + timedelta(days=4)
        
        result = self.transaction_manager.get_transaction_history(
            start_date=start_date, 
            end_date=end_date
        )
        
        # Should include transactions from days 2, 3, and 4
        self.assertEqual(result['total_count'], 3)
        
        # Verify date filtering
        for transaction in result['transactions']:
            self.assertTrue(start_date <= transaction['date'] <= end_date + timedelta(days=1))
    
    def test_get_transaction_history_pagination(self):
        """Test transaction history pagination"""
        # Test first page with page size 2
        result = self.transaction_manager.get_transaction_history(page=1, page_size=2)
        
        self.assertEqual(result['total_count'], 6)
        self.assertEqual(len(result['transactions']), 2)
        self.assertEqual(result['page'], 1)
        self.assertEqual(result['total_pages'], 3)
        self.assertTrue(result['has_next'])
        self.assertFalse(result['has_previous'])
        
        # Test second page
        result = self.transaction_manager.get_transaction_history(page=2, page_size=2)
        
        self.assertEqual(len(result['transactions']), 2)
        self.assertEqual(result['page'], 2)
        self.assertTrue(result['has_next'])
        self.assertTrue(result['has_previous'])
        
        # Test last page
        result = self.transaction_manager.get_transaction_history(page=3, page_size=2)
        
        self.assertEqual(len(result['transactions']), 2)
        self.assertEqual(result['page'], 3)
        self.assertFalse(result['has_next'])
        self.assertTrue(result['has_previous'])
    
    def test_filter_transactions_by_type(self):
        """Test filtering transactions by transaction type"""
        all_transactions = [
            {'type': 'deposit', 'amount': 100, 'account_type': 'savings'},
            {'type': 'withdrawal', 'amount': -50, 'account_type': 'savings'},
            {'type': 'transfer', 'amount': 200, 'account_type': 'current'},
        ]
        
        filters = {'transaction_types': ['deposit', 'transfer']}
        filtered = self.transaction_manager.filter_transactions(all_transactions, filters)
        
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(t['type'] in ['deposit', 'transfer'] for t in filtered))
    
    def test_filter_transactions_by_amount_range(self):
        """Test filtering transactions by amount range"""
        all_transactions = [
            {'type': 'deposit', 'amount': 100, 'account_type': 'savings'},
            {'type': 'withdrawal', 'amount': -50, 'account_type': 'savings'},
            {'type': 'transfer', 'amount': 200, 'account_type': 'current'},
        ]
        
        filters = {'min_amount': 75, 'max_amount': 150}
        filtered = self.transaction_manager.filter_transactions(all_transactions, filters)
        
        self.assertEqual(len(filtered), 1)  # Only the 100 deposit should match
        self.assertEqual(filtered[0]['amount'], 100)
    
    def test_filter_transactions_by_account_type(self):
        """Test filtering transactions by account type"""
        all_transactions = [
            {'type': 'deposit', 'amount': 100, 'account_type': 'savings'},
            {'type': 'withdrawal', 'amount': -50, 'account_type': 'savings'},
            {'type': 'transfer', 'amount': 200, 'account_type': 'current'},
        ]
        
        filters = {'account_types': ['savings']}
        filtered = self.transaction_manager.filter_transactions(all_transactions, filters)
        
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(t['account_type'] == 'savings' for t in filtered))
    
    def test_get_transaction_summary(self):
        """Test transaction summary calculation"""
        summary = self.transaction_manager.get_transaction_summary()
        
        self.assertEqual(summary['total_transactions'], 6)
        self.assertEqual(summary['total_deposits'], 3000.0)  # 1000 + 2000
        self.assertEqual(summary['total_withdrawals'], 300.0)  # 200 + 100
        self.assertEqual(summary['total_transfers_in'], 500.0)  # Only positive transfer
        self.assertEqual(summary['total_transfers_out'], 500.0)  # Only negative transfer
        self.assertEqual(summary['net_change'], 2700.0)  # 3000 + 500 - 300 - 500
        
        # Check date range
        self.assertIsNotNone(summary['date_range'])
        self.assertIsInstance(summary['date_range']['start'], datetime)
        self.assertIsInstance(summary['date_range']['end'], datetime)
    
    def test_get_transaction_summary_empty(self):
        """Test transaction summary with no transactions"""
        # Create user with no transactions
        empty_user = Mock()
        empty_account = Mock()
        empty_account.transaction_history = []
        empty_account.get_display_name.return_value = 'empty'
        empty_user.accounts = [empty_account]
        empty_user.get_account.return_value = empty_account
        
        manager = TransactionManager(empty_user)
        summary = manager.get_transaction_summary()
        
        self.assertEqual(summary['total_transactions'], 0)
        self.assertEqual(summary['total_deposits'], 0)
        self.assertEqual(summary['total_withdrawals'], 0)
        self.assertEqual(summary['net_change'], 0)
        self.assertIsNone(summary['date_range'])
    
    def test_export_transactions_csv(self):
        """Test exporting transactions to CSV format"""
        transactions = [
            {
                'date': datetime(2024, 1, 1, 10, 0, 0),
                'account': 'savings',
                'account_type': 'savings',
                'type': 'deposit',
                'amount': 1000.0
            },
            {
                'date': datetime(2024, 1, 2, 11, 0, 0),
                'account': 'current',
                'account_type': 'current',
                'type': 'withdrawal',
                'amount': -200.0
            }
        ]
        
        csv_output = self.transaction_manager.export_transactions(transactions, 'csv')
        
        self.assertIn('Date,Account,Account Type,Transaction Type,Amount', csv_output)
        self.assertIn('2024-01-01 10:00:00,savings,savings,deposit,1000.0', csv_output)
        self.assertIn('2024-01-02 11:00:00,current,current,withdrawal,-200.0', csv_output)
    
    def test_export_transactions_json(self):
        """Test exporting transactions to JSON format"""
        transactions = [
            {
                'date': datetime(2024, 1, 1, 10, 0, 0),
                'account': 'savings',
                'account_type': 'savings',
                'type': 'deposit',
                'amount': 1000.0
            }
        ]
        
        json_output = self.transaction_manager.export_transactions(transactions, 'json')
        
        self.assertIn('"date": "2024-01-01 10:00:00"', json_output)
        self.assertIn('"account": "savings"', json_output)
        self.assertIn('"transaction_type": "deposit"', json_output)
        self.assertIn('"amount": 1000.0', json_output)
    
    def test_export_transactions_invalid_format(self):
        """Test exporting transactions with invalid format"""
        transactions = []
        
        with self.assertRaises(ValueError):
            self.transaction_manager.export_transactions(transactions, 'xml')
    
    def test_filter_by_date_range_start_only(self):
        """Test date filtering with only start date"""
        base_date = datetime(2024, 1, 1)
        transactions = [
            {'date': base_date},
            {'date': base_date + timedelta(days=1)},
            {'date': base_date + timedelta(days=2)},
        ]
        
        start_date = base_date + timedelta(days=1)
        filtered = self.transaction_manager._filter_by_date_range(transactions, start_date=start_date)
        
        self.assertEqual(len(filtered), 2)
    
    def test_filter_by_date_range_end_only(self):
        """Test date filtering with only end date"""
        base_date = datetime(2024, 1, 1)
        transactions = [
            {'date': base_date},
            {'date': base_date + timedelta(days=1)},
            {'date': base_date + timedelta(days=2)},
        ]
        
        end_date = base_date + timedelta(days=1)
        filtered = self.transaction_manager._filter_by_date_range(transactions, end_date=end_date)
        
        self.assertEqual(len(filtered), 2)  # Should include end_date (inclusive)


if __name__ == '__main__':
    unittest.main()