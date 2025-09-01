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
    
    user = login_user(users, args.username, args.password)
    if user:
        # Create session token
        token = SessionManager.create_session(args.username)
        print(f"Login successful for {args.username}")
        print(f"Session token: {token}")
        print("Use this token for subsequent operations or save it to SESSION_TOKEN environment variable")
        
        # Optionally save to environment file for convenience
        with open('.session', 'w') as f:
            f.write(token)
        print("Session token saved to .session file")
    else:
        print("Login failed")

def add_account(args):
    user = authenticate_user(args)
    if user:
        user.add_account(Account(args.type, balance=float(args.balance), overdraft_limit=args.overdraft_limit))
        save_users_to_file(users)
    # Error message already printed by authenticate_user

def deposit(args):
    user = authenticate_user(args)
    if user:
        account = user.get_account(args.type)
        if account:
            account.deposit(args.amount)
            save_users_to_file(users)

def withdraw(args):
    user = authenticate_user(args)
    if user:
        account = user.get_account(args.type)
        if account:
            account.withdraw(args.amount)
            save_users_to_file(users)

def view_balance(args):
    user = authenticate_user(args)
    if user:
        account = user.get_account(args.type)
        if account:
            print(f"Balance: ${account.get_balance()}")

def reset_password_init(args):
    initiate_password_reset(users, args.username)

def reset_password_complete(args):
    reset_password(users, args.token, args.new_password)
    save_users_to_file(users)

def logout(args):
    """Logout and invalidate session"""
    token = get_session_token(args)
    if token and SessionManager.invalidate_session(token):
        # Remove session file
        if os.path.exists('.session'):
            os.remove('.session')
        print("Logged out successfully")
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
    if user:
        # Validate and execute transfer
        success, message, transfer_id = user.transfer_between_accounts(
            args.from_account, args.to_account, args.amount, args.memo
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