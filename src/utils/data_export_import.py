"""
Data Export and Import System

This module handles exporting and importing account and transaction data
in various formats including CSV and JSON with validation and error handling.
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from io import StringIO
import re


class DataExporter:
    """Handles data export operations for accounts and transactions"""
    
    def __init__(self, user):
        self.user = user
    
    def export_transactions_csv(self, account_identifier: str = None, start_date: datetime = None, 
                               end_date: datetime = None, filename: str = None) -> str:
        """
        Export transaction data to CSV format
        
        Args:
            account_identifier: Specific account or None for all accounts
            start_date: Start date filter
            end_date: End date filter
            filename: Optional custom filename
            
        Returns:
            Path to the exported CSV file
        """
        # Get transactions
        transactions = self._get_filtered_transactions(account_identifier, start_date, end_date)
        
        # Generate filename if not provided
        if not filename:
            account_part = account_identifier.replace(' ', '_') if account_identifier else 'all_accounts'
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"transactions_{account_part}_{date_str}.csv"
        
        # Ensure exports directory exists
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        filepath = os.path.join(exports_dir, filename)
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'account', 'account_type', 'transaction_type', 'amount', 
                         'balance_after', 'transfer_id', 'memo', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for tx_data in transactions:
                # Calculate balance after transaction (approximate)
                balance_after = self._calculate_balance_after_transaction(
                    tx_data['account_obj'], tx_data['transaction']
                )
                
                # Extract additional fields for transfers
                transfer_id = getattr(tx_data['transaction'], 'transfer_id', '')
                memo = getattr(tx_data['transaction'], 'memo', '')
                
                # Create description
                description = self._create_transaction_description(tx_data['transaction'])
                
                writer.writerow({
                    'date': tx_data['transaction'].date.strftime('%Y-%m-%d %H:%M:%S'),
                    'account': tx_data['account_name'],
                    'account_type': tx_data['account_type'],
                    'transaction_type': tx_data['transaction'].transaction_type,
                    'amount': tx_data['transaction'].amount,
                    'balance_after': balance_after,
                    'transfer_id': transfer_id,
                    'memo': memo,
                    'description': description
                })
        
        return filepath
    
    def export_accounts_json(self, filename: str = None) -> str:
        """
        Export account data to JSON format
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to the exported JSON file
        """
        if not filename:
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"accounts_{self.user.username}_{date_str}.json"
        
        # Ensure exports directory exists
        exports_dir = "exports"
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        filepath = os.path.join(exports_dir, filename)
        
        # Prepare account data
        accounts_data = {
            'export_info': {
                'username': self.user.username,
                'email': self.user.email,
                'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_accounts': len(self.user.accounts)
            },
            'accounts': []
        }
        
        for account in self.user.accounts:
            account_data = {
                'account_type': account.account_type,
                'nickname': account.nickname,
                'balance': account.balance,
                'overdraft_limit': account.overdraft_limit,
                'created_date': account.created_date.strftime('%Y-%m-%d %H:%M:%S'),
                'last_activity': account.last_activity.strftime('%Y-%m-%d %H:%M:%S'),
                'transaction_count': len(account.transactions),
                'transactions': []
            }
            
            # Add transaction data
            for transaction in account.transactions:
                tx_data = {
                    'date': transaction.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'amount': transaction.amount,
                    'transaction_type': transaction.transaction_type
                }
                
                # Add transfer-specific fields if applicable
                if hasattr(transaction, 'transfer_id'):
                    tx_data['transfer_id'] = transaction.transfer_id
                    tx_data['from_account'] = transaction.from_account
                    tx_data['to_account'] = transaction.to_account
                    tx_data['memo'] = transaction.memo
                    tx_data['is_outgoing'] = transaction.is_outgoing
                
                account_data['transactions'].append(tx_data)
            
            accounts_data['accounts'].append(account_data)
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(accounts_data, jsonfile, indent=2, ensure_ascii=False)
        
        return filepath
    
    def export_full_backup(self, filename: str = None) -> str:
        """
        Export complete user data backup in JSON format
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to the exported backup file
        """
        if not filename:
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"full_backup_{self.user.username}_{date_str}.json"
        
        # Ensure backups directory exists
        backups_dir = "backups"
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)
        
        filepath = os.path.join(backups_dir, filename)
        
        # Create comprehensive backup data
        backup_data = {
            'backup_info': {
                'username': self.user.username,
                'email': self.user.email,
                'backup_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '1.0'
            },
            'user_data': {
                'username': self.user.username,
                'email': self.user.email,
                'password_hash': self.user.password,  # Hashed password for restore
                'accounts': []
            }
        }
        
        # Add account data with full transaction history
        for account in self.user.accounts:
            account_data = {
                'account_type': account.account_type,
                'nickname': account.nickname,
                'balance': account.balance,
                'overdraft_limit': account.overdraft_limit,
                'created_date': account.created_date.strftime('%Y-%m-%d %H:%M:%S'),
                'last_activity': account.last_activity.strftime('%Y-%m-%d %H:%M:%S'),
                'transactions': []
            }
            
            # Add all transaction details
            for transaction in account.transactions:
                tx_data = transaction.to_dict()
                account_data['transactions'].append(tx_data)
            
            backup_data['user_data']['accounts'].append(account_data)
        
        # Write backup file
        with open(filepath, 'w', encoding='utf-8') as backupfile:
            json.dump(backup_data, backupfile, indent=2, ensure_ascii=False)
        
        return filepath
    
    def _get_filtered_transactions(self, account_identifier: str = None, 
                                  start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get filtered transactions from specified accounts"""
        transactions = []
        
        # Determine which accounts to process
        if account_identifier:
            account = self.user.get_account(account_identifier)
            if not account:
                raise ValueError(f"Account '{account_identifier}' not found")
            accounts_to_process = [account]
        else:
            accounts_to_process = self.user.accounts
        
        # Collect transactions
        for account in accounts_to_process:
            for transaction in account.transactions:
                # Apply date filters
                if start_date and transaction.date < start_date:
                    continue
                if end_date and transaction.date > end_date:
                    continue
                
                transactions.append({
                    'account_obj': account,
                    'account_name': account.get_display_name(),
                    'account_type': account.account_type,
                    'transaction': transaction
                })
        
        # Sort by date
        transactions.sort(key=lambda x: x['transaction'].date)
        return transactions
    
    def _calculate_balance_after_transaction(self, account, transaction) -> float:
        """Calculate approximate balance after a specific transaction"""
        # This is an approximation since we don't store historical balances
        current_balance = account.balance
        
        # Find all transactions after this one and reverse their effect
        later_transactions = [t for t in account.transactions if t.date > transaction.date]
        
        for later_tx in later_transactions:
            if later_tx.transaction_type in ['deposit', 'interest']:
                current_balance -= later_tx.amount
            elif later_tx.transaction_type == 'withdrawal':
                current_balance += abs(later_tx.amount)
            elif hasattr(later_tx, 'is_outgoing'):
                if later_tx.is_outgoing:
                    current_balance += abs(later_tx.amount)
                else:
                    current_balance -= later_tx.amount
        
        return current_balance
    
    def _create_transaction_description(self, transaction) -> str:
        """Create a descriptive text for the transaction"""
        if hasattr(transaction, 'transfer_id'):
            direction = "to" if transaction.is_outgoing else "from"
            other_account = transaction.to_account if transaction.is_outgoing else transaction.from_account
            return f"Transfer {direction} {other_account}"
        elif transaction.transaction_type == 'interest':
            return "Interest payment"
        else:
            return transaction.transaction_type.capitalize()


