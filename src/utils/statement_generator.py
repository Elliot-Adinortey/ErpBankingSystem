"""
Statement Generator Module

This module handles the generation of account statements with formatted output
and export capabilities to various formats including text and PDF.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
from io import StringIO


class StatementGenerator:
    """Generates formatted account statements with transaction details"""
    
    def __init__(self, user):
        self.user = user
    
    def generate_statement(self, account_identifier: str, start_date: datetime = None, 
                          end_date: datetime = None, format: str = 'text') -> Dict[str, Any]:
        """
        Generate account statement for specified period
        
        Args:
            account_identifier: Account type or nickname
            start_date: Statement start date (defaults to 30 days ago)
            end_date: Statement end date (defaults to today)
            format: Output format ('text' or 'pdf')
            
        Returns:
            Dictionary containing statement data and formatted content
        """
        # Get account
        account = self.user.get_account(account_identifier)
        if not account:
            raise ValueError(f"Account '{account_identifier}' not found")
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get transactions for the period
        transactions = self._get_transactions_for_period(account, start_date, end_date)
        
        # Calculate statement data
        statement_data = self._calculate_statement_data(account, transactions, start_date, end_date)
        
        # Generate formatted content
        if format.lower() == 'text':
            formatted_content = self._format_text_statement(statement_data)
        elif format.lower() == 'pdf':
            formatted_content = self._format_pdf_statement(statement_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return {
            'account': account,
            'statement_data': statement_data,
            'formatted_content': formatted_content,
            'format': format,
            'generated_at': datetime.now()
        }
    
    def _get_transactions_for_period(self, account, start_date: datetime, end_date: datetime) -> List:
        """Get transactions within the specified date range"""
        transactions = []
        
        for transaction in account.transactions:
            if start_date <= transaction.date <= end_date:
                transactions.append(transaction)
        
        # Sort by date
        transactions.sort(key=lambda x: x.date)
        return transactions
    
    def _calculate_statement_data(self, account, transactions: List, start_date: datetime, 
                                 end_date: datetime) -> Dict[str, Any]:
        """Calculate statement summary data"""
        # Get opening balance (balance at start of period)
        opening_balance = self._calculate_opening_balance(account, transactions, start_date)
        
        # Calculate transaction totals
        total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
        total_withdrawals = sum(abs(t.amount) for t in transactions if t.transaction_type == 'withdrawal')
        total_interest = sum(t.amount for t in transactions if t.transaction_type == 'interest')
        
        # Calculate transfer totals
        transfer_in = sum(t.amount for t in transactions 
                         if hasattr(t, 'is_outgoing') and not t.is_outgoing)
        transfer_out = sum(abs(t.amount) for t in transactions 
                          if hasattr(t, 'is_outgoing') and t.is_outgoing)
        
        # Current balance
        closing_balance = account.balance
        
        return {
            'account_info': {
                'type': account.account_type,
                'nickname': account.nickname,
                'display_name': account.get_display_name(),
                'overdraft_limit': account.overdraft_limit,
                'created_date': account.created_date
            },
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'balances': {
                'opening_balance': opening_balance,
                'closing_balance': closing_balance,
                'available_balance': closing_balance + (account.overdraft_limit if account.account_type == 'current' else 0)
            },
            'transaction_summary': {
                'total_transactions': len(transactions),
                'total_deposits': total_deposits,
                'total_withdrawals': total_withdrawals,
                'total_interest': total_interest,
                'transfer_in': transfer_in,
                'transfer_out': transfer_out,
                'net_change': closing_balance - opening_balance
            },
            'transactions': transactions,
            'user_info': {
                'username': self.user.username,
                'email': self.user.email
            }
        }
    
    def _calculate_opening_balance(self, account, transactions: List, start_date: datetime) -> float:
        """Calculate account balance at the start of the statement period"""
        current_balance = account.balance
        
        # Subtract all transactions that occurred during the statement period
        for transaction in transactions:
            if transaction.transaction_type == 'deposit' or transaction.transaction_type == 'interest':
                current_balance -= transaction.amount
            elif transaction.transaction_type == 'withdrawal':
                current_balance += abs(transaction.amount)
            elif hasattr(transaction, 'is_outgoing'):
                if transaction.is_outgoing:
                    current_balance += abs(transaction.amount)
                else:
                    current_balance -= transaction.amount
        
        return current_balance
    
    def _format_text_statement(self, statement_data: Dict[str, Any]) -> str:
        """Format statement as text"""
        output = StringIO()
        
        # Header
        output.write("=" * 80 + "\n")
        output.write("ACCOUNT STATEMENT\n")
        output.write("=" * 80 + "\n\n")
        
        # Account Information
        account_info = statement_data['account_info']
        output.write("ACCOUNT INFORMATION\n")
        output.write("-" * 40 + "\n")
        output.write(f"Account: {account_info['display_name']}\n")
        output.write(f"Account Type: {account_info['type'].capitalize()}\n")
        if account_info['nickname']:
            output.write(f"Nickname: {account_info['nickname']}\n")
        output.write(f"Account Opened: {account_info['created_date'].strftime('%Y-%m-%d')}\n")
        if account_info['overdraft_limit'] > 0:
            output.write(f"Overdraft Limit: ${account_info['overdraft_limit']:.2f}\n")
        output.write("\n")
        
        # User Information
        user_info = statement_data['user_info']
        output.write("ACCOUNT HOLDER\n")
        output.write("-" * 40 + "\n")
        output.write(f"Name: {user_info['username']}\n")
        output.write(f"Email: {user_info['email']}\n")
        output.write("\n")
        
        # Statement Period
        period = statement_data['period']
        output.write("STATEMENT PERIOD\n")
        output.write("-" * 40 + "\n")
        output.write(f"From: {period['start_date'].strftime('%Y-%m-%d')}\n")
        output.write(f"To: {period['end_date'].strftime('%Y-%m-%d')}\n")
        output.write("\n")
        
        # Balance Summary
        balances = statement_data['balances']
        output.write("BALANCE SUMMARY\n")
        output.write("-" * 40 + "\n")
        output.write(f"Opening Balance: ${balances['opening_balance']:.2f}\n")
        output.write(f"Closing Balance: ${balances['closing_balance']:.2f}\n")
        output.write(f"Available Balance: ${balances['available_balance']:.2f}\n")
        output.write("\n")
        
        # Transaction Summary
        summary = statement_data['transaction_summary']
        output.write("TRANSACTION SUMMARY\n")
        output.write("-" * 40 + "\n")
        output.write(f"Total Transactions: {summary['total_transactions']}\n")
        output.write(f"Total Deposits: ${summary['total_deposits']:.2f}\n")
        output.write(f"Total Withdrawals: ${summary['total_withdrawals']:.2f}\n")
        if summary['total_interest'] > 0:
            output.write(f"Interest Earned: ${summary['total_interest']:.2f}\n")
        if summary['transfer_in'] > 0:
            output.write(f"Transfers In: ${summary['transfer_in']:.2f}\n")
        if summary['transfer_out'] > 0:
            output.write(f"Transfers Out: ${summary['transfer_out']:.2f}\n")
        output.write(f"Net Change: ${summary['net_change']:.2f}\n")
        output.write("\n")
        
        # Transaction Details
        transactions = statement_data['transactions']
        if transactions:
            output.write("TRANSACTION DETAILS\n")
            output.write("-" * 80 + "\n")
            output.write(f"{'Date':<12} {'Type':<12} {'Amount':<12} {'Balance':<12} {'Details':<20}\n")
            output.write("-" * 80 + "\n")
            
            running_balance = balances['opening_balance']
            
            for transaction in transactions:
                # Calculate running balance
                if transaction.transaction_type in ['deposit', 'interest']:
                    running_balance += transaction.amount
                elif transaction.transaction_type == 'withdrawal':
                    running_balance -= abs(transaction.amount)
                elif hasattr(transaction, 'is_outgoing'):
                    if transaction.is_outgoing:
                        running_balance -= abs(transaction.amount)
                    else:
                        running_balance += transaction.amount
                
                # Format transaction details
                details = ""
                if hasattr(transaction, 'memo') and transaction.memo:
                    details = transaction.memo
                elif hasattr(transaction, 'transfer_id'):
                    details = f"Transfer ID: {transaction.transfer_id}"
                
                output.write(f"{transaction.date.strftime('%Y-%m-%d'):<12} "
                           f"{transaction.transaction_type.capitalize():<12} "
                           f"${transaction.amount:.2f}{'':>6} "
                           f"${running_balance:.2f}{'':>6} "
                           f"{details:<20}\n")
        else:
            output.write("No transactions found for this period.\n")
        
        output.write("\n")
        output.write("=" * 80 + "\n")
        output.write(f"Statement generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("=" * 80 + "\n")
        
        return output.getvalue()
    
    def _format_pdf_statement(self, statement_data: Dict[str, Any]) -> str:
        """Format statement for PDF generation (returns HTML-like markup)"""
        # For now, return a structured format that could be converted to PDF
        # In a real implementation, this would use a PDF library like reportlab
        
        output = StringIO()
        
        # HTML-like structure for PDF conversion
        output.write("<html><head><title>Account Statement</title></head><body>\n")
        output.write("<h1>Account Statement</h1>\n")
        
        # Account Information
        account_info = statement_data['account_info']
        output.write("<h2>Account Information</h2>\n")
        output.write(f"<p><strong>Account:</strong> {account_info['display_name']}</p>\n")
        output.write(f"<p><strong>Account Type:</strong> {account_info['type'].capitalize()}</p>\n")
        if account_info['nickname']:
            output.write(f"<p><strong>Nickname:</strong> {account_info['nickname']}</p>\n")
        output.write(f"<p><strong>Account Opened:</strong> {account_info['created_date'].strftime('%Y-%m-%d')}</p>\n")
        
        # User Information
        user_info = statement_data['user_info']
        output.write("<h2>Account Holder</h2>\n")
        output.write(f"<p><strong>Name:</strong> {user_info['username']}</p>\n")
        output.write(f"<p><strong>Email:</strong> {user_info['email']}</p>\n")
        
        # Statement Period
        period = statement_data['period']
        output.write("<h2>Statement Period</h2>\n")
        output.write(f"<p><strong>From:</strong> {period['start_date'].strftime('%Y-%m-%d')}</p>\n")
        output.write(f"<p><strong>To:</strong> {period['end_date'].strftime('%Y-%m-%d')}</p>\n")
        
        # Balance Summary
        balances = statement_data['balances']
        output.write("<h2>Balance Summary</h2>\n")
        output.write("<table border='1'>\n")
        output.write(f"<tr><td>Opening Balance</td><td>${balances['opening_balance']:.2f}</td></tr>\n")
        output.write(f"<tr><td>Closing Balance</td><td>${balances['closing_balance']:.2f}</td></tr>\n")
        output.write(f"<tr><td>Available Balance</td><td>${balances['available_balance']:.2f}</td></tr>\n")
        output.write("</table>\n")
        
        # Transaction Summary
        summary = statement_data['transaction_summary']
        output.write("<h2>Transaction Summary</h2>\n")
        output.write("<table border='1'>\n")
        output.write(f"<tr><td>Total Transactions</td><td>{summary['total_transactions']}</td></tr>\n")
        output.write(f"<tr><td>Total Deposits</td><td>${summary['total_deposits']:.2f}</td></tr>\n")
        output.write(f"<tr><td>Total Withdrawals</td><td>${summary['total_withdrawals']:.2f}</td></tr>\n")
        if summary['total_interest'] > 0:
            output.write(f"<tr><td>Interest Earned</td><td>${summary['total_interest']:.2f}</td></tr>\n")
        output.write(f"<tr><td>Net Change</td><td>${summary['net_change']:.2f}</td></tr>\n")
        output.write("</table>\n")
        
        # Transaction Details
        transactions = statement_data['transactions']
        if transactions:
            output.write("<h2>Transaction Details</h2>\n")
            output.write("<table border='1'>\n")
            output.write("<tr><th>Date</th><th>Type</th><th>Amount</th><th>Balance</th><th>Details</th></tr>\n")
            
            running_balance = balances['opening_balance']
            
            for transaction in transactions:
                # Calculate running balance
                if transaction.transaction_type in ['deposit', 'interest']:
                    running_balance += transaction.amount
                elif transaction.transaction_type == 'withdrawal':
                    running_balance -= abs(transaction.amount)
                elif hasattr(transaction, 'is_outgoing'):
                    if transaction.is_outgoing:
                        running_balance -= abs(transaction.amount)
                    else:
                        running_balance += transaction.amount
                
                # Format transaction details
                details = ""
                if hasattr(transaction, 'memo') and transaction.memo:
                    details = transaction.memo
                elif hasattr(transaction, 'transfer_id'):
                    details = f"Transfer ID: {transaction.transfer_id}"
                
                output.write(f"<tr><td>{transaction.date.strftime('%Y-%m-%d')}</td>"
                           f"<td>{transaction.transaction_type.capitalize()}</td>"
                           f"<td>${transaction.amount:.2f}</td>"
                           f"<td>${running_balance:.2f}</td>"
                           f"<td>{details}</td></tr>\n")
            
            output.write("</table>\n")
        
        output.write(f"<p><em>Statement generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>\n")
        output.write("</body></html>\n")
        
        return output.getvalue()
    
    def export_statement_to_file(self, statement_result: Dict[str, Any], filename: str = None) -> str:
        """
        Export statement to file
        
        Args:
            statement_result: Result from generate_statement()
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to the exported file
        """
        if not filename:
            account_name = statement_result['account'].get_display_name().replace(' ', '_')
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            extension = 'txt' if statement_result['format'] == 'text' else 'html'
            filename = f"statement_{account_name}_{date_str}.{extension}"
        
        # Ensure statements directory exists
        statements_dir = "statements"
        if not os.path.exists(statements_dir):
            os.makedirs(statements_dir)
        
        filepath = os.path.join(statements_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(statement_result['formatted_content'])
        
        return filepath
    
    def generate_multi_account_statement(self, start_date: datetime = None, 
                                       end_date: datetime = None, format: str = 'text') -> Dict[str, Any]:
        """
        Generate consolidated statement for all user accounts
        
        Args:
            start_date: Statement start date
            end_date: Statement end date
            format: Output format
            
        Returns:
            Dictionary containing consolidated statement data
        """
        if not self.user.accounts:
            raise ValueError("No accounts found for user")
        
        # Set default date range
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Generate statements for all accounts
        account_statements = []
        total_opening_balance = 0
        total_closing_balance = 0
        total_transactions = 0
        
        for account in self.user.accounts:
            try:
                statement = self.generate_statement(account.account_type, start_date, end_date, format)
                account_statements.append(statement)
                
                # Aggregate totals
                total_opening_balance += statement['statement_data']['balances']['opening_balance']
                total_closing_balance += statement['statement_data']['balances']['closing_balance']
                total_transactions += statement['statement_data']['transaction_summary']['total_transactions']
                
            except Exception as e:
                # Continue with other accounts if one fails
                print(f"Warning: Could not generate statement for {account.get_display_name()}: {e}")
        
        # Create consolidated summary
        consolidated_data = {
            'user_info': {
                'username': self.user.username,
                'email': self.user.email
            },
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_accounts': len(account_statements),
                'total_opening_balance': total_opening_balance,
                'total_closing_balance': total_closing_balance,
                'total_net_change': total_closing_balance - total_opening_balance,
                'total_transactions': total_transactions
            },
            'account_statements': account_statements
        }
        
        # Generate consolidated formatted content
        if format.lower() == 'text':
            formatted_content = self._format_consolidated_text_statement(consolidated_data)
        else:
            formatted_content = self._format_consolidated_pdf_statement(consolidated_data)
        
        return {
            'consolidated_data': consolidated_data,
            'formatted_content': formatted_content,
            'format': format,
            'generated_at': datetime.now()
        }
    
    def _format_consolidated_text_statement(self, consolidated_data: Dict[str, Any]) -> str:
        """Format consolidated statement as text"""
        output = StringIO()
        
        # Header
        output.write("=" * 80 + "\n")
        output.write("CONSOLIDATED ACCOUNT STATEMENT\n")
        output.write("=" * 80 + "\n\n")
        
        # User Information
        user_info = consolidated_data['user_info']
        output.write("ACCOUNT HOLDER\n")
        output.write("-" * 40 + "\n")
        output.write(f"Name: {user_info['username']}\n")
        output.write(f"Email: {user_info['email']}\n")
        output.write("\n")
        
        # Statement Period
        period = consolidated_data['period']
        output.write("STATEMENT PERIOD\n")
        output.write("-" * 40 + "\n")
        output.write(f"From: {period['start_date'].strftime('%Y-%m-%d')}\n")
        output.write(f"To: {period['end_date'].strftime('%Y-%m-%d')}\n")
        output.write("\n")
        
        # Consolidated Summary
        summary = consolidated_data['summary']
        output.write("CONSOLIDATED SUMMARY\n")
        output.write("-" * 40 + "\n")
        output.write(f"Total Accounts: {summary['total_accounts']}\n")
        output.write(f"Total Opening Balance: ${summary['total_opening_balance']:.2f}\n")
        output.write(f"Total Closing Balance: ${summary['total_closing_balance']:.2f}\n")
        output.write(f"Total Net Change: ${summary['total_net_change']:.2f}\n")
        output.write(f"Total Transactions: {summary['total_transactions']}\n")
        output.write("\n")
        
        # Individual Account Summaries
        output.write("ACCOUNT BREAKDOWN\n")
        output.write("-" * 80 + "\n")
        output.write(f"{'Account':<25} {'Opening':<12} {'Closing':<12} {'Change':<12} {'Transactions':<12}\n")
        output.write("-" * 80 + "\n")
        
        for statement in consolidated_data['account_statements']:
            account_data = statement['statement_data']
            account_name = account_data['account_info']['display_name']
            opening = account_data['balances']['opening_balance']
            closing = account_data['balances']['closing_balance']
            change = account_data['transaction_summary']['net_change']
            tx_count = account_data['transaction_summary']['total_transactions']
            
            output.write(f"{account_name:<25} ${opening:<11.2f} ${closing:<11.2f} "
                        f"${change:<11.2f} {tx_count:<12}\n")
        
        output.write("\n")
        output.write("=" * 80 + "\n")
        output.write(f"Consolidated statement generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("=" * 80 + "\n")
        
        return output.getvalue()
    
    def _format_consolidated_pdf_statement(self, consolidated_data: Dict[str, Any]) -> str:
        """Format consolidated statement for PDF"""
        # Similar to individual PDF format but for consolidated data
        output = StringIO()
        
        output.write("<html><head><title>Consolidated Account Statement</title></head><body>\n")
        output.write("<h1>Consolidated Account Statement</h1>\n")
        
        # User Information
        user_info = consolidated_data['user_info']
        output.write("<h2>Account Holder</h2>\n")
        output.write(f"<p><strong>Name:</strong> {user_info['username']}</p>\n")
        output.write(f"<p><strong>Email:</strong> {user_info['email']}</p>\n")
        
        # Statement Period
        period = consolidated_data['period']
        output.write("<h2>Statement Period</h2>\n")
        output.write(f"<p><strong>From:</strong> {period['start_date'].strftime('%Y-%m-%d')}</p>\n")
        output.write(f"<p><strong>To:</strong> {period['end_date'].strftime('%Y-%m-%d')}</p>\n")
        
        # Consolidated Summary
        summary = consolidated_data['summary']
        output.write("<h2>Consolidated Summary</h2>\n")
        output.write("<table border='1'>\n")
        output.write(f"<tr><td>Total Accounts</td><td>{summary['total_accounts']}</td></tr>\n")
        output.write(f"<tr><td>Total Opening Balance</td><td>${summary['total_opening_balance']:.2f}</td></tr>\n")
        output.write(f"<tr><td>Total Closing Balance</td><td>${summary['total_closing_balance']:.2f}</td></tr>\n")
        output.write(f"<tr><td>Total Net Change</td><td>${summary['total_net_change']:.2f}</td></tr>\n")
        output.write(f"<tr><td>Total Transactions</td><td>{summary['total_transactions']}</td></tr>\n")
        output.write("</table>\n")
        
        # Account Breakdown
        output.write("<h2>Account Breakdown</h2>\n")
        output.write("<table border='1'>\n")
        output.write("<tr><th>Account</th><th>Opening Balance</th><th>Closing Balance</th><th>Net Change</th><th>Transactions</th></tr>\n")
        
        for statement in consolidated_data['account_statements']:
            account_data = statement['statement_data']
            account_name = account_data['account_info']['display_name']
            opening = account_data['balances']['opening_balance']
            closing = account_data['balances']['closing_balance']
            change = account_data['transaction_summary']['net_change']
            tx_count = account_data['transaction_summary']['total_transactions']
            
            output.write(f"<tr><td>{account_name}</td><td>${opening:.2f}</td><td>${closing:.2f}</td>"
                        f"<td>${change:.2f}</td><td>{tx_count}</td></tr>\n")
        
        output.write("</table>\n")
        
        output.write(f"<p><em>Consolidated statement generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>\n")
        output.write("</body></html>\n")
        
        return output.getvalue()