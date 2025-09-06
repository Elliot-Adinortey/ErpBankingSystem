"""
Unit tests for batch processing functionality
"""

import unittest
import tempfile
import os
import json
import csv
from datetime import datetime
from unittest.mock import Mock, patch

from src.core.user import User
from src.core.account import Account
from src.managers.batch_manager import (
    BatchManager, BatchOperation, BatchFileParser, BatchValidator, 
    BatchExecutor, BatchReporter, BatchOperationType, BatchOperationStatus
)


class TestBatchOperation(unittest.TestCase):
    """Test BatchOperation class"""
    
    def test_batch_operation_creation(self):
        """Test creating a batch operation"""
        operation = BatchOperation("deposit", {"account": "savings", "amount": 100.0}, 1)
        
        self.assertEqual(operation.operation_type, "deposit")
        self.assertEqual(operation.parameters["account"], "savings")
        self.assertEqual(operation.parameters["amount"], 100.0)
        self.assertEqual(operation.line_number, 1)
        self.assertEqual(operation.status, BatchOperationStatus.PENDING)
        self.assertIsNone(operation.error_message)
        self.assertIsNone(operation.result)
    
    def test_batch_operation_to_dict(self):
        """Test converting batch operation to dictionary"""
        operation = BatchOperation("withdraw", {"account": "current", "amount": 50.0}, 2)
        operation.status = BatchOperationStatus.SUCCESS
        operation.result = "Withdrawal successful"
        operation.execution_time = 0.123
        
        result_dict = operation.to_dict()
        
        self.assertEqual(result_dict["operation_type"], "withdraw")
        self.assertEqual(result_dict["status"], "success")
        self.assertEqual(result_dict["result"], "Withdrawal successful")
        self.assertEqual(result_dict["execution_time"], 0.123)


class TestBatchFileParser(unittest.TestCase):
    """Test BatchFileParser class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_parse_csv_file_valid(self):
        """Test parsing valid CSV file"""
        csv_content = """operation_type,account,amount,to_account,memo,nickname,overdraft_limit
deposit,savings,100.00,,,
withdraw,current,50.00,,,
transfer,savings,75.00,current,Monthly transfer,
create_account,salary,1000.00,,,My Salary,500
update_nickname,current,,,,New Current,"""
        
        csv_file = os.path.join(self.temp_dir, "test_batch.csv")
        with open(csv_file, 'w', newline='') as f:
            f.write(csv_content)
        
        operations = BatchFileParser.parse_csv_file(csv_file)
        
        self.assertEqual(len(operations), 5)
        
        # Test deposit operation
        self.assertEqual(operations[0].operation_type, "deposit")
        self.assertEqual(operations[0].parameters["account"], "savings")
        self.assertEqual(operations[0].parameters["amount"], 100.0)
        
        # Test transfer operation
        self.assertEqual(operations[2].operation_type, "transfer")
        self.assertEqual(operations[2].parameters["to_account"], "current")
        self.assertEqual(operations[2].parameters["memo"], "Monthly transfer")
        
        # Test create account operation
        self.assertEqual(operations[3].operation_type, "create_account")
        self.assertEqual(operations[3].parameters["nickname"], "My Salary")
        self.assertEqual(operations[3].parameters["overdraft_limit"], 500.0)
    
    def test_parse_csv_file_invalid_amount(self):
        """Test parsing CSV file with invalid amount"""
        csv_content = """operation_type,account,amount,to_account,memo,nickname,overdraft_limit
