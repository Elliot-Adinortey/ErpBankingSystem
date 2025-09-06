import argparse
import os
import sys
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.user import register_user, login_user, User
from src.core.account import Account
from src.utils.password_reset import initiate_password_reset, reset_password
from src.utils.data_storage import save_users_to_file, load_users_from_file
from src.utils.security_utils import SessionManager
from src.ui.interactive_session import start_interactive_session
from src.utils.help_system import HelpSystem
from src.utils.error_handler import ErrorHandler
from src.utils.statement_generator import StatementGenerator
from src.utils.data_export_import import DataExportImportManager
from src.utils.audit_logger import get_audit_logger, AuditEventType
from src.managers.batch_manager import BatchManager

# Initialize the global user dictionary
users = load_users_from_file()

# Clean up expired sessions on startup
SessionManager.cleanup_expired_sessions()

def register(args):
    register_user(users, args.username, args.password, args.email)
    save_users_to_file(users)

def login(args):
    # Clean up expired sessions first
    SessionManager.cleanup_expired_sessions()
    
    # Get audit logger
    audit_logger = get_audit_logger()
    
    user = login_user(users, args.username, args.password)
    if user:
        # Create session token
        token = SessionManager.create_session(args.username)
        
        # Log successful login
        audit_logger.log_login_attempt(
            username=args.username,
            success=True,
            session_id=token
        )
        
        print(f"Login successful for {args.username}")
        print(f"Session token: {token}")
        print("Use this token for subsequent operations or save it to SESSION_TOKEN environment variable")
        
        # Optionally save to environment file for convenience
        with open('.session', 'w') as f:
            f.write(token)
        print("Session token saved to .session file")
    else:
        # Log failed login
        audit_logger.log_login_attempt(
            username=args.username,
            success=False,
            failure_reason="Invalid credentials"
        )
        print("Login failed")

def add_account(args):
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        try:
            account = Account(args.type, balance=float(args.balance), overdraft_limit=args.overdraft_limit)
            user.add_account(account)
            save_users_to_file(users)
            
            # Log successful account creation
            audit_logger.log_banking_operation(
                operation_type="account_create",
                user=user.username,
                account_identifier=args.type,
                success=True,
                session_id=get_session_token(args),
                additional_details={
                    "initial_balance": float(args.balance),
                    "overdraft_limit": args.overdraft_limit
                }
            )
        except Exception as e:
            # Log failed account creation
            audit_logger.log_banking_operation(
                operation_type="account_create",
                user=user.username,
                account_identifier=args.type,
                success=False,
                session_id=get_session_token(args),
                additional_details={
                    "error": str(e),
                    "attempted_balance": args.balance,
                    "attempted_overdraft": args.overdraft_limit
                }
            )
            raise
    # Error message already printed by authenticate_user

def deposit(args):
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        account = user.get_account(args.type)
        if account:
            try:
                old_balance = account.balance
                account.deposit(args.amount)
                save_users_to_file(users)
                
                # Log successful deposit
                audit_logger.log_banking_operation(
                    operation_type="deposit",
                    user=user.username,
                    account_identifier=args.type,
                    amount=args.amount,
                    success=True,
                    session_id=get_session_token(args),
                    additional_details={
                        "old_balance": old_balance,
                        "new_balance": account.balance
                    }
                )
            except Exception as e:
                # Log failed deposit
                audit_logger.log_banking_operation(
                    operation_type="deposit",
                    user=user.username,
                    account_identifier=args.type,
                    amount=args.amount,
                    success=False,
                    session_id=get_session_token(args),
                    additional_details={"error": str(e)}
                )
                raise
        else:
            # Log failed deposit due to account not found
            audit_logger.log_banking_operation(
                operation_type="deposit",
                user=user.username,
                account_identifier=args.type,
                amount=args.amount,
                success=False,
                session_id=get_session_token(args),
                additional_details={"error": "Account not found"}
            )

def withdraw(args):
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        account = user.get_account(args.type)
        if account:
            try:
                old_balance = account.balance
                account.withdraw(args.amount)
                save_users_to_file(users)
                
                # Log successful withdrawal
                audit_logger.log_banking_operation(
                    operation_type="withdrawal",
                    user=user.username,
                    account_identifier=args.type,
                    amount=args.amount,
                    success=True,
                    session_id=get_session_token(args),
                    additional_details={
                        "old_balance": old_balance,
                        "new_balance": account.balance
                    }
                )
            except Exception as e:
                # Log failed withdrawal
                audit_logger.log_banking_operation(
                    operation_type="withdrawal",
                    user=user.username,
                    account_identifier=args.type,
                    amount=args.amount,
                    success=False,
                    session_id=get_session_token(args),
                    additional_details={"error": str(e)}
                )
                raise
        else:
            # Log failed withdrawal due to account not found
            audit_logger.log_banking_operation(
                operation_type="withdrawal",
                user=user.username,
                account_identifier=args.type,
                amount=args.amount,
                success=False,
                session_id=get_session_token(args),
                additional_details={"error": "Account not found"}
            )

def view_balance(args):
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        account = user.get_account(args.type)
        if account:
            balance = account.get_balance()
            print(f"Balance: ${balance}")
            
            # Log balance inquiry
            audit_logger.log_banking_operation(
                operation_type="balance_inquiry",
                user=user.username,
                account_identifier=args.type,
                success=True,
                session_id=get_session_token(args),
                additional_details={"balance": balance}
            )
        else:
            # Log failed balance inquiry
            audit_logger.log_banking_operation(
                operation_type="balance_inquiry",
                user=user.username,
                account_identifier=args.type,
                success=False,
                session_id=get_session_token(args),
                additional_details={"error": "Account not found"}
            )

def reset_password_init(args):
    initiate_password_reset(users, args.username)

def reset_password_complete(args):
    reset_password(users, args.token, args.new_password)
    save_users_to_file(users)

def logout(args):
    """Logout and invalidate session"""
    token = get_session_token(args)
    audit_logger = get_audit_logger()
    
    if token:
        username = SessionManager.validate_session(token)
        if username and SessionManager.invalidate_session(token):
            # Log logout
            audit_logger.log_logout(
                username=username,
                session_id=token
            )
            
            # Remove session file
            if os.path.exists('.session'):
                os.remove('.session')
            print("Logged out successfully")
        else:
            print("No active session found")
    else:
        print("No active session found")

def status(args):
    """Check login status and session info"""
    token = get_session_token(args)
    if not token:
        print("Status: Not logged in")
        print("No session token found")
        return
    
    username = SessionManager.validate_session(token)
    if username:
        print(f"Status: Logged in as {username}")
        print(f"Session token: {token[:16]}...")
        
        # Show session expiry info
        sessions = SessionManager._load_sessions()
        if token in sessions:
            expiry = sessions[token]["expires"]
            print(f"Session expires: {expiry}")
    else:
        print("Status: Session expired")
        print("Please login again")

def list_accounts(args):
    """List all accounts for the logged in user"""
    user = authenticate_user(args)
    if user:
        if not user.accounts:
            print("No accounts found. Use 'add_account' to create one.")
            return
        
        print(f"\nAccounts for {user.username}:")
        print("-" * 40)
        
        total_balance = 0
        for account in user.accounts:
            balance = account.get_balance()
            total_balance += balance
            
            # Use display name (includes nickname if available)
            display_name = account.get_display_name()
            print(f"{display_name:>20}: ${balance:>10.2f}")
            if account.overdraft_limit > 0:
                print(f"{'':>20}  (Overdraft: ${account.overdraft_limit:.2f})")
        
        print("-" * 40)
        print(f"{'Total':>20}: ${total_balance:>10.2f}")
        print()

