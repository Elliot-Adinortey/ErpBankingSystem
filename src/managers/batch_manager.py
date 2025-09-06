"""
Batch Manager Module

This module handles batch processing of multiple banking operations from files,
including validation, execution, progress tracking, and reporting.
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum
import uuid
import os


class BatchOperationType(Enum):
    """Supported batch operation types"""
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    CREATE_ACCOUNT = "create_account"
    UPDATE_NICKNAME = "update_nickname"


class BatchOperationStatus(Enum):
    """Status of batch operations"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class BatchOperation:
    """Represents a single operation in a batch"""
    
    def __init__(self, operation_type: str, parameters: Dict[str, Any], line_number: int = None):
        self.id = str(uuid.uuid4())
        self.operation_type = operation_type
        self.parameters = parameters
        self.line_number = line_number
        self.status = BatchOperationStatus.PENDING
        self.error_message = None
        self.result = None
        self.execution_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary for reporting"""
        return {
            'id': self.id,
            'operation_type': self.operation_type,
            'parameters': self.parameters,
            'line_number': self.line_number,
            'status': self.status.value,
            'error_message': self.error_message,
            'result': self.result,
            'execution_time': self.execution_time
        }


class BatchFileParser:
    """Parses batch operation files in various formats"""
    
    @staticmethod
    def parse_csv_file(file_path: str) -> List[BatchOperation]:
        """
        Parse CSV batch file
        
        Expected CSV format:
        operation_type,account,amount,to_account,memo,nickname,overdraft_limit
        deposit,savings,100.00,,,
        withdraw,current,50.00,,,
        transfer,savings,75.00,current,Monthly transfer,
        create_account,new_savings,500.00,,,My Savings,1000
        update_nickname,current,,,,New Current,
        """
        operations = []
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Batch file not found: {file_path}")
        
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for line_number, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                try:
                    operation = BatchFileParser._parse_csv_row(row, line_number)
                    if operation:
                        operations.append(operation)
                except Exception as e:
                    # Create a failed operation for invalid rows
                    failed_op = BatchOperation("invalid", row, line_number)
                    failed_op.status = BatchOperationStatus.FAILED
                    failed_op.error_message = f"Parse error: {str(e)}"
                    operations.append(failed_op)
        
        return operations
    
    @staticmethod
    def _parse_csv_row(row: Dict[str, str], line_number: int) -> Optional[BatchOperation]:
        """Parse a single CSV row into a BatchOperation"""
        operation_type = row.get('operation_type', '').strip().lower()
        
        if not operation_type or operation_type.startswith('#'):
            return None  # Skip empty rows and comments
        
        # Clean and prepare parameters
        parameters = {}
        
        # Common parameters
        if row.get('account'):
            parameters['account'] = row['account'].strip()
        if row.get('amount'):
            try:
                parameters['amount'] = float(row['amount'].strip())
            except ValueError:
                raise ValueError(f"Invalid amount: {row['amount']}")
        
        # Operation-specific parameters
        if operation_type == 'transfer':
            if not row.get('to_account'):
                raise ValueError("Transfer operations require 'to_account' parameter")
            parameters['to_account'] = row['to_account'].strip()
            if row.get('memo'):
                parameters['memo'] = row['memo'].strip()
        
        elif operation_type == 'create_account':
            if not row.get('account'):
                raise ValueError("Create account operations require 'account' parameter (account type)")
            if row.get('nickname'):
                parameters['nickname'] = row['nickname'].strip()
            if row.get('overdraft_limit'):
                try:
                    parameters['overdraft_limit'] = float(row['overdraft_limit'].strip())
                except ValueError:
                    raise ValueError(f"Invalid overdraft_limit: {row['overdraft_limit']}")
        
        elif operation_type == 'update_nickname':
            if not row.get('nickname'):
                raise ValueError("Update nickname operations require 'nickname' parameter")
            parameters['nickname'] = row['nickname'].strip()
        
        # Validate operation type
        try:
            BatchOperationType(operation_type)
        except ValueError:
            raise ValueError(f"Unsupported operation type: {operation_type}")
        
        return BatchOperation(operation_type, parameters, line_number)
    
    @staticmethod
    def parse_json_file(file_path: str) -> List[BatchOperation]:
        """
        Parse JSON batch file
        
        Expected JSON format:
        {
            "operations": [
                {
                    "operation_type": "deposit",
                    "parameters": {
                        "account": "savings",
                        "amount": 100.00
                    }
                },
                {
                    "operation_type": "transfer",
                    "parameters": {
                        "account": "savings",
                        "to_account": "current",
                        "amount": 75.00,
                        "memo": "Monthly transfer"
                    }
                }
            ]
        }
        """
        operations = []
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Batch file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            try:
                data = json.load(jsonfile)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {str(e)}")
        
        if 'operations' not in data:
            raise ValueError("JSON file must contain 'operations' array")
        
        for index, op_data in enumerate(data['operations']):
            try:
                operation_type = op_data.get('operation_type', '').strip().lower()
                parameters = op_data.get('parameters', {})
                
                # Validate operation type
                try:
                    BatchOperationType(operation_type)
                except ValueError:
                    raise ValueError(f"Unsupported operation type: {operation_type}")
                
                operation = BatchOperation(operation_type, parameters, index + 1)
                operations.append(operation)
                
            except Exception as e:
                # Create a failed operation for invalid entries
                failed_op = BatchOperation("invalid", op_data, index + 1)
                failed_op.status = BatchOperationStatus.FAILED
                failed_op.error_message = f"Parse error: {str(e)}"
                operations.append(failed_op)
        
        return operations


class BatchValidator:
    """Validates batch operations before execution"""
    
    def __init__(self, user):
        self.user = user
    
    def validate_operations(self, operations: List[BatchOperation]) -> List[BatchOperation]:
        """Validate all operations in the batch"""
        for operation in operations:
            if operation.status == BatchOperationStatus.FAILED:
                continue  # Skip already failed operations
            
            try:
                self._validate_single_operation(operation)
                if operation.status == BatchOperationStatus.PENDING:
                    operation.status = BatchOperationStatus.PENDING  # Validation passed
            except Exception as e:
                operation.status = BatchOperationStatus.FAILED
                operation.error_message = f"Validation error: {str(e)}"
        
        return operations
    
    def _validate_single_operation(self, operation: BatchOperation):
        """Validate a single operation"""
        op_type = operation.operation_type
        params = operation.parameters
        
        if op_type == 'deposit':
            self._validate_deposit(params)
        elif op_type == 'withdraw':
            self._validate_withdraw(params)
        elif op_type == 'transfer':
            self._validate_transfer(params)
        elif op_type == 'create_account':
            self._validate_create_account(params)
        elif op_type == 'update_nickname':
            self._validate_update_nickname(params)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    def _validate_deposit(self, params: Dict[str, Any]):
        """Validate deposit operation parameters"""
        if 'account' not in params:
            raise ValueError("Deposit requires 'account' parameter")
        if 'amount' not in params:
            raise ValueError("Deposit requires 'amount' parameter")
        if params['amount'] <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # Check if account exists
        account = self.user.get_account(params['account'])
        if not account:
            raise ValueError(f"Account '{params['account']}' not found")
    
    def _validate_withdraw(self, params: Dict[str, Any]):
        """Validate withdraw operation parameters"""
        if 'account' not in params:
            raise ValueError("Withdraw requires 'account' parameter")
        if 'amount' not in params:
            raise ValueError("Withdraw requires 'amount' parameter")
        if params['amount'] <= 0:
            raise ValueError("Withdraw amount must be positive")
        
        # Check if account exists and has sufficient funds
        account = self.user.get_account(params['account'])
        if not account:
            raise ValueError(f"Account '{params['account']}' not found")
        
        # Check available balance (including overdraft)
        available_balance = account.balance
        if account.account_type == 'current':
            available_balance += account.overdraft_limit
        
        if available_balance < params['amount']:
            raise ValueError(f"Insufficient funds. Available: ${available_balance:.2f}")
    
    def _validate_transfer(self, params: Dict[str, Any]):
        """Validate transfer operation parameters"""
        required_params = ['account', 'to_account', 'amount']
        for param in required_params:
            if param not in params:
                raise ValueError(f"Transfer requires '{param}' parameter")
        
        if params['amount'] <= 0:
            raise ValueError("Transfer amount must be positive")
        
        # Use existing transfer validation
        is_valid, error_message, _, _ = self.user.validate_transfer(
            params['account'], params['to_account'], params['amount']
        )
        
        if not is_valid:
            raise ValueError(error_message)
    
    def _validate_create_account(self, params: Dict[str, Any]):
        """Validate create account operation parameters"""
        if 'account' not in params:
            raise ValueError("Create account requires 'account' parameter (account type)")
        
        account_type = params['account']
        valid_types = ['savings', 'current', 'salary']
        if account_type not in valid_types:
            raise ValueError(f"Invalid account type. Must be one of: {valid_types}")
        
        # Check if account type already exists
        existing_account = self.user.get_account(account_type)
        if existing_account:
            raise ValueError(f"Account of type '{account_type}' already exists")
        
        # Validate optional parameters
        if 'amount' in params and params['amount'] < 0:
            raise ValueError("Initial balance cannot be negative")
        
        if 'overdraft_limit' in params and params['overdraft_limit'] < 0:
            raise ValueError("Overdraft limit cannot be negative")
    
    def _validate_update_nickname(self, params: Dict[str, Any]):
        """Validate update nickname operation parameters"""
        if 'account' not in params:
            raise ValueError("Update nickname requires 'account' parameter")
        if 'nickname' not in params:
            raise ValueError("Update nickname requires 'nickname' parameter")
        
        # Check if account exists
        account = self.user.get_account(params['account'])
        if not account:
            raise ValueError(f"Account '{params['account']}' not found")


class BatchExecutor:
    """Executes validated batch operations"""
    
    def __init__(self, user):
        self.user = user
    
    def execute_operations(self, operations: List[BatchOperation], 
                          progress_callback=None) -> List[BatchOperation]:
        """
        Execute all operations in the batch
        
        Args:
            operations: List of validated batch operations
            progress_callback: Optional callback function for progress updates
        
        Returns:
            List of operations with updated status and results
        """
        total_operations = len([op for op in operations if op.status == BatchOperationStatus.PENDING])
        completed = 0
        
        for operation in operations:
            if operation.status != BatchOperationStatus.PENDING:
                continue  # Skip failed or already processed operations
            
            operation.status = BatchOperationStatus.PROCESSING
            start_time = datetime.now()
            
            try:
                result = self._execute_single_operation(operation)
                operation.status = BatchOperationStatus.SUCCESS
                operation.result = result
                completed += 1
                
            except Exception as e:
                operation.status = BatchOperationStatus.FAILED
                operation.error_message = f"Execution error: {str(e)}"
            
            finally:
                operation.execution_time = (datetime.now() - start_time).total_seconds()
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(completed, total_operations, operation)
        
        return operations
    
    def _execute_single_operation(self, operation: BatchOperation) -> str:
        """Execute a single operation and return result message"""
        op_type = operation.operation_type
        params = operation.parameters
        
        if op_type == 'deposit':
            return self._execute_deposit(params)
        elif op_type == 'withdraw':
            return self._execute_withdraw(params)
        elif op_type == 'transfer':
            return self._execute_transfer(params)
        elif op_type == 'create_account':
            return self._execute_create_account(params)
        elif op_type == 'update_nickname':
            return self._execute_update_nickname(params)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    def _execute_deposit(self, params: Dict[str, Any]) -> str:
        """Execute deposit operation"""
        account = self.user.get_account(params['account'])
        old_balance = account.balance
        account.deposit(params['amount'])
        return f"Deposited ${params['amount']:.2f} to {account.get_display_name()}. Balance: ${old_balance:.2f} → ${account.balance:.2f}"
    
    def _execute_withdraw(self, params: Dict[str, Any]) -> str:
        """Execute withdraw operation"""
        account = self.user.get_account(params['account'])
        old_balance = account.balance
        account.withdraw(params['amount'])
        return f"Withdrew ${params['amount']:.2f} from {account.get_display_name()}. Balance: ${old_balance:.2f} → ${account.balance:.2f}"
    
    def _execute_transfer(self, params: Dict[str, Any]) -> str:
        """Execute transfer operation"""
        memo = params.get('memo')
        success, message, transfer_id = self.user.transfer_between_accounts(
            params['account'], params['to_account'], params['amount'], memo
        )
        
        if not success:
            raise Exception(message)
        
        return message
    
    def _execute_create_account(self, params: Dict[str, Any]) -> str:
        """Execute create account operation"""
        account_type = params['account']
        balance = params.get('amount', 0)
        overdraft_limit = params.get('overdraft_limit', 0)
        nickname = params.get('nickname')
        
        account = self.user.create_account_with_nickname(
            account_type, balance, overdraft_limit, nickname
        )
        
        return f"Created {account_type} account with balance ${balance:.2f}" + (
            f" and nickname '{nickname}'" if nickname else ""
        )
    
    def _execute_update_nickname(self, params: Dict[str, Any]) -> str:
        """Execute update nickname operation"""
        account_identifier = params['account']
        nickname = params['nickname']
        
        success = self.user.update_account_nickname(account_identifier, nickname)
        if not success:
            raise Exception(f"Failed to update nickname for account '{account_identifier}'")
        
        return f"Updated nickname for account '{account_identifier}' to '{nickname}'"


class BatchReporter:
    """Generates reports for batch operations"""
    
    @staticmethod
    def generate_summary_report(operations: List[BatchOperation]) -> Dict[str, Any]:
        """Generate summary report of batch execution"""
        total_operations = len(operations)
        successful = len([op for op in operations if op.status == BatchOperationStatus.SUCCESS])
        failed = len([op for op in operations if op.status == BatchOperationStatus.FAILED])
        skipped = len([op for op in operations if op.status == BatchOperationStatus.SKIPPED])
        
        # Calculate execution time
        executed_ops = [op for op in operations if op.execution_time is not None]
        total_execution_time = sum(op.execution_time for op in executed_ops)
        
        # Group operations by type
        operations_by_type = {}
        for op in operations:
            op_type = op.operation_type
            if op_type not in operations_by_type:
                operations_by_type[op_type] = {'total': 0, 'successful': 0, 'failed': 0}
            
            operations_by_type[op_type]['total'] += 1
            if op.status == BatchOperationStatus.SUCCESS:
                operations_by_type[op_type]['successful'] += 1
            elif op.status == BatchOperationStatus.FAILED:
                operations_by_type[op_type]['failed'] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_operations': total_operations,
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'success_rate': (successful / total_operations * 100) if total_operations > 0 else 0,
            'total_execution_time': total_execution_time,
            'operations_by_type': operations_by_type,
            'failed_operations': [op.to_dict() for op in operations if op.status == BatchOperationStatus.FAILED]
        }
    
    @staticmethod
    def generate_detailed_report(operations: List[BatchOperation]) -> str:
        """Generate detailed text report of batch execution"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("BATCH OPERATION DETAILED REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary section
        summary = BatchReporter.generate_summary_report(operations)
        report_lines.append("SUMMARY:")
        report_lines.append(f"  Total Operations: {summary['total_operations']}")
        report_lines.append(f"  Successful: {summary['successful']}")
        report_lines.append(f"  Failed: {summary['failed']}")
        report_lines.append(f"  Success Rate: {summary['success_rate']:.1f}%")
        report_lines.append(f"  Total Execution Time: {summary['total_execution_time']:.2f} seconds")
        report_lines.append("")
        
        # Operations by type
        if summary['operations_by_type']:
            report_lines.append("OPERATIONS BY TYPE:")
            for op_type, stats in summary['operations_by_type'].items():
                report_lines.append(f"  {op_type.upper()}:")
                report_lines.append(f"    Total: {stats['total']}")
                report_lines.append(f"    Successful: {stats['successful']}")
                report_lines.append(f"    Failed: {stats['failed']}")
            report_lines.append("")
        
        # Detailed operation results
        report_lines.append("DETAILED RESULTS:")
        for i, operation in enumerate(operations, 1):
            status_symbol = "✓" if operation.status == BatchOperationStatus.SUCCESS else "✗"
            report_lines.append(f"  {i:3d}. {status_symbol} {operation.operation_type.upper()}")
            
            if operation.line_number:
                report_lines.append(f"       Line: {operation.line_number}")
            
            report_lines.append(f"       Status: {operation.status.value}")
            
            if operation.result:
                report_lines.append(f"       Result: {operation.result}")
            
            if operation.error_message:
                report_lines.append(f"       Error: {operation.error_message}")
            
            if operation.execution_time is not None:
                report_lines.append(f"       Time: {operation.execution_time:.3f}s")
            
            report_lines.append("")
        
        return "\n".join(report_lines)


