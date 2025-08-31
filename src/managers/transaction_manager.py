from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import math


class TransactionManager:
    """Manages transaction history operations including filtering and pagination"""
    
    def __init__(self, user):
        self.user = user
    
    def get_transaction_history(self, account: str = None, start_date: datetime = None, 
                              end_date: datetime = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        Get transaction history with optional filtering and pagination
        
        Args:
            account: Account identifier (type or nickname), None for all accounts
            start_date: Start date for filtering
            end_date: End date for filtering  
            page: Page number (1-based)
            page_size: Number of transactions per page
            
        Returns:
            Dict containing transactions, pagination info, and metadata
        """
        all_transactions = []
        
        # Collect transactions from specified account(s)
        if account:
            target_account = self.user.get_account(account)
            if not target_account:
                return {
                    'transactions': [],
                    'total_count': 0,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': 0,
                    'error': f"Account '{account}' not found"
                }
            accounts_to_check = [target_account]
        else:
            accounts_to_check = self.user.accounts
        
        # Collect all transactions with account context
        for acc in accounts_to_check:
            for transaction in acc.transaction_history:
                transaction_data = {
                    'account': acc.get_display_name(),
                    'account_type': acc.account_type,
                    'amount': transaction.amount,
                    'type': transaction.transaction_type,
                    'date': transaction.date,
                    'transaction_obj': transaction  # Keep reference for additional data
                }
                all_transactions.append(transaction_data)
        
        # Apply date filtering
        filtered_transactions = self._filter_by_date_range(all_transactions, start_date, end_date)
        
        # Sort by date (newest first)
        filtered_transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Apply pagination
        total_count = len(filtered_transactions)
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_transactions = filtered_transactions[start_idx:end_idx]
        
        return {
            'transactions': paginated_transactions,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }
    
    def filter_transactions(self, transactions: List[Dict], filters: Dict) -> List[Dict]:
        """
        Apply various filters to transaction list
        
        Args:
            transactions: List of transaction dictionaries
            filters: Dictionary containing filter criteria
                - transaction_types: List of transaction types to include
                - min_amount: Minimum transaction amount
                - max_amount: Maximum transaction amount
                - account_types: List of account types to include
                
        Returns:
            Filtered list of transactions
        """
        filtered = transactions.copy()
        
        # Filter by transaction type
        if 'transaction_types' in filters and filters['transaction_types']:
            filtered = [t for t in filtered if t['type'] in filters['transaction_types']]
        
        # Filter by amount range
        if 'min_amount' in filters and filters['min_amount'] is not None:
            filtered = [t for t in filtered if abs(t['amount']) >= filters['min_amount']]
        
        if 'max_amount' in filters and filters['max_amount'] is not None:
            filtered = [t for t in filtered if abs(t['amount']) <= filters['max_amount']]
        
        # Filter by account type
        if 'account_types' in filters and filters['account_types']:
            filtered = [t for t in filtered if t['account_type'] in filters['account_types']]
        
        return filtered
    
    def _filter_by_date_range(self, transactions: List[Dict], start_date: datetime = None, 
                             end_date: datetime = None) -> List[Dict]:
        """Filter transactions by date range"""
        if not start_date and not end_date:
            return transactions
        
        filtered = []
        for transaction in transactions:
            transaction_date = transaction['date']
            
            # Check start date
            if start_date and transaction_date < start_date:
                continue
            
            # Check end date (inclusive - end of day)
            if end_date:
                end_of_day = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                if transaction_date > end_of_day:
                    continue
            
            filtered.append(transaction)
        
        return filtered
    
    def get_transaction_summary(self, account: str = None, start_date: datetime = None, 
                               end_date: datetime = None) -> Dict[str, Any]:
        """
        Get summary statistics for transactions
        
        Returns:
            Dictionary with transaction summary statistics
        """
        history_result = self.get_transaction_history(
            account=account, 
            start_date=start_date, 
            end_date=end_date,
            page=1,
            page_size=10000  # Get all for summary
        )
        
        transactions = history_result['transactions']
        
        if not transactions:
            return {
                'total_transactions': 0,
                'total_deposits': 0,
                'total_withdrawals': 0,
                'total_transfers_in': 0,
                'total_transfers_out': 0,
                'net_change': 0,
                'date_range': None
            }
        
        # Calculate summary statistics
        total_deposits = sum(t['amount'] for t in transactions if t['type'] == 'deposit')
        total_withdrawals = sum(abs(t['amount']) for t in transactions if t['type'] == 'withdrawal')
        total_transfers_in = sum(t['amount'] for t in transactions if t['type'] == 'transfer' and t['amount'] > 0)
        total_transfers_out = sum(abs(t['amount']) for t in transactions if t['type'] == 'transfer' and t['amount'] < 0)
        
        net_change = total_deposits + total_transfers_in - total_withdrawals - total_transfers_out
        
        # Get date range
        dates = [t['date'] for t in transactions]
        date_range = {
            'start': min(dates),
            'end': max(dates)
        } if dates else None
        
        return {
            'total_transactions': len(transactions),
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'total_transfers_in': total_transfers_in,
            'total_transfers_out': total_transfers_out,
            'net_change': net_change,
            'date_range': date_range
        }
    
    def export_transactions(self, transactions: List[Dict], format: str = 'csv') -> str:
        """
        Export transactions to specified format
        
        Args:
            transactions: List of transaction dictionaries
            format: Export format ('csv' or 'json')
            
        Returns:
            Formatted string ready for file output
        """
        if format.lower() == 'csv':
            return self._export_to_csv(transactions)
        elif format.lower() == 'json':
            return self._export_to_json(transactions)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_csv(self, transactions: List[Dict]) -> str:
        """Export transactions to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Account', 'Account Type', 'Transaction Type', 'Amount'])
        
        # Write transaction data
        for transaction in transactions:
            writer.writerow([
                transaction['date'].strftime('%Y-%m-%d %H:%M:%S'),
                transaction['account'],
                transaction['account_type'],
                transaction['type'],
                transaction['amount']
            ])
        
        return output.getvalue()
    
    def _export_to_json(self, transactions: List[Dict]) -> str:
        """Export transactions to JSON format"""
        import json
        
        # Prepare data for JSON serialization
        json_data = []
        for transaction in transactions:
            json_data.append({
                'date': transaction['date'].strftime('%Y-%m-%d %H:%M:%S'),
                'account': transaction['account'],
                'account_type': transaction['account_type'],
                'transaction_type': transaction['type'],
                'amount': transaction['amount']
            })
        
        return json.dumps(json_data, indent=2)