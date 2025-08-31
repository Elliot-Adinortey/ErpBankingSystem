import unittest
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timedelta
import argparse
import io
import sys
from main import transaction_history, transaction_summary, parse_date_string, display_transaction_history


class TestTransactionHistoryCLI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock user with transaction history
        self.mock_user = Mock()
        
        # Sample transaction data
        base_date = datetime(2024, 1, 1, 10, 0, 0)
        self.sample_transactions = [
            {
                'date': base_date,
                'account': 'savings',
                'account_type': 'savings',
                'type': 'deposit',
                'amount': 1000.0
            },
            {
                'date': base_date + timedelta(days=1),
                'account': 'current',
                'account_type': 'current',
                'type': 'withdrawal',
                'amount': -200.0
            },
            {
                'date': base_date + timedelta(days=2),
                'account': 'savings',
                'account_type': 'savings',
                'type': 'transfer',
                'amount': 500.0
            }
        ]
        
        self.sample_result = {
            'transactions': self.sample_transactions,
            'total_count': 3,
            'page': 1,
            'page_size': 20,
            'total_pages': 1,
            'has_next': False,
            'has_previous': False
        }
        
        self.mock_user.get_transaction_history.return_value = self.sample_result
        self.mock_user.filter_transactions.return_value = self.sample_transactions
        
        # Mock summary data
        self.sample_summary = {
            'total_transactions': 3,
            'total_deposits': 1000.0,
            'total_withdrawals': 200.0,
            'total_transfers_in': 500.0,
            'total_transfers_out': 0.0,
            'net_change': 1300.0,
            'date_range': {
                'start': base_date,
                'end': base_date + timedelta(days=2)
            }
        }
        
        self.mock_user.get_transaction_summary.return_value = self.sample_summary
        self.mock_user.get_account.return_value = Mock(get_display_name=Mock(return_value='Test Account'))
    
    def create_mock_args(self, **kwargs):
        """Create mock args object with default values"""
        defaults = {
            'account': None,
            'start_date': None,
            'end_date': None,
            'type': None,
            'min_amount': None,
            'max_amount': None,
            'page': 1,
            'page_size': 20,
            'sort_by': 'date',
            'export_format': None,
            'token': 'test_token'
        }
        defaults.update(kwargs)
        
        args = Mock()
        for key, value in defaults.items():
            setattr(args, key, value)
        
        return args
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_basic(self, mock_stdout, mock_auth):
        """Test basic transaction history display"""
        mock_auth.return_value = self.mock_user
        args = self.create_mock_args()
        
        transaction_history(args)
        
        output = mock_stdout.getvalue()
        self.assertIn('Transaction History', output)
        self.assertIn('Total transactions: 3', output)
        self.assertIn('deposit', output)
        self.assertIn('withdrawal', output)
        self.assertIn('transfer', output)
        self.assertIn('1000.00', output)
        self.assertIn('-200.00', output)
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_with_account_filter(self, mock_stdout, mock_auth):
        """Test transaction history with account filter"""
        mock_auth.return_value = self.mock_user
        args = self.create_mock_args(account='savings')
        
        transaction_history(args)
        
        # Verify get_transaction_history was called with correct parameters
        self.mock_user.get_transaction_history.assert_called_with(
            account='savings',
            start_date=None,
            end_date=None,
            page=1,
            page_size=20
        )
    
    @patch('main.authenticate_user')
    @patch('main.parse_date_string')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_with_date_filter(self, mock_stdout, mock_parse_date, mock_auth):
        """Test transaction history with date filtering"""
        mock_auth.return_value = self.mock_user
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        mock_parse_date.side_effect = [start_date, end_date]
        
        args = self.create_mock_args(start_date='2024-01-01', end_date='2024-01-31')
        
        transaction_history(args)
        
        # Verify dates were parsed
        self.assertEqual(mock_parse_date.call_count, 2)
        
        # Verify get_transaction_history was called with dates
        self.mock_user.get_transaction_history.assert_called_with(
            account=None,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=20
        )
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_with_type_filter(self, mock_stdout, mock_auth):
        """Test transaction history with transaction type filter"""
        mock_auth.return_value = self.mock_user
        args = self.create_mock_args(type=['deposit', 'withdrawal'])
        
        transaction_history(args)
        
        # Verify filter_transactions was called with correct filters
        expected_filters = {'transaction_types': ['deposit', 'withdrawal']}
        self.mock_user.filter_transactions.assert_called_with(
            self.sample_transactions, expected_filters
        )
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_with_amount_filter(self, mock_stdout, mock_auth):
        """Test transaction history with amount range filter"""
        mock_auth.return_value = self.mock_user
        args = self.create_mock_args(min_amount=100.0, max_amount=1000.0)
        
        transaction_history(args)
        
        # Verify filter_transactions was called with amount filters
        expected_filters = {'min_amount': 100.0, 'max_amount': 1000.0}
        self.mock_user.filter_transactions.assert_called_with(
            self.sample_transactions, expected_filters
        )
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_no_transactions(self, mock_stdout, mock_auth):
        """Test transaction history when no transactions found"""
        mock_auth.return_value = self.mock_user
        
        # Mock empty result
        empty_result = {
            'transactions': [],
            'total_count': 0,
            'page': 1,
            'page_size': 20,
            'total_pages': 0,
            'has_next': False,
            'has_previous': False
        }
        self.mock_user.get_transaction_history.return_value = empty_result
        
        args = self.create_mock_args()
        
        transaction_history(args)
        
        output = mock_stdout.getvalue()
        self.assertIn('No transactions found', output)
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_error(self, mock_stdout, mock_auth):
        """Test transaction history with error response"""
        mock_auth.return_value = self.mock_user
        
        # Mock error result
        error_result = {
            'transactions': [],
            'total_count': 0,
            'error': 'Account not found'
        }
        self.mock_user.get_transaction_history.return_value = error_result
        
        args = self.create_mock_args(account='nonexistent')
        
        transaction_history(args)
        
        output = mock_stdout.getvalue()
        self.assertIn('Error: Account not found', output)
    
    @patch('main.authenticate_user')
    @patch('builtins.open', new_callable=mock_open)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_export_csv(self, mock_stdout, mock_file, mock_auth):
        """Test transaction history CSV export"""
        mock_auth.return_value = self.mock_user
        args = self.create_mock_args(export_format='csv')
        
        transaction_history(args)
        
        # Verify file was opened for writing
        mock_file.assert_called_once()
        
        # Verify export message
        output = mock_stdout.getvalue()
        self.assertIn('Transactions exported to', output)
        self.assertIn('.csv', output)
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_summary_basic(self, mock_stdout, mock_auth):
        """Test basic transaction summary display"""
        mock_auth.return_value = self.mock_user
        args = self.create_mock_args()
        
        transaction_summary(args)
        
        output = mock_stdout.getvalue()
        self.assertIn('Transaction Summary', output)
        self.assertIn('Total Transactions: 3', output)
        self.assertIn('Total Deposits: $1000.00', output)
        self.assertIn('Total Withdrawals: $200.00', output)
        self.assertIn('Net Change: $1300.00', output)
    
    @patch('main.authenticate_user')
    @patch('main.parse_date_string')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_summary_with_dates(self, mock_stdout, mock_parse_date, mock_auth):
        """Test transaction summary with date filtering"""
        mock_auth.return_value = self.mock_user
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        mock_parse_date.side_effect = [start_date, end_date]
        
        args = self.create_mock_args(start_date='2024-01-01', end_date='2024-01-31')
        
        transaction_summary(args)
        
        # Verify get_transaction_summary was called with dates
        self.mock_user.get_transaction_summary.assert_called_with(
            account=None,
            start_date=start_date,
            end_date=end_date
        )
        
        output = mock_stdout.getvalue()
        self.assertIn('Period: 2024-01-01 to 2024-01-03', output)
    
    def test_parse_date_string_various_formats(self):
        """Test parsing various date string formats"""
        # Test YYYY-MM-DD format
        result = parse_date_string('2024-01-15')
        expected = datetime(2024, 1, 15)
        self.assertEqual(result, expected)
        
        # Test YYYY-MM-DD HH:MM format
        result = parse_date_string('2024-01-15 14:30')
        expected = datetime(2024, 1, 15, 14, 30)
        self.assertEqual(result, expected)
        
        # Test YYYY-MM-DD HH:MM:SS format
        result = parse_date_string('2024-01-15 14:30:45')
        expected = datetime(2024, 1, 15, 14, 30, 45)
        self.assertEqual(result, expected)
    
    def test_parse_date_string_invalid_format(self):
        """Test parsing invalid date string"""
        with self.assertRaises(ValueError) as context:
            parse_date_string('invalid-date')
        
        self.assertIn('Unable to parse date', str(context.exception))
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_display_transaction_history_sorting(self, mock_stdout):
        """Test transaction history display with different sorting"""
        transactions = self.sample_transactions.copy()
        result_info = self.sample_result.copy()
        
        # Test sorting by amount
        display_transaction_history(transactions, result_info, sort_by='amount')
        
        output = mock_stdout.getvalue()
        self.assertIn('Transaction History', output)
        
        # Reset stdout for next test
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        # Test sorting by type
        display_transaction_history(transactions, result_info, sort_by='type')
        
        output = mock_stdout.getvalue()
        self.assertIn('Transaction History', output)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_display_transaction_history_pagination(self, mock_stdout):
        """Test transaction history display with pagination"""
        transactions = self.sample_transactions.copy()
        result_info = {
            'transactions': transactions,
            'total_count': 50,
            'page': 2,
            'page_size': 20,
            'total_pages': 3,
            'has_next': True,
            'has_previous': True
        }
        
        display_transaction_history(transactions, result_info)
        
        output = mock_stdout.getvalue()
        self.assertIn('Page 2 of 3', output)
        self.assertIn('Previous: --page 1', output)
        self.assertIn('Next: --page 3', output)
    
    @patch('main.authenticate_user')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_invalid_date_format(self, mock_stdout, mock_auth):
        """Test transaction history with invalid date format"""
        mock_auth.return_value = self.mock_user
        args = self.create_mock_args(start_date='invalid-date')
        
        transaction_history(args)
        
        output = mock_stdout.getvalue()
        self.assertIn('Error: Invalid start date format', output)
    
    @patch('main.authenticate_user')
    @patch('main.parse_date_string')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_transaction_history_invalid_date_range(self, mock_stdout, mock_parse_date, mock_auth):
        """Test transaction history with invalid date range (start > end)"""
        mock_auth.return_value = self.mock_user
        
        start_date = datetime(2024, 1, 31)
        end_date = datetime(2024, 1, 1)
        mock_parse_date.side_effect = [start_date, end_date]
        
        args = self.create_mock_args(start_date='2024-01-31', end_date='2024-01-01')
        
        transaction_history(args)
        
        output = mock_stdout.getvalue()
        self.assertIn('Error: Start date cannot be after end date', output)
    
    @patch('main.authenticate_user')
    def test_transaction_history_no_authentication(self, mock_auth):
        """Test transaction history without authentication"""
        mock_auth.return_value = None
        args = self.create_mock_args()
        
        # Should return early without error
        transaction_history(args)
        
        # Verify user methods were not called
        self.mock_user.get_transaction_history.assert_not_called()


if __name__ == '__main__':
    unittest.main()