class BatchManager:
    """Main batch processing manager"""
    
    def __init__(self, user):
        self.user = user
        self.validator = BatchValidator(user)
        self.executor = BatchExecutor(user)
    
    def process_batch_file(self, file_path: str, preview_mode: bool = False, 
                          progress_callback=None) -> Tuple[List[BatchOperation], Dict[str, Any]]:
        """
        Process a batch file with operations
        
        Args:
            file_path: Path to the batch file (CSV or JSON)
            preview_mode: If True, only validate without executing
            progress_callback: Optional callback for progress updates
        
        Returns:
            Tuple of (operations_list, summary_report)
        """
        # Determine file format and parse
        if file_path.lower().endswith('.csv'):
            operations = BatchFileParser.parse_csv_file(file_path)
        elif file_path.lower().endswith('.json'):
            operations = BatchFileParser.parse_json_file(file_path)
        else:
            raise ValueError("Unsupported file format. Use .csv or .json files")
        
        # Validate operations
        operations = self.validator.validate_operations(operations)
        
        # Execute operations (unless in preview mode)
        if not preview_mode:
            operations = self.executor.execute_operations(operations, progress_callback)
        
        # Generate summary report
        summary_report = BatchReporter.generate_summary_report(operations)
        
        return operations, summary_report
    
    def create_batch_template(self, file_path: str, format: str = 'csv') -> str:
        """Create a template batch file for users"""
        if format.lower() == 'csv':
            return self._create_csv_template(file_path)
        elif format.lower() == 'json':
            return self._create_json_template(file_path)
        else:
            raise ValueError("Unsupported format. Use 'csv' or 'json'")
    
    def _create_csv_template(self, file_path: str) -> str:
        """Create CSV template file"""
        template_content = """operation_type,account,amount,to_account,memo,nickname,overdraft_limit
# Deposit $100 to savings account
deposit,savings,100.00,,,
# Withdraw $50 from current account
withdraw,current,50.00,,,
# Transfer $75 from savings to current with memo
transfer,savings,75.00,current,Monthly transfer,
# Create new salary account with $1000 initial balance and nickname
create_account,salary,1000.00,,,My Salary,500
# Update nickname for current account
update_nickname,current,,,,Updated Current,
"""
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            f.write(template_content)
        
        return f"CSV template created at: {file_path}"
    
    def _create_json_template(self, file_path: str) -> str:
        """Create JSON template file"""
        template_data = {
            "operations": [
                {
                    "operation_type": "deposit",
                    "parameters": {
                        "account": "savings",
                        "amount": 100.00
                    }
                },
                {
                    "operation_type": "withdraw",
                    "parameters": {
                        "account": "current",
                        "amount": 50.00
                    }
                },
                {
                    "operation_type": "transfer",
                    "parameters": {
                        "account": "savings",
                        "to_account": "current",
                        "amount": 75.00,
                        "memo": "Monthly transfer"
                    }
                },
                {
                    "operation_type": "create_account",
                    "parameters": {
                        "account": "salary",
                        "amount": 1000.00,
                        "nickname": "My Salary",
                        "overdraft_limit": 500
                    }
                },
                {
                    "operation_type": "update_nickname",
                    "parameters": {
                        "account": "current",
                        "nickname": "Updated Current"
                    }
                }
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2)
        
        return f"JSON template created at: {file_path}"