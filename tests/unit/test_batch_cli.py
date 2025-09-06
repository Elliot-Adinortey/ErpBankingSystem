"""
Integration tests for batch operations CLI interface
"""

import unittest
import tempfile
import os
import json
import csv
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from src.core.user import User
from src.core.account import Account
from src.managers.batch_manager import BatchManager


class TestBatchCLI(unittest.TestCase):
    """Test batch operations CLI interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.user = User("testuser", "password123", "test@example.com")
        
        # Create test accounts
        savings_account = Account("savings", 1000.0)
        current_account = Account("current", 500.0, 200.0)
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
        
        # Mock session management
        self.session_patcher = patch('main.SessionManager')
        self.mock_session_manager = self.session_patcher.start()
        self.mock_session_manager.validate_session.return_value = "testuser"
        
        # Mock users dictionary
        self.users_patcher = patch('main.users', {'testuser': self.user})
        self.users_patcher.start()
        
        # Mock audit logger
        self.audit_patcher = patch('main.get_audit_logger')
        self.mock_audit_logger = self.audit_patcher.start()
        self.mock_audit_logger.return_value = Mock()
        
        # Mock save_users_to_file
        self.save_patcher = patch('main.save_users_to_file')
        self.mock_save = self.save_patcher.start()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
        self.session_patcher.stop()
        self.users_patcher.stop()
        self.audit_patcher.stop()
        self.save_patcher.stop()
    
    def create_test_csv_file(self, operations):
        """Create a test CSV file with operations"""
        csv_file = os.path.join(self.temp_dir, "test_batch.csv")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['operation_type', 'account', 'amount', 'to_account', 'memo', 'nickname', 'overdraft_limit'])
            # Write operations
            for op in operations:
                writer.writerow(op)
        
        return csv_file
    
    def create_test_json_file(self, operations):
        """Create a test JSON file with operations"""
        json_file = os.path.join(self.temp_dir, "test_batch.json")
        
        data = {"operations": operations}
        
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return json_file
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_operations_csv_preview(self, mock_stdout, mock_get_token):
        """Test batch operations command with CSV file in preview mode"""
        mock_get_token.return_value = "test_token"
        
        # Create test CSV file
        operations = [
            ['deposit', 'savings', '100.00', '', '', '', ''],
            ['withdraw', 'current', '50.00', '', '', '', '']
        ]
        csv_file = self.create_test_csv_file(operations)
        
        # Import and test the function
        from main import batch_operations
        
        # Create mock args
        args = Mock()
        args.file = csv_file
        args.preview = True
        args.report = False
        
        # Execute function
        batch_operations(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("PREVIEW MODE", output)
        self.assertIn("Processing batch file", output)
        self.assertIn("BATCH OPERATION SUMMARY", output)
        self.assertIn("Total Operations: 2", output)
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_operations_csv_execute(self, mock_stdout, mock_get_token):
        """Test batch operations command with CSV file execution"""
        mock_get_token.return_value = "test_token"
        
        # Create test CSV file
        operations = [
            ['deposit', 'savings', '100.00', '', '', '', ''],
            ['withdraw', 'current', '50.00', '', '', '', '']
        ]
        csv_file = self.create_test_csv_file(operations)
        
        # Import and test the function
        from main import batch_operations
        
        # Create mock args
        args = Mock()
        args.file = csv_file
        args.preview = False
        args.report = False
        
        # Execute function
        batch_operations(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Processing batch file", output)
        self.assertIn("BATCH OPERATION SUMMARY", output)
        self.assertIn("Total Operations: 2", output)
        self.assertIn("Changes saved", output)
        
        # Verify account balances were updated
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        self.assertEqual(savings_account.balance, 1100.0)  # 1000 + 100
        self.assertEqual(current_account.balance, 450.0)   # 500 - 50
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_operations_json_execute(self, mock_stdout, mock_get_token):
        """Test batch operations command with JSON file execution"""
        mock_get_token.return_value = "test_token"
        
        # Create test JSON file
        operations = [
            {
                "operation_type": "deposit",
                "parameters": {
                    "account": "savings",
                    "amount": 150.0
                }
            },
            {
                "operation_type": "transfer",
                "parameters": {
                    "account": "savings",
                    "to_account": "current",
                    "amount": 200.0,
                    "memo": "Test transfer"
                }
            }
        ]
        json_file = self.create_test_json_file(operations)
        
        # Import and test the function
        from main import batch_operations
        
        # Create mock args
        args = Mock()
        args.file = json_file
        args.preview = False
        args.report = False
        
        # Execute function
        batch_operations(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Processing batch file", output)
        self.assertIn("BATCH OPERATION SUMMARY", output)
        self.assertIn("Total Operations: 2", output)
        
        # Verify account balances were updated
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        self.assertEqual(savings_account.balance, 950.0)   # 1000 + 150 - 200
        self.assertEqual(current_account.balance, 700.0)   # 500 + 200
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_operations_with_errors(self, mock_stdout, mock_get_token):
        """Test batch operations command with some failed operations"""
        mock_get_token.return_value = "test_token"
        
        # Create test CSV file with some invalid operations
        operations = [
            ['deposit', 'savings', '100.00', '', '', '', ''],
            ['withdraw', 'nonexistent', '50.00', '', '', '', ''],  # Invalid account
            ['deposit', 'current', '75.00', '', '', '', '']
        ]
        csv_file = self.create_test_csv_file(operations)
        
        # Import and test the function
        from main import batch_operations
        
        # Create mock args
        args = Mock()
        args.file = csv_file
        args.preview = False
        args.report = False
        
        # Execute function
        batch_operations(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Processing batch file", output)
        self.assertIn("BATCH OPERATION SUMMARY", output)
        self.assertIn("Total Operations: 3", output)
        self.assertIn("Successful: 2", output)
        self.assertIn("Failed: 1", output)
        self.assertIn("Failed Operations", output)
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_operations_file_not_found(self, mock_stdout, mock_get_token):
        """Test batch operations command with non-existent file"""
        mock_get_token.return_value = "test_token"
        
        # Import and test the function
        from main import batch_operations
        
        # Create mock args with non-existent file
        args = Mock()
        args.file = "nonexistent_file.csv"
        args.preview = False
        args.report = False
        
        # Execute function
        batch_operations(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Batch file not found", output)
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_template_csv(self, mock_stdout, mock_get_token):
        """Test batch template command for CSV format"""
        mock_get_token.return_value = "test_token"
        
        # Import and test the function
        from main import batch_template
        
        # Create mock args
        template_file = os.path.join(self.temp_dir, "template.csv")
        args = Mock()
        args.filename = template_file
        args.format = 'csv'
        
        # Execute function
        batch_template(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("CSV template created", output)
        self.assertIn("Template Usage", output)
        self.assertIn("CSV Format Tips", output)
        
        # Verify template file was created
        self.assertTrue(os.path.exists(template_file))
        
        # Check template content
        with open(template_file, 'r') as f:
            content = f.read()
            self.assertIn("operation_type,account,amount", content)
            self.assertIn("deposit,savings,100.00", content)
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_template_json(self, mock_stdout, mock_get_token):
        """Test batch template command for JSON format"""
        mock_get_token.return_value = "test_token"
        
        # Import and test the function
        from main import batch_template
        
        # Create mock args
        template_file = os.path.join(self.temp_dir, "template.json")
        args = Mock()
        args.filename = template_file
        args.format = 'json'
        
        # Execute function
        batch_template(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("JSON template created", output)
        self.assertIn("Template Usage", output)
        self.assertIn("JSON Format Tips", output)
        
        # Verify template file was created
        self.assertTrue(os.path.exists(template_file))
        
        # Check template content
        with open(template_file, 'r') as f:
            data = json.load(f)
            self.assertIn("operations", data)
            self.assertEqual(data["operations"][0]["operation_type"], "deposit")
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_status(self, mock_stdout, mock_get_token):
        """Test batch status command"""
        mock_get_token.return_value = "test_token"
        
        # Mock recent batch operations
        mock_recent_batches = [
            {
                'timestamp': '2024-01-15 10:30:00',
                'details': {
                    'file_path': 'test_batch.csv',
                    'preview_mode': False,
                    'total_operations': 5,
                    'success_rate': 100.0
                },
                'success': True
            },
            {
                'timestamp': '2024-01-15 09:15:00',
                'details': {
                    'file_path': 'another_batch.json',
                    'preview_mode': True,
                    'total_operations': 3,
                    'success_rate': 66.7
                },
                'success': False
            }
        ]
        
        # Mock the audit logger's get_recent_operations method
        mock_audit_instance = Mock()
        mock_audit_instance.get_recent_operations.return_value = mock_recent_batches
        self.mock_audit_logger.return_value = mock_audit_instance
        
        # Import and test the function
        from main import batch_status
        
        # Create mock args
        args = Mock()
        args.hours = 24
        args.limit = 10
        
        # Execute function
        batch_status(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("BATCH OPERATION HISTORY", output)
        self.assertIn("test_batch.csv", output)
        self.assertIn("another_batch.json", output)
        self.assertIn("Execute", output)
        self.assertIn("Preview", output)
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_status_no_history(self, mock_stdout, mock_get_token):
        """Test batch status command with no history"""
        mock_get_token.return_value = "test_token"
        
        # Mock empty recent batch operations
        mock_audit_instance = Mock()
        mock_audit_instance.get_recent_operations.return_value = []
        self.mock_audit_logger.return_value = mock_audit_instance
        
        # Import and test the function
        from main import batch_status
        
        # Create mock args
        args = Mock()
        args.hours = 24
        args.limit = 10
        
        # Execute function
        batch_status(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("No batch operations found", output)
    
    @patch('main.get_session_token')
    @patch('sys.stdout', new_callable=StringIO)
    def test_batch_operations_with_report(self, mock_stdout, mock_get_token):
        """Test batch operations command with detailed report generation"""
        mock_get_token.return_value = "test_token"
        
        # Create test CSV file
        operations = [
            ['deposit', 'savings', '100.00', '', '', '', ''],
            ['withdraw', 'current', '50.00', '', '', '', '']
        ]
        csv_file = self.create_test_csv_file(operations)
        
        # Import and test the function
        from main import batch_operations
        
        # Create mock args
        args = Mock()
        args.file = csv_file
        args.preview = False
        args.report = True
        
        # Execute function
        batch_operations(args)
        
        # Check output
        output = mock_stdout.getvalue()
        self.assertIn("Processing batch file", output)
        self.assertIn("Detailed report saved to", output)
        
        # Check if report file was created
        report_files = [f for f in os.listdir('.') if f.startswith('batch_report_') and f.endswith('.txt')]
        self.assertTrue(len(report_files) > 0)
        
        # Clean up report file
        for report_file in report_files:
            if os.path.exists(report_file):
                os.remove(report_file)
    
    def test_authentication_failure(self):
        """Test batch operations with authentication failure"""
        # Mock failed authentication
        self.mock_session_manager.validate_session.return_value = None
        
        # Import and test the function
        from main import batch_operations
        
        # Create mock args
        args = Mock()
        args.file = "test.csv"
        args.preview = False
        args.report = False
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            batch_operations(args)
            output = mock_stdout.getvalue()
            self.assertIn("Invalid or expired session", output)


if __name__ == '__main__':
    unittest.main()