class DataImporter:
    """Handles data import operations with validation"""
    
    def __init__(self, user):
        self.user = user
    
    def import_transactions_csv(self, filepath: str, validate_only: bool = False) -> Dict[str, Any]:
        """
        Import transaction data from CSV file
        
        Args:
            filepath: Path to CSV file
            validate_only: If True, only validate without importing
            
        Returns:
            Dictionary with import results and validation errors
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        results = {
            'total_rows': 0,
            'valid_transactions': 0,
            'invalid_transactions': 0,
            'errors': [],
            'imported_transactions': [],
            'validation_only': validate_only
        }
        
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                results['total_rows'] += 1
                
                try:
                    # Validate and parse transaction data
                    validation_result = self._validate_transaction_row(row, row_num)
                    
                    if validation_result['valid']:
                        results['valid_transactions'] += 1
                        
                        if not validate_only:
                            # Import the transaction
                            self._import_transaction(validation_result['transaction_data'])
                            results['imported_transactions'].append(validation_result['transaction_data'])
                    else:
                        results['invalid_transactions'] += 1
                        results['errors'].extend(validation_result['errors'])
                
                except Exception as e:
                    results['invalid_transactions'] += 1
                    results['errors'].append(f"Row {row_num}: Unexpected error - {str(e)}")
        
        return results
    
    def import_accounts_json(self, filepath: str, validate_only: bool = False) -> Dict[str, Any]:
        """
        Import account data from JSON file
        
        Args:
            filepath: Path to JSON file
            validate_only: If True, only validate without importing
            
        Returns:
            Dictionary with import results and validation errors
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        results = {
            'total_accounts': 0,
            'valid_accounts': 0,
            'invalid_accounts': 0,
            'errors': [],
            'imported_accounts': [],
            'validation_only': validate_only
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            
            # Validate JSON structure
            if 'accounts' not in data:
                results['errors'].append("Invalid JSON structure: 'accounts' key not found")
                return results
            
            accounts_data = data['accounts']
            results['total_accounts'] = len(accounts_data)
            
            for account_num, account_data in enumerate(accounts_data):
                try:
                    validation_result = self._validate_account_data(account_data, account_num)
                    
                    if validation_result['valid']:
                        results['valid_accounts'] += 1
                        
                        if not validate_only:
                            # Import the account
                            imported_account = self._import_account(validation_result['account_data'])
                            results['imported_accounts'].append(imported_account)
                    else:
                        results['invalid_accounts'] += 1
                        results['errors'].extend(validation_result['errors'])
                
                except Exception as e:
                    results['invalid_accounts'] += 1
                    results['errors'].append(f"Account {account_num}: Unexpected error - {str(e)}")
        
        except json.JSONDecodeError as e:
            results['errors'].append(f"Invalid JSON format: {str(e)}")
        
        return results
    
    def _validate_transaction_row(self, row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """Validate a single transaction row from CSV"""
        errors = []
        transaction_data = {}
        
        # Required fields
        required_fields = ['date', 'account', 'transaction_type', 'amount']
        for field in required_fields:
            if field not in row or not row[field].strip():
                errors.append(f"Row {row_num}: Missing required field '{field}'")
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        try:
            # Validate and parse date
            date_str = row['date'].strip()
            transaction_data['date'] = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # Try alternative date format
                transaction_data['date'] = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append(f"Row {row_num}: Invalid date format '{date_str}'. Expected YYYY-MM-DD HH:MM:SS or YYYY-MM-DD")
        
        # Validate account exists
        account_name = row['account'].strip()
        account = self.user.get_account(account_name)
        if not account:
            errors.append(f"Row {row_num}: Account '{account_name}' not found")
        else:
            transaction_data['account'] = account
        
        # Validate transaction type
        valid_types = ['deposit', 'withdrawal', 'interest', 'transfer']
        transaction_type = row['transaction_type'].strip().lower()
        if transaction_type not in valid_types:
            errors.append(f"Row {row_num}: Invalid transaction type '{transaction_type}'. Must be one of: {valid_types}")
        else:
            transaction_data['transaction_type'] = transaction_type
        
        # Validate amount
        try:
            amount = float(row['amount'].strip())
            if amount <= 0:
                errors.append(f"Row {row_num}: Amount must be positive, got {amount}")
            else:
                transaction_data['amount'] = amount
        except ValueError:
            errors.append(f"Row {row_num}: Invalid amount '{row['amount']}'. Must be a number")
        
        # Optional fields
        transaction_data['memo'] = row.get('memo', '').strip()
        transaction_data['transfer_id'] = row.get('transfer_id', '').strip()
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'transaction_data': transaction_data if len(errors) == 0 else None
        }
    
    def _validate_account_data(self, account_data: Dict[str, Any], account_num: int) -> Dict[str, Any]:
        """Validate account data from JSON"""
        errors = []
        validated_data = {}
        
        # Required fields
        required_fields = ['account_type', 'balance']
        for field in required_fields:
            if field not in account_data:
                errors.append(f"Account {account_num}: Missing required field '{field}'")
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        # Validate account type
        valid_types = ['savings', 'current', 'salary']
        account_type = account_data['account_type']
        if account_type not in valid_types:
            errors.append(f"Account {account_num}: Invalid account type '{account_type}'. Must be one of: {valid_types}")
        else:
            validated_data['account_type'] = account_type
        
        # Check if account type already exists
        existing_account = self.user.get_account(account_type)
        if existing_account:
            errors.append(f"Account {account_num}: Account type '{account_type}' already exists")
        
        # Validate balance
        try:
            balance = float(account_data['balance'])
            validated_data['balance'] = balance
        except (ValueError, TypeError):
            errors.append(f"Account {account_num}: Invalid balance '{account_data['balance']}'. Must be a number")
        
        # Optional fields with validation
        validated_data['nickname'] = account_data.get('nickname')
        
        # Validate overdraft limit
        overdraft_limit = account_data.get('overdraft_limit', 0)
        try:
            validated_data['overdraft_limit'] = float(overdraft_limit)
        except (ValueError, TypeError):
            errors.append(f"Account {account_num}: Invalid overdraft_limit '{overdraft_limit}'. Must be a number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'account_data': validated_data if len(errors) == 0 else None
        }
    
    def _import_transaction(self, transaction_data: Dict[str, Any]) -> None:
        """Import a validated transaction"""
        from src.core.transaction import Transaction
        
        account = transaction_data['account']
        
        # Create transaction
        transaction = Transaction(
            transaction_data['amount'],
            transaction_data['transaction_type'],
            transaction_data['date']
        )
        
        # Add memo if provided
        if transaction_data.get('memo'):
            transaction.memo = transaction_data['memo']
        
        # Add to account
        account.transactions.append(transaction)
        
        # Update account balance (simplified - in real system this would be more complex)
        if transaction_data['transaction_type'] in ['deposit', 'interest']:
            account.balance += transaction_data['amount']
        elif transaction_data['transaction_type'] == 'withdrawal':
            account.balance -= transaction_data['amount']
        
        account.update_activity()
    
    def _import_account(self, account_data: Dict[str, Any]) -> str:
        """Import a validated account"""
        from src.core.account import Account
        
        # Create account
        account = Account(
            account_data['account_type'],
            account_data['balance'],
            account_data['overdraft_limit'],
            account_data['nickname']
        )
        
        # Add to user
        self.user.accounts.append(account)
        
        return account.get_display_name()


class DataExportImportManager:
    """Main manager class for data export/import operations"""
    
    def __init__(self, user):
        self.user = user
        self.exporter = DataExporter(user)
        self.importer = DataImporter(user)
    
    def export_data(self, data_type: str, format: str, **kwargs) -> str:
        """
        Export data with specified type and format
        
        Args:
            data_type: 'transactions', 'accounts', or 'full_backup'
            format: 'csv' or 'json'
            **kwargs: Additional arguments for specific export types
            
        Returns:
            Path to exported file
        """
        if data_type == 'transactions':
            if format == 'csv':
                return self.exporter.export_transactions_csv(**kwargs)
            else:
                raise ValueError(f"Unsupported format '{format}' for transactions. Use 'csv'")
        
        elif data_type == 'accounts':
            if format == 'json':
                return self.exporter.export_accounts_json(**kwargs)
            else:
                raise ValueError(f"Unsupported format '{format}' for accounts. Use 'json'")
        
        elif data_type == 'full_backup':
            if format == 'json':
                return self.exporter.export_full_backup(**kwargs)
            else:
                raise ValueError(f"Unsupported format '{format}' for full backup. Use 'json'")
        
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def import_data(self, data_type: str, filepath: str, validate_only: bool = False) -> Dict[str, Any]:
        """
        Import data from file with validation
        
        Args:
            data_type: 'transactions' or 'accounts'
            filepath: Path to import file
            validate_only: If True, only validate without importing
            
        Returns:
            Import results dictionary
        """
        if data_type == 'transactions':
            return self.importer.import_transactions_csv(filepath, validate_only)
        elif data_type == 'accounts':
            return self.importer.import_accounts_json(filepath, validate_only)
        else:
            raise ValueError(f"Unsupported import data type: {data_type}")
    
    def get_export_formats(self, data_type: str) -> List[str]:
        """Get supported export formats for a data type"""
        formats = {
            'transactions': ['csv'],
            'accounts': ['json'],
            'full_backup': ['json']
        }
        return formats.get(data_type, [])
    
    def get_import_formats(self, data_type: str) -> List[str]:
        """Get supported import formats for a data type"""
        formats = {
            'transactions': ['csv'],
            'accounts': ['json']
        }
        return formats.get(data_type, [])