deposit,savings,invalid_amount,,,"""
        
        csv_file = os.path.join(self.temp_dir, "test_invalid.csv")
        with open(csv_file, 'w', newline='') as f:
            f.write(csv_content)
        
        operations = BatchFileParser.parse_csv_file(csv_file)
        
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0].status, BatchOperationStatus.FAILED)
        self.assertIn("Invalid amount", operations[0].error_message)
    
    def test_parse_json_file_valid(self):
        """Test parsing valid JSON file"""
        json_data = {
            "operations": [
                {
                    "operation_type": "deposit",
                    "parameters": {
                        "account": "savings",
                        "amount": 100.0
                    }
                },
                {
                    "operation_type": "transfer",
                    "parameters": {
                        "account": "savings",
                        "to_account": "current",
                        "amount": 75.0,
                        "memo": "Test transfer"
                    }
                }
            ]
        }
        
        json_file = os.path.join(self.temp_dir, "test_batch.json")
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        operations = BatchFileParser.parse_json_file(json_file)
        
        self.assertEqual(len(operations), 2)
        self.assertEqual(operations[0].operation_type, "deposit")
        self.assertEqual(operations[1].operation_type, "transfer")
        self.assertEqual(operations[1].parameters["memo"], "Test transfer")
    
    def test_parse_json_file_invalid_format(self):
        """Test parsing invalid JSON file"""
        json_file = os.path.join(self.temp_dir, "invalid.json")
        with open(json_file, 'w') as f:
            f.write("{ invalid json }")
        
        with self.assertRaises(ValueError) as context:
            BatchFileParser.parse_json_file(json_file)
        
        self.assertIn("Invalid JSON format", str(context.exception))
    
    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file"""
        with self.assertRaises(FileNotFoundError):
            BatchFileParser.parse_csv_file("nonexistent.csv")


class TestBatchValidator(unittest.TestCase):
    """Test BatchValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "password123", "test@example.com")
        
        # Create test accounts
        savings_account = Account("savings", 1000.0)
        current_account = Account("current", 500.0, 200.0)
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
        
        self.validator = BatchValidator(self.user)
    
    def test_validate_deposit_valid(self):
        """Test validating valid deposit operation"""
        operation = BatchOperation("deposit", {"account": "savings", "amount": 100.0})
        
        operations = self.validator.validate_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.PENDING)
        self.assertIsNone(operations[0].error_message)
    
    def test_validate_deposit_invalid_account(self):
        """Test validating deposit with invalid account"""
        operation = BatchOperation("deposit", {"account": "nonexistent", "amount": 100.0})
        
        operations = self.validator.validate_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.FAILED)
        self.assertIn("Account 'nonexistent' not found", operations[0].error_message)
    
    def test_validate_deposit_negative_amount(self):
        """Test validating deposit with negative amount"""
        operation = BatchOperation("deposit", {"account": "savings", "amount": -100.0})
        
        operations = self.validator.validate_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.FAILED)
        self.assertIn("amount must be positive", operations[0].error_message)
    
    def test_validate_withdraw_insufficient_funds(self):
        """Test validating withdrawal with insufficient funds"""
        operation = BatchOperation("withdraw", {"account": "savings", "amount": 2000.0})
        
        operations = self.validator.validate_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.FAILED)
        self.assertIn("Insufficient funds", operations[0].error_message)
    
    def test_validate_transfer_valid(self):
        """Test validating valid transfer operation"""
        operation = BatchOperation("transfer", {
            "account": "savings",
            "to_account": "current",
            "amount": 100.0,
            "memo": "Test transfer"
        })
        
        operations = self.validator.validate_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.PENDING)
    
    def test_validate_create_account_existing_type(self):
        """Test validating create account with existing type"""
        operation = BatchOperation("create_account", {
            "account": "savings",
            "amount": 500.0
        })
        
        operations = self.validator.validate_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.FAILED)
        self.assertIn("already exists", operations[0].error_message)
    
    def test_validate_update_nickname_valid(self):
        """Test validating valid nickname update"""
        operation = BatchOperation("update_nickname", {
            "account": "savings",
            "nickname": "My Savings"
        })
        
        operations = self.validator.validate_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.PENDING)


class TestBatchExecutor(unittest.TestCase):
    """Test BatchExecutor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "password123", "test@example.com")
        
        # Create test accounts
        savings_account = Account("savings", 1000.0)
        current_account = Account("current", 500.0, 200.0)
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
        
        self.executor = BatchExecutor(self.user)
    
    def test_execute_deposit(self):
        """Test executing deposit operation"""
        operation = BatchOperation("deposit", {"account": "savings", "amount": 100.0})
        operation.status = BatchOperationStatus.PENDING
        
        operations = self.executor.execute_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.SUCCESS)
        self.assertIn("Deposited $100.00", operations[0].result)
        
        # Check account balance was updated
        savings_account = self.user.get_account("savings")
        self.assertEqual(savings_account.balance, 1100.0)
    
    def test_execute_withdraw(self):
        """Test executing withdraw operation"""
        operation = BatchOperation("withdraw", {"account": "current", "amount": 50.0})
        operation.status = BatchOperationStatus.PENDING
        
        operations = self.executor.execute_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.SUCCESS)
        self.assertIn("Withdrew $50.00", operations[0].result)
        
        # Check account balance was updated
        current_account = self.user.get_account("current")
        self.assertEqual(current_account.balance, 450.0)
    
    def test_execute_transfer(self):
        """Test executing transfer operation"""
        operation = BatchOperation("transfer", {
            "account": "savings",
            "to_account": "current",
            "amount": 200.0,
            "memo": "Test transfer"
        })
        operation.status = BatchOperationStatus.PENDING
        
        operations = self.executor.execute_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.SUCCESS)
        self.assertIn("Transfer of $200.00", operations[0].result)
        
        # Check account balances were updated
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        self.assertEqual(savings_account.balance, 800.0)
        self.assertEqual(current_account.balance, 700.0)
    
    def test_execute_create_account(self):
        """Test executing create account operation"""
        operation = BatchOperation("create_account", {
            "account": "salary",
            "amount": 1500.0,
            "nickname": "My Salary",
            "overdraft_limit": 300.0
        })
        operation.status = BatchOperationStatus.PENDING
        
        operations = self.executor.execute_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.SUCCESS)
        self.assertIn("Created salary account", operations[0].result)
        
        # Check account was created
        salary_account = self.user.get_account("salary")
        self.assertIsNotNone(salary_account)
        self.assertEqual(salary_account.balance, 1500.0)
        self.assertEqual(salary_account.nickname, "My Salary")
    
    def test_execute_update_nickname(self):
        """Test executing update nickname operation"""
        operation = BatchOperation("update_nickname", {
            "account": "current",
            "nickname": "Updated Current"
        })
        operation.status = BatchOperationStatus.PENDING
        
        operations = self.executor.execute_operations([operation])
        
        self.assertEqual(operations[0].status, BatchOperationStatus.SUCCESS)
        self.assertIn("Updated nickname", operations[0].result)
        
        # Check nickname was updated
        current_account = self.user.get_account("current")
        self.assertEqual(current_account.nickname, "Updated Current")
    
    def test_execute_with_progress_callback(self):
        """Test executing operations with progress callback"""
        operations = [
            BatchOperation("deposit", {"account": "savings", "amount": 100.0}),
            BatchOperation("withdraw", {"account": "current", "amount": 50.0})
        ]
        
        for op in operations:
            op.status = BatchOperationStatus.PENDING
        
        progress_calls = []
        
        def progress_callback(completed, total, operation):
            progress_calls.append((completed, total, operation.operation_type))
        
        self.executor.execute_operations(operations, progress_callback)
        
        self.assertEqual(len(progress_calls), 2)
        self.assertEqual(progress_calls[0], (1, 2, "deposit"))
        self.assertEqual(progress_calls[1], (2, 2, "withdraw"))