def account_summary(args):
    """Display comprehensive account summary with detailed information"""
    user = authenticate_user(args)
    if user:
        summary = user.get_enhanced_summary()
        
        if summary['total_accounts'] == 0:
            print("No accounts found. Use 'add_account' to create one.")
            return
        
        print(f"\n=== Account Summary for {user.username} ===")
        print(f"Total Accounts: {summary['total_accounts']}")
        print(f"Total Balance: ${summary['total_balance']:.2f}")
        print("=" * 60)
        
        for account_info in summary['accounts']:
            print(f"\nAccount: {account_info['display_name']}")
            print(f"  Type: {account_info['type'].capitalize()}")
            if account_info['nickname']:
                print(f"  Nickname: {account_info['nickname']}")
            print(f"  Balance: ${account_info['balance']:.2f}")
            if account_info['overdraft_limit'] > 0:
                print(f"  Overdraft Limit: ${account_info['overdraft_limit']:.2f}")
                print(f"  Available Balance: ${account_info['available_balance']:.2f}")
            print(f"  Transactions: {account_info['transaction_count']}")
            print(f"  Created: {account_info['created_date']}")
            print(f"  Last Activity: {account_info['last_activity']}")
        
        print("=" * 60)

def financial_overview(args):
    """Display financial overview with total balances and recent activity"""
    user = authenticate_user(args)
    if user:
        overview = user.get_financial_overview()
        
        if not user.accounts:
            print("No accounts found. Use 'add_account' to create one.")
            return
        
        print(f"\n=== Financial Overview for {user.username} ===")
        print(f"Total Balance: ${overview['total_balance']:.2f}")
        print(f"Total Available: ${overview['total_available']:.2f}")
        print("=" * 50)
        
        print("\nAccount Breakdown:")
        for account_name, details in overview['account_breakdown'].items():
            print(f"  {account_name}:")
            print(f"    Balance: ${details['balance']:.2f}")
            if details['available'] != details['balance']:
                print(f"    Available: ${details['available']:.2f}")
        
        if overview['recent_activity']:
            print("\nRecent Activity (Last 10 transactions):")
            print("-" * 50)
            for transaction in overview['recent_activity']:
                date_str = transaction['date'].strftime("%Y-%m-%d %H:%M")
                print(f"{date_str} | {transaction['account']:>15} | {transaction['type']:>10} | ${transaction['amount']:>8.2f}")
        else:
            print("\nNo recent activity found.")
        
        print("=" * 50)

def transfer(args):
    """Transfer money between user's accounts"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        # Validate and execute transfer
        success, message, transfer_id = user.transfer_between_accounts(
            args.from_account, args.to_account, args.amount, args.memo
        )
        
        # Log transfer attempt
        audit_logger.log_banking_operation(
            operation_type="transfer",
            user=user.username,
            account_identifier=f"{args.from_account} -> {args.to_account}",
            amount=args.amount,
            success=success,
            session_id=get_session_token(args),
            additional_details={
                "from_account": args.from_account,
                "to_account": args.to_account,
                "memo": args.memo,
                "transfer_id": transfer_id,
                "message": message
            }
        )
        
        if success:
            print(f"✓ {message}")
            
            # Show updated balances
            from_account = user.get_account(args.from_account)
            to_account = user.get_account(args.to_account)
            
            if from_account and to_account:
                print(f"\nUpdated Balances:")
                print(f"  {from_account.get_display_name()}: ${from_account.balance:.2f}")
                print(f"  {to_account.get_display_name()}: ${to_account.balance:.2f}")
            
            # Save changes
            from data_storage import save_users_to_file
            save_users_to_file(users)
        else:
            print(f"✗ Transfer failed: {message}")
            
            # Show available accounts for reference
            if "not found" in message.lower():
                print("\nAvailable accounts:")
                for account in user.accounts:
                    print(f"  - {account.get_display_name()}")

def transaction_history(args):
    """Display transaction history with filtering options"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        # Parse date arguments
        start_date = None
        end_date = None
        
        if args.start_date:
            try:
                start_date = parse_date_string(args.start_date)
            except ValueError as e:
                print(f"Error: Invalid start date format. {e}")
                return
        
        if args.end_date:
            try:
                end_date = parse_date_string(args.end_date)
            except ValueError as e:
                print(f"Error: Invalid end date format. {e}")
                return
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            print("Error: Start date cannot be after end date.")
            return
        
        # Get transaction history
        result = user.get_transaction_history(
            account=args.account,
            start_date=start_date,
            end_date=end_date,
            page=args.page,
            page_size=args.page_size
        )
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            return
        
        transactions = result['transactions']
        
        if not transactions:
            print("No transactions found for the specified criteria.")
            return
        
        # Apply additional filters if specified
        if args.type or args.min_amount is not None or args.max_amount is not None:
            filters = {}
            if args.type:
                filters['transaction_types'] = args.type
            if args.min_amount is not None:
                filters['min_amount'] = args.min_amount
            if args.max_amount is not None:
                filters['max_amount'] = args.max_amount
            
            transactions = user.filter_transactions(transactions, filters)
            
            if not transactions:
                print("No transactions found matching the specified filters.")
                return
        
        # Log transaction history access
        audit_logger.log_operation(
            event_type=AuditEventType.TRANSACTION_HISTORY,
            user=user.username,
            operation=f"Transaction history accessed - {len(transactions)} records",
            success=True,
            session_id=get_session_token(args),
            details={
                "account": args.account,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "page": args.page,
                "page_size": args.page_size,
                "filters_applied": bool(args.type or args.min_amount is not None or args.max_amount is not None),
                "record_count": len(transactions)
            }
        )
        
        # Display transactions
        display_transaction_history(transactions, result, args.sort_by, args.export_format)