class TestBatchReporter(unittest.TestCase):
    """Test BatchReporter class"""
    
    def test_generate_summary_report(self):
        """Test generating summary report"""
        operations = [
            BatchOperation("deposit", {"account": "savings", "amount": 100.0}),
            BatchOperation("withdraw", {"account": "current", "amount": 50.0}),
            BatchOperation("transfer", {"account": "savings", "to_account": "current", "amount": 75.0})
        ]
        
        # Set different statuses
        operations[0].status = BatchOperationStatus.SUCCESS
        operations[0].execution_time = 0.1
        operations[1].status = BatchOperationStatus.SUCCESS
        operations[1].execution_time = 0.2
        operations[2].status = BatchOperationStatus.FAILED
        operations[2].error_message = "Test error"
        
        summary = BatchReporter.generate_summary_report(operations)
        
        self.assertEqual(summary['total_operations'], 3)
        self.assertEqual(summary['successful'], 2)
        self.assertEqual(summary['failed'], 1)
        self.assertAlmostEqual(summary['success_rate'], 66.67, places=1)
        self.assertAlmostEqual(summary['total_execution_time'], 0.3, places=1)
        
        # Check operations by type
        self.assertIn('deposit', summary['operations_by_type'])
        self.assertEqual(summary['operations_by_type']['deposit']['successful'], 1)
        self.assertEqual(summary['operations_by_type']['transfer']['failed'], 1)
        
        # Check failed operations are included
        self.assertEqual(len(summary['failed_operations']), 1)
        self.assertEqual(summary['failed_operations'][0]['operation_type'], 'transfer')
    
    def test_generate_detailed_report(self):
        """Test generating detailed text report"""
        operations = [
            BatchOperation("deposit", {"account": "savings", "amount": 100.0}),
            BatchOperation("withdraw", {"account": "current", "amount": 50.0})
        ]
        
        operations[0].status = BatchOperationStatus.SUCCESS
        operations[0].result = "Deposit successful"
        operations[0].execution_time = 0.1
        operations[1].status = BatchOperationStatus.FAILED
        operations[1].error_message = "Insufficient funds"
        
        report = BatchReporter.generate_detailed_report(operations)
        
        self.assertIn("BATCH OPERATION DETAILED REPORT", report)
        self.assertIn("Total Operations: 2", report)
        self.assertIn("Successful: 1", report)
        self.assertIn("Failed: 1", report)
        self.assertIn("✓ DEPOSIT", report)
        self.assertIn("✗ WITHDRAW", report)
        self.assertIn("Deposit successful", report)
        self.assertIn("Insufficient funds", report)