def parse_date_string(date_str):
    """Parse date string in various formats"""
    from datetime import datetime
    
    # Try different date formats
    formats = [
        '%Y-%m-%d',           # 2024-01-15
        '%Y-%m-%d %H:%M',     # 2024-01-15 14:30
        '%Y-%m-%d %H:%M:%S',  # 2024-01-15 14:30:00
        '%m/%d/%Y',           # 01/15/2024
        '%d/%m/%Y',           # 15/01/2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date '{date_str}'. Supported formats: YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY")

def display_transaction_history(transactions, result_info, sort_by='date', export_format=None):
    """Display formatted transaction history"""
    
    # Sort transactions if requested
    if sort_by == 'amount':
        transactions.sort(key=lambda x: abs(x['amount']), reverse=True)
    elif sort_by == 'type':
        transactions.sort(key=lambda x: x['type'])
    elif sort_by == 'account':
        transactions.sort(key=lambda x: x['account'])
    # Default is already sorted by date (newest first)
    
    # Export if requested
    if export_format:
        from transaction_manager import TransactionManager
        manager = TransactionManager(None)  # We don't need user for export
        
        try:
            exported_data = manager.export_transactions(transactions, export_format)
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            
            with open(filename, 'w') as f:
                f.write(exported_data)
            
            print(f"Transactions exported to {filename}")
            return
        except Exception as e:
            print(f"Export failed: {e}")
            return
    
    # Display header
    print(f"\n=== Transaction History ===")
    if result_info['total_count'] > len(transactions):
        print(f"Showing {len(transactions)} of {result_info['total_count']} transactions")
    else:
        print(f"Total transactions: {result_info['total_count']}")
    
    if result_info['total_pages'] > 1:
        print(f"Page {result_info['page']} of {result_info['total_pages']}")
    
    print("=" * 80)
    
    # Display transactions
    print(f"{'Date':<20} {'Account':<20} {'Type':<12} {'Amount':<12}")
    print("-" * 80)
    
    for transaction in transactions:
        date_str = transaction['date'].strftime('%Y-%m-%d %H:%M:%S')
        account_name = transaction['account'][:18] + '..' if len(transaction['account']) > 20 else transaction['account']
        amount_str = f"${transaction['amount']:>8.2f}"
        
        print(f"{date_str:<20} {account_name:<20} {transaction['type']:<12} {amount_str:<12}")
    
    print("=" * 80)
    
    # Show pagination info
    if result_info['total_pages'] > 1:
        pagination_info = []
        if result_info['has_previous']:
            pagination_info.append(f"Previous: --page {result_info['page'] - 1}")
        if result_info['has_next']:
            pagination_info.append(f"Next: --page {result_info['page'] + 1}")
        
        if pagination_info:
            print(f"Navigation: {' | '.join(pagination_info)}")
    
    print()

def transaction_summary(args):
    """Display transaction summary statistics"""
    user = authenticate_user(args)
    if user:
        # Parse date arguments
        start_date = None
        end_date = None
        
        if args.start_date:
            try:
                start_date = parse_date_string(args.start_date)
            except ValueError as e:
                print(f"Error: Invalid start date format. {e}")
                return
        
        if args.end_date:
            try:
                end_date = parse_date_string(args.end_date)
            except ValueError as e:
                print(f"Error: Invalid end date format. {e}")
                return
        
        # Get summary
        summary = user.get_transaction_summary(
            account=args.account,
            start_date=start_date,
            end_date=end_date
        )
        
        # Display summary
        print(f"\n=== Transaction Summary ===")
        if args.account:
            account_obj = user.get_account(args.account)
            if account_obj:
                print(f"Account: {account_obj.get_display_name()}")
        else:
            print("All Accounts")
        
        if summary['date_range']:
            start_str = summary['date_range']['start'].strftime('%Y-%m-%d')
            end_str = summary['date_range']['end'].strftime('%Y-%m-%d')
            print(f"Period: {start_str} to {end_str}")
        
        print("=" * 40)
        print(f"Total Transactions: {summary['total_transactions']}")
        print(f"Total Deposits: ${summary['total_deposits']:.2f}")
        print(f"Total Withdrawals: ${summary['total_withdrawals']:.2f}")
        print(f"Total Transfers In: ${summary['total_transfers_in']:.2f}")
        print(f"Total Transfers Out: ${summary['total_transfers_out']:.2f}")
        print("-" * 40)
        print(f"Net Change: ${summary['net_change']:.2f}")
        print("=" * 40)

def interactive(args):
    """Start interactive banking session"""
    user = authenticate_user(args)
    if user:
        start_interactive_session(user, users)

def help_command(args):
    """Display detailed help for commands"""
    if args.command:
        # Show help for specific command
        help_text = HelpSystem.get_command_help(args.command, detailed=True)
        print(help_text)
    else:
        # Show general help
        print("🏦 Banking System - Command Help")
        print("=" * 60)
        print("Available commands:")
        print()
        
        commands = HelpSystem.get_all_commands()
        for command in sorted(commands):
            help_info = HelpSystem.COMMAND_HELP[command]
            print(f"  {command:<20} {help_info['description']}")

def generate_statement(args):
    """Generate account statement for specified period"""
    user = authenticate_user(args)
    if user:
        try:
            statement_generator = StatementGenerator(user)
            
            # Parse date arguments
            start_date = None
            end_date = None
            
            if args.start_date:
                start_date = parse_date_input(args.start_date)
            if args.end_date:
                end_date = parse_date_input(args.end_date)
            
            # Generate statement
            result = statement_generator.generate_statement(
                args.account, 
                start_date, 
                end_date, 
                args.format
            )
            
            if args.export:
                # Export to file
                filepath = statement_generator.export_statement_to_file(result, args.filename)
                print(f"Statement exported to: {filepath}")
            else:
                # Display statement
                print(result['formatted_content'])
                
        except ValueError as e:
            ErrorHandler.handle_invalid_account(str(e), [])
        except Exception as e:
            print(f"Error generating statement: {e}")

def export_data(args):
    """Export account or transaction data"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        try:
            export_manager = DataExportImportManager(user)
            
            # Prepare export arguments
            export_kwargs = {}
            if args.data_type == 'transactions':
                if args.account:
                    export_kwargs['account_identifier'] = args.account
                if args.start_date:
                    export_kwargs['start_date'] = parse_date_input(args.start_date)
                if args.end_date:
                    export_kwargs['end_date'] = parse_date_input(args.end_date)
            
            if args.filename:
                export_kwargs['filename'] = args.filename
            
            # Export data
            filepath = export_manager.export_data(args.data_type, args.format, **export_kwargs)
            
            # Log successful export
            audit_logger.log_operation(
                event_type=AuditEventType.DATA_EXPORT,
                user=user.username,
                operation=f"Data export: {args.data_type} ({args.format})",
                success=True,
                session_id=get_session_token(args),
                details={
                    "data_type": args.data_type,
                    "format": args.format,
                    "filepath": filepath,
                    "export_kwargs": export_kwargs
                }
            )
            
            print(f"Data exported successfully to: {filepath}")
            
            # Show export summary
            if args.data_type == 'transactions':
                print(f"Export type: Transaction data ({args.format.upper()})")
                if args.account:
                    print(f"Account: {args.account}")
                if args.start_date or args.end_date:
                    print(f"Date range: {args.start_date or 'beginning'} to {args.end_date or 'now'}")
            elif args.data_type == 'accounts':
                print(f"Export type: Account data ({args.format.upper()})")
                print(f"Total accounts: {len(user.accounts)}")
            elif args.data_type == 'full_backup':
                print(f"Export type: Full backup ({args.format.upper()})")
                print("Includes: User data, all accounts, and complete transaction history")
                
        except ValueError as e:
            # Log failed export
            audit_logger.log_operation(
                event_type=AuditEventType.DATA_EXPORT,
                user=user.username,
                operation=f"Data export failed: {args.data_type} ({args.format})",
                success=False,
                session_id=get_session_token(args),
                details={
                    "data_type": args.data_type,
                    "format": args.format,
                    "error": str(e),
                    "error_type": "ValueError"
                }
            )
            print(f"Export error: {e}")
        except Exception as e:
            # Log unexpected export error
            audit_logger.log_error(
                error=e,
                context={
                    "operation": "data_export",
                    "data_type": args.data_type,
                    "format": args.format
                },
                user=user.username,
                session_id=get_session_token(args)
            )
            print(f"Unexpected error during export: {e}")

def import_data(args):
    """Import account or transaction data"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if user:
        try:
            import_manager = DataExportImportManager(user)
            
            # Validate file exists
            if not os.path.exists(args.filepath):
                print(f"Error: File not found: {args.filepath}")
                return
            
            # Perform import (with validation first if requested)
            if args.validate_only:
                print("Validating import file...")
                result = import_manager.import_data(args.data_type, args.filepath, validate_only=True)
                print("Validation Results:")
                
                # Log validation
                audit_logger.log_operation(
                    event_type=AuditEventType.DATA_IMPORT,
                    user=user.username,
                    operation=f"Data validation: {args.data_type}",
                    success=True,
                    session_id=get_session_token(args),
                    details={
                        "data_type": args.data_type,
                        "filepath": args.filepath,
                        "validation_only": True,
                        "result": result
                    }
                )
            else:
                print(f"Importing {args.data_type} from {args.filepath}...")
                result = import_manager.import_data(args.data_type, args.filepath, validate_only=False)
                print("Import Results:")
                
                # Log import
                audit_logger.log_operation(
                    event_type=AuditEventType.DATA_IMPORT,
                    user=user.username,
                    operation=f"Data import: {args.data_type}",
                    success=True,
                    session_id=get_session_token(args),
                    details={
                        "data_type": args.data_type,
                        "filepath": args.filepath,
                        "validation_only": False,
                        "result": result
                    }
                )
            
            # Display results
            if args.data_type == 'transactions':
                print(f"  Total rows processed: {result['total_rows']}")
                print(f"  Valid transactions: {result['valid_transactions']}")
                print(f"  Invalid transactions: {result['invalid_transactions']}")
                
                if not args.validate_only and result['valid_transactions'] > 0:
                    print(f"  Successfully imported: {len(result['imported_transactions'])} transactions")
                    # Save changes
                    save_users_to_file(users)
                    
            elif args.data_type == 'accounts':
                print(f"  Total accounts processed: {result['total_accounts']}")
                print(f"  Valid accounts: {result['valid_accounts']}")
                print(f"  Invalid accounts: {result['invalid_accounts']}")
                
                if not args.validate_only and result['valid_accounts'] > 0:
                    print(f"  Successfully imported: {len(result['imported_accounts'])} accounts")
                    # Save changes
                    save_users_to_file(users)
            
            # Display errors if any
            if result['errors']:
                print(f"\nErrors encountered ({len(result['errors'])}):")
                for error in result['errors'][:10]:  # Show first 10 errors
                    print(f"  - {error}")
                if len(result['errors']) > 10:
                    print(f"  ... and {len(result['errors']) - 10} more errors")
            
            if args.validate_only:
                print("\nValidation complete. Use --import to actually import the data.")
            
        except FileNotFoundError as e:
            # Log file not found error
            audit_logger.log_operation(
                event_type=AuditEventType.DATA_IMPORT,
                user=user.username,
                operation=f"Data import failed: {args.data_type}",
                success=False,
                session_id=get_session_token(args),
                details={
                    "data_type": args.data_type,
                    "filepath": args.filepath,
                    "error": str(e),
                    "error_type": "FileNotFoundError"
                }
            )
            print(f"File error: {e}")
        except ValueError as e:
            # Log validation error
            audit_logger.log_operation(
                event_type=AuditEventType.DATA_IMPORT,
                user=user.username,
                operation=f"Data import failed: {args.data_type}",
                success=False,
                session_id=get_session_token(args),
                details={
                    "data_type": args.data_type,
                    "filepath": args.filepath,
                    "error": str(e),
                    "error_type": "ValueError"
                }
            )
            print(f"Import error: {e}")
        except Exception as e:
            # Log unexpected import error
            audit_logger.log_error(
                error=e,
                context={
                    "operation": "data_import",
                    "data_type": args.data_type,
                    "filepath": args.filepath
                },
                user=user.username,
                session_id=get_session_token(args)
            )
            print(f"Unexpected error during import: {e}")
        
        print()
        print("Usage:")
        print("  python main.py <command> [arguments]")
        print("  python main.py help <command>     # Detailed help for specific command")
        print("  python main.py interactive        # Interactive mode with menus")
        print()
        print("Examples:")
        print("  python main.py help login         # Help for login command")
        print("  python main.py login user pass    # Login with credentials")
        print("  python main.py interactive        # Start interactive session")
        print()
        print("For command-specific help, use: python main.py help <command>")

def suggest_command(invalid_command):
    """Suggest similar commands for invalid input"""
    suggestions = HelpSystem.get_command_suggestions(invalid_command)
    
    if suggestions:
        print(f"❓ Unknown command: '{invalid_command}'")
        print()
        print("💡 Did you mean:")
        for suggestion in suggestions:
            help_info = HelpSystem.COMMAND_HELP.get(suggestion, {})
            description = help_info.get('description', 'No description available')
            print(f"  • {suggestion:<15} {description}")
        print()
        print("For help: python main.py help <command>")
        print("For all commands: python main.py help")
    else:
        print(ErrorHandler.handle_command_not_found(invalid_command))

def get_session_token(args):
    """Get session token from args, environment, or file"""
    # Check if token provided as argument
    if hasattr(args, 'token') and args.token:
        return args.token
    
    # Check environment variable
    token = os.getenv('SESSION_TOKEN')
    if token:
        return token
    
    # Check session file
    if os.path.exists('.session'):
        try:
            with open('.session', 'r') as f:
                return f.read().strip()
        except:
            pass
    
    return None

def view_audit_logs(args):
    """View audit logs with filtering options"""
    user = authenticate_user(args)
    if not user:
        return
    
    audit_logger = get_audit_logger()
    
    try:
        # Prepare filters
        filters = {}
        if args.user:
            filters['user'] = args.user
        if args.event_type:
            filters['event_type'] = args.event_type
        if args.failed_only:
            filters['success'] = False
        
        # Calculate date range
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(hours=args.hours)
        
        # Get audit logs
        logs = audit_logger.get_audit_logs(
            filters=filters,
            start_date=start_date,
            limit=args.limit
        )
        
        if not logs:
            print("No audit logs found matching the specified criteria.")
            return
        
        # Display logs
        print(f"\n=== Audit Logs ===")
        print(f"Showing {len(logs)} entries from the last {args.hours} hours")
        if filters:
            print(f"Filters applied: {filters}")
        print("=" * 80)
        
        print(f"{'Timestamp':<20} {'User':<15} {'Event':<15} {'Success':<8} {'Operation'}")
        print("-" * 80)
        
        for log_entry in logs:
            timestamp_str = log_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            user_str = (log_entry.user or 'system')[:14]
            event_str = log_entry.event_type.value[:14]
            success_str = '✓' if log_entry.success else '✗'
            operation_str = log_entry.operation[:40] + '...' if len(log_entry.operation) > 40 else log_entry.operation
            
            print(f"{timestamp_str:<20} {user_str:<15} {event_str:<15} {success_str:<8} {operation_str}")
        
        print("=" * 80)
        
        # Log the audit access
        audit_logger.log_operation(
            event_type=AuditEventType.SYSTEM_EVENT,
            user=user.username,
            operation=f"Audit logs accessed - {len(logs)} entries viewed",
            success=True,
            session_id=get_session_token(args),
            details={
                "filters": filters,
                "hours": args.hours,
                "limit": args.limit,
                "entries_returned": len(logs)
            }
        )
        
    except Exception as e:
        audit_logger.log_error(
            error=e,
            context={"operation": "view_audit_logs"},
            user=user.username,
            session_id=get_session_token(args)
        )
        print(f"Error accessing audit logs: {e}")

def view_audit_stats(args):
    """View audit log statistics"""
    user = authenticate_user(args)
    if not user:
        return
    
    audit_logger = get_audit_logger()
    
    try:
        # Get statistics
        stats = audit_logger.get_statistics(hours=args.hours)
        
        # Display statistics
        print(f"\n=== Audit Log Statistics ===")
        print(f"Analysis period: Last {args.hours} hours")
        print("=" * 50)
        
        print(f"Total Events: {stats['total_events']}")
        print(f"Successful Operations: {stats['successful_operations']}")
        print(f"Failed Operations: {stats['failed_operations']}")
        print(f"Unique Users: {stats['unique_users']}")
        print(f"Error Count: {stats['error_count']}")
        
        print(f"\nLogin Activity:")
        print(f"  Total Login Attempts: {stats['login_attempts']}")
        print(f"  Successful Logins: {stats['successful_logins']}")
        print(f"  Failed Logins: {stats['failed_logins']}")
        
        if stats['event_types']:
            print(f"\nEvent Types:")
            for event_type, count in sorted(stats['event_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {event_type}: {count}")
        
        if stats['users_activity']:
            print(f"\nUser Activity (Top 10):")
            sorted_users = sorted(stats['users_activity'].items(), key=lambda x: x[1], reverse=True)
            for username, count in sorted_users[:10]:
                print(f"  {username}: {count} operations")
        
        print("=" * 50)
        
        # Log the stats access
        audit_logger.log_operation(
            event_type=AuditEventType.SYSTEM_EVENT,
            user=user.username,
            operation=f"Audit statistics accessed - {args.hours}h period",
            success=True,
            session_id=get_session_token(args),
            details={
                "hours": args.hours,
                "stats": stats
            }
        )
        
    except Exception as e:
        audit_logger.log_error(
            error=e,
            context={"operation": "view_audit_stats"},
            user=user.username,
            session_id=get_session_token(args)
        )
        print(f"Error accessing audit statistics: {e}")

def authenticate_user(args):
    """Authenticate user using session token"""
    token = get_session_token(args)
    if not token:
        print("Error: No session token found. Please login first.")
        return None
    
    username = SessionManager.validate_session(token)
    if not username:
        print("Error: Invalid or expired session. Please login again.")
        return None
    
    if username not in users:
        print("Error: User not found.")
        return None
    
    return users[username]

def batch_operations(args):
    """Process batch operations from file"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if not user:
        return
    
    try:
        batch_manager = BatchManager(user)
        
        # Check if file exists
        if not os.path.exists(args.file):
            print(f"Error: Batch file not found: {args.file}")
            return
        
        print(f"Processing batch file: {args.file}")
        
        if args.preview:
            print("🔍 PREVIEW MODE - Operations will be validated but not executed")
        
        print("-" * 60)
        
        # Progress callback for real-time updates
        def progress_callback(completed, total, operation):
            if not args.preview:
                progress_percent = (completed / total * 100) if total > 0 else 0
                status_symbol = "✓" if operation.status.value == "success" else "✗"
                print(f"[{progress_percent:5.1f}%] {status_symbol} {operation.operation_type.upper()}: {operation.result or operation.error_message}")
        
        # Process batch file
        operations, summary = batch_manager.process_batch_file(
            args.file, 
            preview_mode=args.preview,
            progress_callback=progress_callback if not args.preview else None
        )
        
        # Log batch operation
        audit_logger.log_operation(
            event_type=AuditEventType.BATCH_OPERATION,
            user=user.username,
            operation=f"Batch processing: {args.file} ({'preview' if args.preview else 'execute'})",
            success=summary['failed'] == 0,
            session_id=get_session_token(args),
            details={
                "file_path": args.file,
                "preview_mode": args.preview,
                "total_operations": summary['total_operations'],
                "successful": summary['successful'],
                "failed": summary['failed'],
                "success_rate": summary['success_rate']
            }
        )
        
        print("-" * 60)
        
        # Display summary
        print(f"\n📊 BATCH OPERATION SUMMARY")
        print("=" * 40)
        print(f"File: {args.file}")
        print(f"Mode: {'Preview' if args.preview else 'Execute'}")
        print(f"Total Operations: {summary['total_operations']}")
        
        if args.preview:
            # In preview mode, show validation results
            validated = summary['total_operations'] - summary['failed']
            print(f"Valid Operations: {validated}")
            print(f"Invalid Operations: {summary['failed']}")
            if summary['total_operations'] > 0:
                validation_rate = (validated / summary['total_operations'] * 100)
                print(f"Validation Rate: {validation_rate:.1f}%")
        else:
            print(f"Successful: {summary['successful']}")
            print(f"Failed: {summary['failed']}")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['total_execution_time'] > 0:
            print(f"Execution Time: {summary['total_execution_time']:.2f} seconds")
        
        # Show operations by type
        if summary['operations_by_type']:
            print(f"\nOperations by Type:")
            for op_type, stats in summary['operations_by_type'].items():
                print(f"  {op_type.upper()}: {stats['successful']}/{stats['total']} successful")
        
        # Show failed operations if any
        if summary['failed_operations']:
            print(f"\n❌ Failed Operations ({len(summary['failed_operations'])}):")
            for failed_op in summary['failed_operations'][:5]:  # Show first 5
                line_info = f" (Line {failed_op['line_number']})" if failed_op['line_number'] else ""
                print(f"  • {failed_op['operation_type'].upper()}{line_info}: {failed_op['error_message']}")
            
            if len(summary['failed_operations']) > 5:
                print(f"  ... and {len(summary['failed_operations']) - 5} more failures")
        
        # Generate detailed report if requested
        if args.report:
            from src.managers.batch_manager import BatchReporter
            detailed_report = BatchReporter.generate_detailed_report(operations)
            
            report_filename = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w') as f:
                f.write(detailed_report)
            
            print(f"\n📄 Detailed report saved to: {report_filename}")
        
        # Save changes if operations were executed
        if not args.preview and summary['successful'] > 0:
            save_users_to_file(users)
            print(f"\n💾 Changes saved to user data file")
        
        if args.preview:
            print(f"\n💡 To execute these operations, run without --preview flag")
        
        print("=" * 40)
        
    except Exception as e:
        # Log batch operation error
        audit_logger.log_error(
            error=e,
            context={
                "operation": "batch_operations",
                "file_path": args.file,
                "preview_mode": args.preview
            },
            user=user.username,
            session_id=get_session_token(args)
        )
        print(f"❌ Batch operation failed: {e}")

def batch_template(args):
    """Create batch operation template file"""
    user = authenticate_user(args)
    if not user:
        return
    
    try:
        batch_manager = BatchManager(user)
        
        # Create template
        result = batch_manager.create_batch_template(args.filename, args.format)
        print(f"✓ {result}")
        
        # Show template usage
        print(f"\n📝 Template Usage:")
        print(f"1. Edit the template file: {args.filename}")
        print(f"2. Add your operations following the examples")
        print(f"3. Preview: python main.py batch_operations {args.filename} --preview")
        print(f"4. Execute: python main.py batch_operations {args.filename}")
        
        if args.format == 'csv':
            print(f"\n💡 CSV Format Tips:")
            print(f"  • Lines starting with # are comments (ignored)")
            print(f"  • Required columns: operation_type, account, amount")
            print(f"  • Optional columns: to_account, memo, nickname, overdraft_limit")
            print(f"  • Supported operations: deposit, withdraw, transfer, create_account, update_nickname")
        else:
            print(f"\n💡 JSON Format Tips:")
            print(f"  • Each operation has 'operation_type' and 'parameters'")
            print(f"  • Parameters vary by operation type")
            print(f"  • Use proper JSON syntax (quotes, commas, brackets)")
        
    except Exception as e:
        print(f"❌ Template creation failed: {e}")

def batch_status(args):
    """Show batch operation status and recent history"""
    user = authenticate_user(args)
    if not user:
        return
    
    audit_logger = get_audit_logger()
    
    try:
        # Get recent batch operations from audit logs
        recent_batches = audit_logger.get_recent_operations(
            user=user.username,
            operation_type="batch_operations",
            hours=args.hours,
            limit=args.limit
        )
        
        if not recent_batches:
            print(f"📊 No batch operations found in the last {args.hours} hours")
            return
        
        print(f"📊 BATCH OPERATION HISTORY")
        print(f"User: {user.username}")
        print(f"Period: Last {args.hours} hours")
        print("=" * 60)
        
        for batch in recent_batches:
            timestamp = batch.get('timestamp', 'Unknown')
            details = batch.get('details', {})
            success = batch.get('success', False)
            
            status_symbol = "✓" if success else "✗"
            mode = "Preview" if details.get('preview_mode') else "Execute"
            
            print(f"{status_symbol} {timestamp}")
            print(f"   File: {details.get('file_path', 'Unknown')}")
            print(f"   Mode: {mode}")
            print(f"   Operations: {details.get('total_operations', 0)}")
            print(f"   Success Rate: {details.get('success_rate', 0):.1f}%")
            print()
        
        print("=" * 60)
        print(f"💡 Use 'python main.py batch_template' to create new batch files")
        
    except Exception as e:
        print(f"❌ Failed to retrieve batch status: {e}")

def update_account_settings(args):
    """Update account settings (nickname and overdraft limit)"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if not user:
        return
    
    # Validate that at least one setting is provided
    if args.nickname is None and args.overdraft_limit is None:
        print("❌ Error: At least one setting must be provided (--nickname or --overdraft-limit)")
        print("💡 Use: python main.py help update_account_settings")
        return
    
    try:
        # Update account settings
        changes = user.update_account_settings(
            args.account,
            nickname=args.nickname,
            overdraft_limit=args.overdraft_limit
        )
        
        if changes:
            print(f"✓ Account settings updated successfully:")
            for change in changes:
                print(f"  • {change}")
            
            # Save changes
            save_users_to_file(users)
            
            # Log successful update
            audit_logger.log_banking_operation(
                operation_type="account_settings_update",
                user=user.username,
                account_identifier=args.account,
                success=True,
                session_id=get_session_token(args),
                additional_details={
                    "changes_made": changes,
                    "nickname": args.nickname,
                    "overdraft_limit": args.overdraft_limit
                }
            )
        else:
            print("ℹ️  No changes were made (settings already match provided values)")
            
    except ValueError as e:
        print(f"❌ Error: {e}")
        
        # Log failed update
        audit_logger.log_banking_operation(
            operation_type="account_settings_update",
            user=user.username,
            account_identifier=args.account,
            success=False,
            session_id=get_session_token(args),
            additional_details={
                "error": str(e),
                "attempted_nickname": args.nickname,
                "attempted_overdraft_limit": args.overdraft_limit
            }
        )
        
        # Show available accounts
        print("\n💡 Available accounts:")
        for account in user.accounts:
            print(f"  • {account.get_display_name()}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def view_account_settings(args):
    """View current account settings"""
    user = authenticate_user(args)
    if not user:
        return
    
    try:
        settings = user.get_account_settings(args.account)
        
        print(f"\n🏦 ACCOUNT SETTINGS")
        print("=" * 40)
        print(f"Account: {settings['display_name']}")
        print(f"Type: {settings['account_type'].capitalize()}")
        print(f"Status: {'Active' if settings['is_active'] else 'Inactive'}")
        print(f"Balance: ${settings['balance']:.2f}")
        
        if settings['nickname']:
            print(f"Nickname: {settings['nickname']}")
        else:
            print("Nickname: Not set")
        
        if settings['account_type'] == 'current':
            print(f"Overdraft Limit: ${settings['overdraft_limit']:.2f}")
            available_balance = settings['balance'] + settings['overdraft_limit']
            print(f"Available Balance: ${available_balance:.2f}")
        
        print(f"Created: {settings['created_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Activity: {settings['last_activity'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 40)
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        
        # Show available accounts
        print("\n💡 Available accounts:")
        for account in user.accounts:
            print(f"  • {account.get_display_name()}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def deactivate_account(args):
    """Deactivate an account"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if not user:
        return
    
    # Require confirmation for account deactivation
    if not args.confirm:
        print("⚠️  Account deactivation requires confirmation")
        print("💡 Use: python main.py deactivate_account <account> --confirm")
        print("⚠️  Deactivated accounts cannot be used for transactions until reactivated")
        return
    
    try:
        # Get account info before deactivation
        account = user.get_account(args.account)
        if not account:
            raise ValueError(f"Account '{args.account}' not found")
        
        account_name = account.get_display_name()
        
        # Deactivate account
        user.deactivate_account(args.account)
        
        print(f"✓ Account '{account_name}' has been deactivated")
        print("ℹ️  The account can no longer be used for transactions")
        print("ℹ️  Use 'reactivate_account' command to restore functionality")
        
        # Save changes
        save_users_to_file(users)
        
        # Log successful deactivation
        audit_logger.log_banking_operation(
            operation_type="account_deactivate",
            user=user.username,
            account_identifier=args.account,
            success=True,
            session_id=get_session_token(args),
            additional_details={
                "account_name": account_name,
                "balance_at_deactivation": account.balance
            }
        )
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        
        # Log failed deactivation
        audit_logger.log_banking_operation(
            operation_type="account_deactivate",
            user=user.username,
            account_identifier=args.account,
            success=False,
            session_id=get_session_token(args),
            additional_details={"error": str(e)}
        )
        
        # Show available accounts
        print("\n💡 Available accounts:")
        for account in user.accounts:
            status = "Active" if account.is_active else "Inactive"
            print(f"  • {account.get_display_name()} [{status}]")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def reactivate_account(args):
    """Reactivate an account"""
    user = authenticate_user(args)
    audit_logger = get_audit_logger()
    
    if not user:
        return
    
    try:
        # Get account info before reactivation
        account = user.get_account(args.account)
        if not account:
            raise ValueError(f"Account '{args.account}' not found")
        
        account_name = account.get_display_name()
        
        # Reactivate account
        user.reactivate_account(args.account)
        
        print(f"✓ Account '{account_name}' has been reactivated")
        print("ℹ️  The account can now be used for transactions")
        
        # Save changes
        save_users_to_file(users)
        
        # Log successful reactivation
        audit_logger.log_banking_operation(
            operation_type="account_reactivate",
            user=user.username,
            account_identifier=args.account,
            success=True,
            session_id=get_session_token(args),
            additional_details={
                "account_name": account_name,
                "balance_at_reactivation": account.balance
            }
        )
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        
        # Log failed reactivation
        audit_logger.log_banking_operation(
            operation_type="account_reactivate",
            user=user.username,
            account_identifier=args.account,
            success=False,
            session_id=get_session_token(args),
            additional_details={"error": str(e)}
        )
        
        # Show available accounts
        print("\n💡 Available accounts:")
        for account in user.accounts:
            status = "Active" if account.is_active else "Inactive"
            print(f"  • {account.get_display_name()} [{status}]")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="🏦 Banking System - Secure Personal Banking Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py login john_doe mypassword     # Login to your account
  python main.py interactive                   # Start interactive mode
  python main.py help login                    # Get help for login command
  python main.py list_accounts                 # List your accounts
  
For detailed help on any command:
  python main.py help <command>
  
For interactive mode with menus:
  python main.py interactive
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # help command
    help_parser = subparsers.add_parser(
        'help', 
        help="Display detailed help for commands",
        description="Get comprehensive help and usage examples for banking commands"
    )
    help_parser.add_argument(
        "command", 
        type=str, 
        nargs='?',
        help="Command to get help for (optional - shows all commands if omitted)"
    )
    help_parser.set_defaults(func=help_command)

    # register command
    register_parser = subparsers.add_parser(
        'register', 
        help="Register a new user account",
        description="Create a new user account in the banking system with username, password, and email"
    )
    register_parser.add_argument(
        "username", 
        type=str, 
        help="Unique username (letters, numbers, underscore only)"
    )
    register_parser.add_argument(
        'password', 
        type=str, 
        help="Strong password (min 8 chars, mixed case, numbers)"
    )
    register_parser.add_argument(
        'email', 
        type=str, 
        help="Valid email address for password reset"
    )
    register_parser.set_defaults(func=register)

    # login command
    login_parser = subparsers.add_parser(
        "login", 
        help="Authenticate and create session token",
        description="Login to the banking system and create a session token for subsequent operations"
    )
    login_parser.add_argument(
        "username", 
        type=str, 
        help="Your registered username"
    )
    login_parser.add_argument(
        "password", 
        type=str, 
        help="Your account password"
    )
    login_parser.set_defaults(func=login)

    # add account command
    add_account_parser = subparsers.add_parser(
        "add_account", 
        help="Create a new bank account",
        description="Create a new bank account of specified type (savings, current, or salary)"
    )
    add_account_parser.add_argument(
        "type", 
        type=str, 
        choices=['savings', 'current', 'salary'], 
        help="Account type: savings (standard), current (with overdraft), or salary (payroll)"
    )
    add_account_parser.add_argument(
        "balance", 
        type=str, 
        help="Initial balance (must be positive number)"
    )
    add_account_parser.add_argument(
        "--overdraft_limit", 
        type=float, 
        default=0,  
        help="Overdraft limit for current accounts (default: 0)"
    )
    add_account_parser.add_argument(
        "--token", 
        type=str, 
        help="Session token (optional if saved in .session file)"
    )
    add_account_parser.set_defaults(func=add_account)

    # deposit command
    deposit_parser = subparsers.add_parser("deposit", help="Deposit money into an account")
    deposit_parser.add_argument("type", type=str, choices=['savings', 'current', 'salary'], help="Account type")
    deposit_parser.add_argument("amount", type=float, help="Amount to deposit")
    deposit_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    deposit_parser.set_defaults(func=deposit)

    # withdraw command
    withdraw_parser = subparsers.add_parser("withdraw", help="Withdraw money from an account")
    withdraw_parser.add_argument("type", type=str, choices=['savings', 'current', 'salary'], help="Account type")
    withdraw_parser.add_argument("amount", type=float, help="Amount to withdraw")
    withdraw_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    withdraw_parser.set_defaults(func=withdraw)

    # view balance command
    view_balance_parser = subparsers.add_parser("view_balance", help="View account balance")
    view_balance_parser.add_argument("type", type=str, choices=['savings', 'current', 'salary'], help="Account type")
    view_balance_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    view_balance_parser.set_defaults(func=view_balance)

    # initiate password reset command
    reset_password_init_parser = subparsers.add_parser("reset_password_init", help="Initiate password reset")
    reset_password_init_parser.add_argument("username", type=str, help="Username")
    reset_password_init_parser.set_defaults(func=reset_password_init)

    # complete password reset command
    reset_password_complete_parser = subparsers.add_parser("reset_password_complete", help="Complete password reset")
    reset_password_complete_parser.add_argument("token", type=str, help="Password reset token")
    reset_password_complete_parser.add_argument('new_password', type=str, help="New password")
    reset_password_complete_parser.set_defaults(func=reset_password_complete)

    # logout command
    logout_parser = subparsers.add_parser("logout", help="Logout and invalidate session")
    logout_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    logout_parser.set_defaults(func=logout)

    # status command
    status_parser = subparsers.add_parser("status", help="Check login status and session info")
    status_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    status_parser.set_defaults(func=status)

    # list accounts command
    list_accounts_parser = subparsers.add_parser("list_accounts", help="List all accounts for logged in user")
    list_accounts_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    list_accounts_parser.set_defaults(func=list_accounts)

    # account summary command
    account_summary_parser = subparsers.add_parser("account_summary", help="Display comprehensive account summary with detailed information")
    account_summary_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    account_summary_parser.set_defaults(func=account_summary)

    # financial overview command
    financial_overview_parser = subparsers.add_parser("financial_overview", help="Display financial overview with total balances and recent activity")
    financial_overview_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    financial_overview_parser.set_defaults(func=financial_overview)

    # transfer command
    transfer_parser = subparsers.add_parser("transfer", help="Transfer money between your accounts")
    transfer_parser.add_argument("from_account", type=str, help="Source account (account type or nickname)")
    transfer_parser.add_argument("to_account", type=str, help="Destination account (account type or nickname)")
    transfer_parser.add_argument("amount", type=float, help="Amount to transfer")
    transfer_parser.add_argument("--memo", type=str, help="Optional memo for the transfer")
    transfer_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    transfer_parser.set_defaults(func=transfer)

    # transaction history command
    transaction_history_parser = subparsers.add_parser("transaction_history", help="View transaction history with filtering options")
    transaction_history_parser.add_argument("--account", type=str, help="Account identifier (type or nickname)")
    transaction_history_parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    transaction_history_parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    transaction_history_parser.add_argument("--type", nargs='+', choices=['deposit', 'withdrawal', 'transfer'], help="Filter by transaction type(s)")
    transaction_history_parser.add_argument("--min-amount", type=float, help="Minimum transaction amount")
    transaction_history_parser.add_argument("--max-amount", type=float, help="Maximum transaction amount")
    transaction_history_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    transaction_history_parser.add_argument("--page-size", type=int, default=20, help="Transactions per page (default: 20)")
    transaction_history_parser.add_argument("--sort-by", choices=['date', 'amount', 'type', 'account'], default='date', help="Sort transactions by field (default: date)")
    transaction_history_parser.add_argument("--export-format", choices=['csv', 'json'], help="Export transactions to file format")
    transaction_history_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    transaction_history_parser.set_defaults(func=transaction_history)

    # transaction summary command
    transaction_summary_parser = subparsers.add_parser("transaction_summary", help="Display transaction summary statistics")
    transaction_summary_parser.add_argument("--account", type=str, help="Account identifier (type or nickname)")
    transaction_summary_parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    transaction_summary_parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    transaction_summary_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    transaction_summary_parser.set_defaults(func=transaction_summary)

    # interactive mode command
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive banking session")
    interactive_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    interactive_parser.set_defaults(func=interactive)

    # generate statement command
    statement_parser = subparsers.add_parser("generate_statement", help="Generate account statement for specified period")
    statement_parser.add_argument("account", type=str, help="Account identifier (type or nickname)")
    statement_parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    statement_parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    statement_parser.add_argument("--format", choices=['text', 'pdf'], default='text', help="Statement format (default: text)")
    statement_parser.add_argument("--export", action='store_true', help="Export statement to file")
    statement_parser.add_argument("--filename", type=str, help="Custom filename for export")
    statement_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    statement_parser.set_defaults(func=generate_statement)

    # export data command
    export_parser = subparsers.add_parser("export_data", help="Export account or transaction data to file")
    export_parser.add_argument("data_type", choices=['transactions', 'accounts', 'full_backup'], help="Type of data to export")
    export_parser.add_argument("format", choices=['csv', 'json'], help="Export format")
    export_parser.add_argument("--account", type=str, help="Account identifier for transaction export (type or nickname)")
    export_parser.add_argument("--start-date", type=str, help="Start date for transaction export (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    export_parser.add_argument("--end-date", type=str, help="End date for transaction export (YYYY-MM-DD, YYYY-MM-DD HH:MM, MM/DD/YYYY, DD/MM/YYYY)")
    export_parser.add_argument("--filename", type=str, help="Custom filename for export")
    export_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    export_parser.set_defaults(func=export_data)

    # import data command
    import_parser = subparsers.add_parser("import_data", help="Import account or transaction data from file")
    import_parser.add_argument("data_type", choices=['transactions', 'accounts'], help="Type of data to import")
    import_parser.add_argument("filepath", type=str, help="Path to import file")
    import_parser.add_argument("--validate-only", action='store_true', help="Only validate the file without importing")
    import_parser.add_argument("--token", type=str, help="Session token (optional if saved in .session file)")
    import_parser.set_defaults(func=import_data)

    # audit_logs command
    audit_logs_parser = subparsers.add_parser(
        "audit_logs",
        help="View audit logs and system activity",
        description="Access audit logs with filtering options for administrators"
    )
    audit_logs_parser.add_argument(
        "--user",
        type=str,
        help="Filter logs by specific user"
    )
    audit_logs_parser.add_argument(
        "--event-type",
        type=str,
        choices=['login_success', 'login_failure', 'logout', 'deposit', 'withdrawal', 'transfer', 'balance_inquiry', 'error'],
        help="Filter logs by event type"
    )
    audit_logs_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back (default: 24)"
    )
    audit_logs_parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of entries to show (default: 100)"
    )
    audit_logs_parser.add_argument(
        "--failed-only",
        action="store_true",
        help="Show only failed operations"
    )
    audit_logs_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    audit_logs_parser.set_defaults(func=view_audit_logs)

    # audit_stats command
    audit_stats_parser = subparsers.add_parser(
        "audit_stats",
        help="View audit log statistics",
        description="Display audit log statistics and system activity summary"
    )
    audit_stats_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to analyze (default: 24)"
    )
    audit_stats_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    audit_stats_parser.set_defaults(func=view_audit_stats)

    # batch_operations command
    batch_operations_parser = subparsers.add_parser(
        "batch_operations",
        help="Process batch operations from file",
        description="Execute multiple banking operations from CSV or JSON batch files"
    )
    batch_operations_parser.add_argument(
        "file",
        type=str,
        help="Path to batch operations file (CSV or JSON format)"
    )
    batch_operations_parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview operations without executing (validation only)"
    )
    batch_operations_parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report file after processing"
    )
    batch_operations_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    batch_operations_parser.set_defaults(func=batch_operations)

    # batch_template command
    batch_template_parser = subparsers.add_parser(
        "batch_template",
        help="Create batch operation template file",
        description="Generate template files for batch operations with examples"
    )
    batch_template_parser.add_argument(
        "filename",
        type=str,
        help="Template filename to create"
    )
    batch_template_parser.add_argument(
        "--format",
        choices=['csv', 'json'],
        default='csv',
        help="Template format (default: csv)"
    )
    batch_template_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    batch_template_parser.set_defaults(func=batch_template)

    # batch_status command
    batch_status_parser = subparsers.add_parser(
        "batch_status",
        help="Show batch operation status and history",
        description="Display recent batch operation history and status"
    )
    batch_status_parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back (default: 24)"
    )
    batch_status_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of batch operations to show (default: 10)"
    )
    batch_status_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    batch_status_parser.set_defaults(func=batch_status)

    # update_account_settings command
    update_account_settings_parser = subparsers.add_parser(
        "update_account_settings",
        help="Update account settings (nickname and overdraft limit)",
        description="Modify account nickname and overdraft limit settings"
    )
    update_account_settings_parser.add_argument(
        "account",
        type=str,
        help="Account identifier (account type or nickname)"
    )
    update_account_settings_parser.add_argument(
        "--nickname",
        type=str,
        help="New nickname for the account"
    )
    update_account_settings_parser.add_argument(
        "--overdraft-limit",
        type=float,
        help="New overdraft limit (only for current accounts)"
    )
    update_account_settings_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    update_account_settings_parser.set_defaults(func=update_account_settings)

    # view_account_settings command
    view_account_settings_parser = subparsers.add_parser(
        "view_account_settings",
        help="View current account settings",
        description="Display detailed settings for a specific account"
    )
    view_account_settings_parser.add_argument(
        "account",
        type=str,
        help="Account identifier (account type or nickname)"
    )
    view_account_settings_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    view_account_settings_parser.set_defaults(func=view_account_settings)

    # deactivate_account command
    deactivate_account_parser = subparsers.add_parser(
        "deactivate_account",
        help="Deactivate an account",
        description="Deactivate an account to prevent transactions while preserving data"
    )
    deactivate_account_parser.add_argument(
        "account",
        type=str,
        help="Account identifier (account type or nickname)"
    )
    deactivate_account_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm account deactivation"
    )
    deactivate_account_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    deactivate_account_parser.set_defaults(func=deactivate_account)

    # reactivate_account command
    reactivate_account_parser = subparsers.add_parser(
        "reactivate_account",
        help="Reactivate an account",
        description="Reactivate a previously deactivated account"
    )
    reactivate_account_parser.add_argument(
        "account",
        type=str,
        help="Account identifier (account type or nickname)"
    )
    reactivate_account_parser.add_argument(
        "--token",
        type=str,
        help="Session token (optional if saved in .session file)"
    )
    reactivate_account_parser.set_defaults(func=reactivate_account)

    return parser.parse_args()

if __name__ == "__main__":
    current_user = None
    
    try:
        args = parse_args()
        
        # Check if a command was provided
        if hasattr(args, 'func'):
            # Validate command usage before execution
            command_name = args.command if hasattr(args, 'command') else 'unknown'
            
            # Execute the command with enhanced error handling
            try:
                args.func(args)
            except KeyboardInterrupt:
                print("\n\n⚠️  Operation interrupted by user")
                sys.exit(0)
            except Exception as e:
                print(f"\n❌ Error executing command '{command_name}': {e}")
                
                # Provide helpful error context
                if command_name in HelpSystem.get_all_commands():
                    print(f"\n💡 For help with this command:")
                    print(f"   python main.py help {command_name}")
                
                sys.exit(1)
        else:
            # No command provided or invalid command
            if len(sys.argv) > 1:
                invalid_command = sys.argv[1]
                suggest_command(invalid_command)
            else:
                print("🏦 Banking System")
                print("=" * 50)
                print("No command provided. Use one of the following:")
                print()
                print("  python main.py help              # Show all commands")
                print("  python main.py interactive       # Start interactive mode")
                print("  python main.py login <user> <pass>  # Login to your account")
                print()
                print("For detailed help: python main.py help <command>")
            
            sys.exit(1)
            
    except SystemExit:
        # Handle argparse exits gracefully
        pass
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n💡 Try:")
        print("   python main.py help              # For available commands")
        print("   python main.py interactive       # For interactive mode")
        sys.exit(1)