class TestBatchManager(unittest.TestCase):
    """Test BatchManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "password123", "test@example.com")
        
        # Create test accounts
        savings_account = Account("savings", 1000.0)
        current_account = Account("current", 500.0, 200.0)
        self.user.add_account(savings_account)
        self.user.add_account(current_account)
        
        self.batch_manager = BatchManager(self.user)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_process_batch_file_csv_preview(self):
        """Test processing CSV batch file in preview mode"""
        csv_content = """operation_type,account,amount,to_account,memo,nickname,overdraft_limit
deposit,savings,100.00,,,
withdraw,current,50.00,,,"""
        
        csv_file = os.path.join(self.temp_dir, "test_batch.csv")
        with open(csv_file, 'w', newline='') as f:
            f.write(csv_content)
        
        operations, summary = self.batch_manager.process_batch_file(csv_file, preview_mode=True)
        
        self.assertEqual(len(operations), 2)
        self.assertEqual(summary['total_operations'], 2)
        
        # In preview mode, operations should be validated but not executed
        for op in operations:
            self.assertIn(op.status, [BatchOperationStatus.PENDING, BatchOperationStatus.FAILED])
    
    def test_process_batch_file_csv_execute(self):
        """Test processing CSV batch file with execution"""
        csv_content = """operation_type,account,amount,to_account,memo,nickname,overdraft_limit
deposit,savings,100.00,,,
withdraw,current,50.00,,,"""
        
        csv_file = os.path.join(self.temp_dir, "test_batch.csv")
        with open(csv_file, 'w', newline='') as f:
            f.write(csv_content)
        
        operations, summary = self.batch_manager.process_batch_file(csv_file, preview_mode=False)
        
        self.assertEqual(len(operations), 2)
        self.assertEqual(summary['successful'], 2)
        
        # Check account balances were updated
        savings_account = self.user.get_account("savings")
        current_account = self.user.get_account("current")
        self.assertEqual(savings_account.balance, 1100.0)
        self.assertEqual(current_account.balance, 450.0)
    
    def test_process_batch_file_unsupported_format(self):
        """Test processing file with unsupported format"""
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, 'w') as f:
            f.write("some content")
        
        with self.assertRaises(ValueError) as context:
            self.batch_manager.process_batch_file(txt_file)
        
        self.assertIn("Unsupported file format", str(context.exception))
    
    def test_create_csv_template(self):
        """Test creating CSV template"""
        template_file = os.path.join(self.temp_dir, "template.csv")
        
        result = self.batch_manager.create_batch_template(template_file, 'csv')
        
        self.assertIn("CSV template created", result)
        self.assertTrue(os.path.exists(template_file))
        
        # Check template content
        with open(template_file, 'r') as f:
            content = f.read()
            self.assertIn("operation_type,account,amount", content)
            self.assertIn("deposit,savings,100.00", content)
    
    def test_create_json_template(self):
        """Test creating JSON template"""
        template_file = os.path.join(self.temp_dir, "template.json")
        
        result = self.batch_manager.create_batch_template(template_file, 'json')
        
        self.assertIn("JSON template created", result)
        self.assertTrue(os.path.exists(template_file))
        
        # Check template content
        with open(template_file, 'r') as f:
            data = json.load(f)
            self.assertIn("operations", data)
            self.assertEqual(data["operations"][0]["operation_type"], "deposit")


if __name__ == '__main__':
    unittest.main()