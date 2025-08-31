"""
Interactive Session Management for Banking System

This module provides an interactive menu-driven interface for the banking system,
allowing users to perform multiple operations within a single authenticated session.
"""

import os
import time
from datetime import datetime, timedelta
from src.utils.security_utils import SessionManager
from src.utils.data_storage import save_users_to_file


class InteractiveSession:
    """
    Manages interactive banking sessions with menu-driven interface
    """
    
    # Session configuration
    SESSION_TIMEOUT_MINUTES = 30
    INACTIVITY_WARNING_MINUTES = 25
    
    def __init__(self, user, users_dict):
        """
        Initialize interactive session
        
        Args:
            user: Authenticated User object
            users_dict: Global users dictionary for saving changes
        """
        self.user = user
        self.users_dict = users_dict
        self.session_start = datetime.now()
        self.last_activity = datetime.now()
        self.session_active = True
        self.warned_timeout = False
        
    def display_main_menu(self):
        """Display the main menu options"""
        print("\n" + "=" * 60)
        print(f"  BANKING SYSTEM - Interactive Mode")
        print(f"  Welcome, {self.user.username}!")
        print("=" * 60)
        print("1. Account Management")
        print("2. Banking Operations") 
        print("3. Transaction History")
        print("4. Account Statements")
        print("5. Settings & Profile")
        print("6. Logout")
        print("=" * 60)
        
        # Show session info
        session_duration = datetime.now() - self.session_start
        minutes_active = int(session_duration.total_seconds() / 60)
        print(f"Session active for: {minutes_active} minutes")
        
        # Show timeout warning if approaching limit
        if self._should_show_timeout_warning():
            remaining = self.SESSION_TIMEOUT_MINUTES - minutes_active
            print(f"⚠️  Session will timeout in {remaining} minutes")
        
        print("=" * 60)
    
    def handle_menu_selection(self, choice):
        """
        Handle main menu selection
        
        Args:
            choice: User's menu choice as string
            
        Returns:
            bool: True to continue session, False to exit
        """
        self._update_activity()
        
        if not self._check_session_timeout():
            return False
            
        choice = choice.strip()
        
        if choice == '1':
            return self._handle_account_management()
        elif choice == '2':
            return self._handle_banking_operations()
        elif choice == '3':
            return self._handle_transaction_history()
        elif choice == '4':
            return self._handle_account_statements()
        elif choice == '5':
            return self._handle_settings()
        elif choice == '6':
            return self._handle_logout()
        else:
            print("❌ Invalid choice. Please select 1-6.")
            return True
    
    def run_session(self):
        """
        Main session loop - displays menu and handles user input
        """
        print(f"\n🏦 Starting interactive banking session for {self.user.username}")
        print("Type 'help' at any prompt for assistance, or 'exit' to logout")
        
        try:
            while self.session_active:
                if not self._check_session_timeout():
                    break
                    
                self.display_main_menu()
                
                try:
                    choice = input("\nSelect an option (1-6): ").strip()
                    
                    # Handle special commands
                    if choice.lower() in ['exit', 'quit', 'logout']:
                        break
                    elif choice.lower() == 'help':
                        self._show_help()
                        continue
                    
                    # Handle menu selection
                    if not self.handle_menu_selection(choice):
                        break
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️  Session interrupted by user")
                    break
                except EOFError:
                    print("\n\n⚠️  Input stream ended")
                    break
                    
        except Exception as e:
            print(f"\n❌ Unexpected error in session: {e}")
        finally:
            self.cleanup_session()
    
    def cleanup_session(self):
        """
        Clean up session resources and perform logout
        """
        print("\n" + "=" * 60)
        print("  SESSION CLEANUP")
        print("=" * 60)
        
        # Save any pending changes
        try:
            save_users_to_file(self.users_dict)
            print("✓ Data saved successfully")
        except Exception as e:
            print(f"❌ Error saving data: {e}")
        
        # Calculate session duration
        session_duration = datetime.now() - self.session_start
        minutes_active = int(session_duration.total_seconds() / 60)
        
        print(f"✓ Session duration: {minutes_active} minutes")
        print(f"✓ Logged out user: {self.user.username}")
        print("✓ Session cleanup complete")
        print("=" * 60)
        print("Thank you for using the Banking System!")
        
        self.session_active = False
    
    def _update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        self.warned_timeout = False  # Reset warning flag on activity
    
    def _check_session_timeout(self):
        """
        Check if session has timed out
        
        Returns:
            bool: True if session is still valid, False if timed out
        """
        time_since_activity = datetime.now() - self.last_activity
        minutes_inactive = time_since_activity.total_seconds() / 60
        
        if minutes_inactive >= self.SESSION_TIMEOUT_MINUTES:
            print("\n" + "⚠️" * 20)
            print("  SESSION TIMEOUT")
            print("⚠️" * 20)
            print(f"Your session has been inactive for {int(minutes_inactive)} minutes.")
            print("For security reasons, you have been automatically logged out.")
            print("Please login again to continue banking operations.")
            print("⚠️" * 20)
            return False
        
        return True
    
    def _should_show_timeout_warning(self):
        """
        Check if timeout warning should be displayed
        
        Returns:
            bool: True if warning should be shown
        """
        time_since_activity = datetime.now() - self.last_activity
        minutes_inactive = time_since_activity.total_seconds() / 60
        
        return (minutes_inactive >= self.INACTIVITY_WARNING_MINUTES and 
                not self.warned_timeout)
    
    def _show_help(self):
        """Display help information"""
        print("\n" + "=" * 60)
        print("  HELP - Interactive Banking System")
        print("=" * 60)
        print("Navigation:")
        print("  • Select menu options by entering the number (1-6)")
        print("  • Type 'help' at any prompt for assistance")
        print("  • Type 'exit', 'quit', or 'logout' to end session")
        print("  • Use Ctrl+C to interrupt current operation")
        print()
        print("Menu Options:")
        print("  1. Account Management - Create, view, and manage accounts")
        print("  2. Banking Operations - Deposits, withdrawals, transfers")
        print("  3. Transaction History - View and filter transaction records")
        print("  4. Account Statements - Generate account statements")
        print("  5. Settings & Profile - Update account settings and profile")
        print("  6. Logout - End session and exit")
        print()
        print("Session Information:")
        print(f"  • Session timeout: {self.SESSION_TIMEOUT_MINUTES} minutes of inactivity")
        print(f"  • Warning shown at: {self.INACTIVITY_WARNING_MINUTES} minutes")
        print("  • All changes are automatically saved")
        print("=" * 60)
    
    def _handle_account_management(self):
        """Handle account management submenu"""
        while True:
            print("\n" + "=" * 50)
            print("  ACCOUNT MANAGEMENT")
            print("=" * 50)
            print("1. List All Accounts")
            print("2. Create New Account")
            print("3. Account Details & Summary")
            print("4. Update Account Settings")
            print("5. Financial Overview")
            print("6. Back to Main Menu")
            print("=" * 50)
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                self._list_accounts()
            elif choice == '2':
                self._create_account()
            elif choice == '3':
                self._account_details()
            elif choice == '4':
                self._update_account_settings()
            elif choice == '5':
                self._financial_overview()
            elif choice == '6':
                return True
            else:
                print("❌ Invalid choice. Please select 1-6.")
            
            if not self._check_session_timeout():
                return False
    
    def _handle_banking_operations(self):
        """Handle banking operations submenu"""
        while True:
            print("\n" + "=" * 50)
            print("  BANKING OPERATIONS")
            print("=" * 50)
            print("1. Deposit Money")
            print("2. Withdraw Money")
            print("3. Transfer Between Accounts")
            print("4. View Account Balance")
            print("5. Transfer History")
            print("6. Back to Main Menu")
            print("=" * 50)
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                self._deposit_money()
            elif choice == '2':
                self._withdraw_money()
            elif choice == '3':
                self._transfer_money()
            elif choice == '4':
                self._view_balance()
            elif choice == '5':
                self._transfer_history()
            elif choice == '6':
                return True
            else:
                print("❌ Invalid choice. Please select 1-6.")
            
            if not self._check_session_timeout():
                return False
    
    def _handle_transaction_history(self):
        """Handle transaction history submenu"""
        while True:
            print("\n" + "=" * 50)
            print("  TRANSACTION HISTORY")
            print("=" * 50)
            print("1. View All Transactions")
            print("2. Filter by Account")
            print("3. Filter by Date Range")
            print("4. Filter by Transaction Type")
            print("5. Transaction Summary")
            print("6. Export Transactions")
            print("7. Back to Main Menu")
            print("=" * 50)
            
            choice = input("Select an option (1-7): ").strip()
            
            if choice == '1':
                self._view_all_transactions()
            elif choice == '2':
                self._filter_by_account()
            elif choice == '3':
                self._filter_by_date()
            elif choice == '4':
                self._filter_by_type()
            elif choice == '5':
                self._transaction_summary()
            elif choice == '6':
                self._export_transactions()
            elif choice == '7':
                return True
            else:
                print("❌ Invalid choice. Please select 1-7.")
            
            if not self._check_session_timeout():
                return False
    
    def _handle_account_statements(self):
        """Handle account statements - placeholder for future implementation"""
        print("\n📄 Account Statements")
        print("This feature will be implemented in a future phase.")
        input("Press Enter to continue...")
        return True
    
    def _handle_settings(self):
        """Handle settings and profile submenu"""
        while True:
            print("\n" + "=" * 50)
            print("  SETTINGS & PROFILE")
            print("=" * 50)
            print("1. Update Account Nicknames")
            print("2. Change Account Settings")
            print("3. View Profile Information")
            print("4. Session Information")
            print("5. Help & Documentation")
            print("6. Back to Main Menu")
            print("=" * 50)
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                self._update_nicknames()
            elif choice == '2':
                self._change_account_settings()
            elif choice == '3':
                self._view_profile()
            elif choice == '4':
                self._session_info()
            elif choice == '5':
                self._show_help()
            elif choice == '6':
                return True
            else:
                print("❌ Invalid choice. Please select 1-6.")
            
            if not self._check_session_timeout():
                return False
    
    def _handle_logout(self):
        """Handle logout confirmation"""
        print("\n🚪 Logout Confirmation")
        print("Are you sure you want to logout?")
        
        while True:
            choice = input("Enter 'y' to logout or 'n' to continue: ").strip().lower()
            if choice in ['y', 'yes']:
                print("✓ Logging out...")
                return False
            elif choice in ['n', 'no']:
                print("✓ Continuing session...")
                return True
            else:
                print("❌ Please enter 'y' for yes or 'n' for no")


    # Account Management Operations
    def _list_accounts(self):
        """List all user accounts"""
        print("\n📋 Account List")
        print("-" * 40)
        
        if not self.user.accounts:
            print("No accounts found. Create an account first.")
            return
        
        total_balance = 0
        for account in self.user.accounts:
            balance = account.get_balance()
            total_balance += balance
            
            display_name = account.get_display_name()
            print(f"{display_name:>25}: ${balance:>10.2f}")
            if account.overdraft_limit > 0:
                print(f"{'':>25}  (Overdraft: ${account.overdraft_limit:.2f})")
        
        print("-" * 40)
        print(f"{'Total Balance':>25}: ${total_balance:>10.2f}")
        input("\nPress Enter to continue...")
    
    def _create_account(self):
        """Create a new account"""
        print("\n🆕 Create New Account")
        print("-" * 30)
        
        # Get account type
        print("Available account types:")
        print("1. Savings")
        print("2. Current")
        print("3. Salary")
        
        while True:
            choice = input("Select account type (1-3): ").strip()
            if choice == '1':
                account_type = 'savings'
                break
            elif choice == '2':
                account_type = 'current'
                break
            elif choice == '3':
                account_type = 'salary'
                break
            else:
                print("❌ Invalid choice. Please select 1-3.")
        
        # Check if account type already exists
        existing = self.user.get_account(account_type)
        if existing:
            print(f"❌ You already have a {account_type} account.")
            input("Press Enter to continue...")
            return
        
        # Get initial balance
        while True:
            try:
                balance_str = input("Enter initial balance (default 0): ").strip()
                balance = float(balance_str) if balance_str else 0.0
                if balance < 0:
                    print("❌ Balance cannot be negative.")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Get overdraft limit for current accounts
        overdraft_limit = 0
        if account_type == 'current':
            while True:
                try:
                    overdraft_str = input("Enter overdraft limit (default 0): ").strip()
                    overdraft_limit = float(overdraft_str) if overdraft_str else 0.0
                    if overdraft_limit < 0:
                        print("❌ Overdraft limit cannot be negative.")
                        continue
                    break
                except ValueError:
                    print("❌ Please enter a valid number.")
        
        # Get optional nickname
        nickname = input("Enter account nickname (optional): ").strip()
        nickname = nickname if nickname else None
        
        # Create account
        try:
            account = self.user.create_account_with_nickname(account_type, balance, overdraft_limit, nickname)
            print(f"✓ {account_type.capitalize()} account created successfully!")
            if nickname:
                print(f"  Nickname: {nickname}")
            print(f"  Initial balance: ${balance:.2f}")
            if overdraft_limit > 0:
                print(f"  Overdraft limit: ${overdraft_limit:.2f}")
        except Exception as e:
            print(f"❌ Error creating account: {e}")
        
        input("\nPress Enter to continue...")
    
    def _account_details(self):
        """Show detailed account information"""
        print("\n📊 Account Details")
        
        if not self.user.accounts:
            print("No accounts found.")
            input("Press Enter to continue...")
            return
        
        summary = self.user.get_enhanced_summary()
        
        print(f"\n=== Account Summary for {self.user.username} ===")
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
        
        input("\nPress Enter to continue...")
    
    def _update_account_settings(self):
        """Update account settings like nicknames"""
        print("\n⚙️  Update Account Settings")
        
        if not self.user.accounts:
            print("No accounts found.")
            input("Press Enter to continue...")
            return
        
        # Show available accounts
        print("\nAvailable accounts:")
        for i, account in enumerate(self.user.accounts, 1):
            print(f"{i}. {account.get_display_name()}")
        
        # Select account
        while True:
            try:
                choice = input(f"Select account (1-{len(self.user.accounts)}): ").strip()
                account_idx = int(choice) - 1
                if 0 <= account_idx < len(self.user.accounts):
                    selected_account = self.user.accounts[account_idx]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(self.user.accounts)}")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Update nickname
        current_nickname = selected_account.nickname or "None"
        print(f"\nCurrent nickname: {current_nickname}")
        new_nickname = input("Enter new nickname (leave empty to remove): ").strip()
        
        if new_nickname:
            selected_account.update_nickname(new_nickname)
            print(f"✓ Nickname updated to: {new_nickname}")
        elif selected_account.nickname:
            selected_account.update_nickname(None)
            print("✓ Nickname removed")
        else:
            print("No changes made.")
        
        input("\nPress Enter to continue...")
    
    def _financial_overview(self):
        """Display financial overview"""
        print("\n💰 Financial Overview")
        
        if not self.user.accounts:
            print("No accounts found.")
            input("Press Enter to continue...")
            return
        
        overview = self.user.get_financial_overview()
        
        print(f"\n=== Financial Overview for {self.user.username} ===")
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
        
        input("\nPress Enter to continue...")
    
    # Banking Operations
    def _deposit_money(self):
        """Handle money deposit"""
        print("\n💵 Deposit Money")
        
        if not self.user.accounts:
            print("No accounts found. Create an account first.")
            input("Press Enter to continue...")
            return
        
        # Select account
        account = self._select_account("Select account for deposit:")
        if not account:
            return
        
        # Get amount
        while True:
            try:
                amount = float(input("Enter deposit amount: $"))
                if amount <= 0:
                    print("❌ Amount must be positive.")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Perform deposit
        old_balance = account.balance
        account.deposit(amount)
        
        print(f"✓ Deposit successful!")
        print(f"  Previous balance: ${old_balance:.2f}")
        print(f"  New balance: ${account.balance:.2f}")
        
        input("\nPress Enter to continue...")
    
    def _withdraw_money(self):
        """Handle money withdrawal"""
        print("\n💸 Withdraw Money")
        
        if not self.user.accounts:
            print("No accounts found. Create an account first.")
            input("Press Enter to continue...")
            return
        
        # Select account
        account = self._select_account("Select account for withdrawal:")
        if not account:
            return
        
        # Show available balance
        available = account.balance
        if account.account_type == 'current':
            available += account.overdraft_limit
        
        print(f"Current balance: ${account.balance:.2f}")
        if account.overdraft_limit > 0:
            print(f"Available (with overdraft): ${available:.2f}")
        
        # Get amount
        while True:
            try:
                amount = float(input("Enter withdrawal amount: $"))
                if amount <= 0:
                    print("❌ Amount must be positive.")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Perform withdrawal
        old_balance = account.balance
        account.withdraw(amount)
        
        # Check if withdrawal was successful (balance changed)
        if account.balance != old_balance:
            print(f"✓ Withdrawal successful!")
            print(f"  Previous balance: ${old_balance:.2f}")
            print(f"  New balance: ${account.balance:.2f}")
        
        input("\nPress Enter to continue...")
    
    def _transfer_money(self):
        """Handle money transfer between accounts"""
        print("\n🔄 Transfer Money")
        
        if len(self.user.accounts) < 2:
            print("You need at least 2 accounts to make transfers.")
            input("Press Enter to continue...")
            return
        
        # Select source account
        print("\nSelect source account:")
        from_account = self._select_account("Transfer FROM:")
        if not from_account:
            return
        
        # Select destination account
        print("\nSelect destination account:")
        available_accounts = [acc for acc in self.user.accounts if acc != from_account]
        to_account = self._select_account("Transfer TO:", available_accounts)
        if not to_account:
            return
        
        # Show balances
        print(f"\nSource account balance: ${from_account.balance:.2f}")
        available = from_account.balance
        if from_account.account_type == 'current':
            available += from_account.overdraft_limit
            print(f"Available (with overdraft): ${available:.2f}")
        
        # Get amount
        while True:
            try:
                amount = float(input("Enter transfer amount: $"))
                if amount <= 0:
                    print("❌ Amount must be positive.")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Get optional memo
        memo = input("Enter memo (optional): ").strip()
        memo = memo if memo else None
        
        # Perform transfer
        success, message, transfer_id = self.user.transfer_between_accounts(
            from_account.account_type, to_account.account_type, amount, memo
        )
        
        if success:
            print(f"✓ {message}")
            print(f"\nUpdated Balances:")
            print(f"  {from_account.get_display_name()}: ${from_account.balance:.2f}")
            print(f"  {to_account.get_display_name()}: ${to_account.balance:.2f}")
        else:
            print(f"❌ Transfer failed: {message}")
        
        input("\nPress Enter to continue...")
    
    def _view_balance(self):
        """View account balance"""
        print("\n💰 View Balance")
        
        if not self.user.accounts:
            print("No accounts found.")
            input("Press Enter to continue...")
            return
        
        # Select account
        account = self._select_account("Select account to view balance:")
        if not account:
            return
        
        print(f"\nAccount: {account.get_display_name()}")
        print(f"Balance: ${account.balance:.2f}")
        
        if account.overdraft_limit > 0:
            available = account.balance + account.overdraft_limit
            print(f"Overdraft Limit: ${account.overdraft_limit:.2f}")
            print(f"Available Balance: ${available:.2f}")
        
        print(f"Total Transactions: {len(account.transactions)}")
        
        input("\nPress Enter to continue...")
    
    def _transfer_history(self):
        """View transfer history"""
        print("\n🔄 Transfer History")
        
        try:
            transfers = self.user.get_transfer_history()
            
            if not transfers:
                print("No transfers found.")
                input("Press Enter to continue...")
                return
            
            print(f"\nFound {len(transfers)} transfers:")
            print("-" * 80)
            print(f"{'Date':<20} {'From':<15} {'To':<15} {'Amount':<12} {'ID':<10}")
            print("-" * 80)
            
            for transfer in transfers[-10:]:  # Show last 10
                date_str = transfer['date'].strftime('%Y-%m-%d %H:%M')
                print(f"{date_str:<20} {transfer['from_account']:<15} {transfer['to_account']:<15} ${transfer['amount']:<10.2f} {transfer['transfer_id']:<10}")
            
            if len(transfers) > 10:
                print(f"\n(Showing last 10 of {len(transfers)} transfers)")
            
        except Exception as e:
            print(f"❌ Error retrieving transfer history: {e}")
        
        input("\nPress Enter to continue...")
    
    # Transaction History Operations
    def _view_all_transactions(self):
        """View all transactions"""
        print("\n📊 All Transactions")
        
        try:
            result = self.user.get_transaction_history(page_size=20)
            transactions = result['transactions']
            
            if not transactions:
                print("No transactions found.")
                input("Press Enter to continue...")
                return
            
            self._display_transactions(transactions, result)
            
        except Exception as e:
            print(f"❌ Error retrieving transactions: {e}")
        
        input("\nPress Enter to continue...")
    
    def _filter_by_account(self):
        """Filter transactions by account"""
        print("\n🏦 Filter by Account")
        
        if not self.user.accounts:
            print("No accounts found.")
            input("Press Enter to continue...")
            return
        
        # Select account
        account = self._select_account("Select account to filter by:")
        if not account:
            return
        
        try:
            result = self.user.get_transaction_history(account=account.account_type, page_size=20)
            transactions = result['transactions']
            
            if not transactions:
                print(f"No transactions found for {account.get_display_name()}.")
                input("Press Enter to continue...")
                return
            
            print(f"\nTransactions for {account.get_display_name()}:")
            self._display_transactions(transactions, result)
            
        except Exception as e:
            print(f"❌ Error retrieving transactions: {e}")
        
        input("\nPress Enter to continue...")
    
    def _filter_by_date(self):
        """Filter transactions by date range"""
        print("\n📅 Filter by Date Range")
        
        # Get start date
        start_date = None
        start_input = input("Enter start date (YYYY-MM-DD, leave empty for all): ").strip()
        if start_input:
            try:
                start_date = datetime.strptime(start_input, '%Y-%m-%d')
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD")
                input("Press Enter to continue...")
                return
        
        # Get end date
        end_date = None
        end_input = input("Enter end date (YYYY-MM-DD, leave empty for all): ").strip()
        if end_input:
            try:
                end_date = datetime.strptime(end_input, '%Y-%m-%d')
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD")
                input("Press Enter to continue...")
                return
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            print("❌ Start date cannot be after end date.")
            input("Press Enter to continue...")
            return
        
        try:
            result = self.user.get_transaction_history(
                start_date=start_date, end_date=end_date, page_size=20
            )
            transactions = result['transactions']
            
            if not transactions:
                print("No transactions found for the specified date range.")
                input("Press Enter to continue...")
                return
            
            date_range = ""
            if start_date:
                date_range += f"from {start_date.strftime('%Y-%m-%d')} "
            if end_date:
                date_range += f"to {end_date.strftime('%Y-%m-%d')}"
            
            print(f"\nTransactions {date_range}:")
            self._display_transactions(transactions, result)
            
        except Exception as e:
            print(f"❌ Error retrieving transactions: {e}")
        
        input("\nPress Enter to continue...")
    
    def _filter_by_type(self):
        """Filter transactions by type"""
        print("\n🏷️  Filter by Transaction Type")
        
        print("Available transaction types:")
        print("1. Deposits")
        print("2. Withdrawals")
        print("3. Transfers")
        
        while True:
            choice = input("Select transaction type (1-3): ").strip()
            if choice == '1':
                transaction_types = ['deposit']
                type_name = "Deposits"
                break
            elif choice == '2':
                transaction_types = ['withdrawal']
                type_name = "Withdrawals"
                break
            elif choice == '3':
                transaction_types = ['transfer']
                type_name = "Transfers"
                break
            else:
                print("❌ Invalid choice. Please select 1-3.")
        
        try:
            result = self.user.get_transaction_history(page_size=20)
            all_transactions = result['transactions']
            
            # Filter by type
            filtered_transactions = self.user.filter_transactions(
                all_transactions, {'transaction_types': transaction_types}
            )
            
            if not filtered_transactions:
                print(f"No {type_name.lower()} found.")
                input("Press Enter to continue...")
                return
            
            print(f"\n{type_name}:")
            # Create a mock result for display
            filtered_result = {
                'transactions': filtered_transactions,
                'total_count': len(filtered_transactions),
                'page': 1,
                'total_pages': 1,
                'has_previous': False,
                'has_next': False
            }
            self._display_transactions(filtered_transactions, filtered_result)
            
        except Exception as e:
            print(f"❌ Error retrieving transactions: {e}")
        
        input("\nPress Enter to continue...")
    
    def _transaction_summary(self):
        """Show transaction summary"""
        print("\n📈 Transaction Summary")
        
        try:
            summary = self.user.get_transaction_summary()
            
            print(f"\n=== Transaction Summary ===")
            print(f"Total Transactions: {summary['total_transactions']}")
            print(f"Total Deposits: ${summary['total_deposits']:.2f}")
            print(f"Total Withdrawals: ${summary['total_withdrawals']:.2f}")
            print(f"Total Transfers In: ${summary['total_transfers_in']:.2f}")
            print(f"Total Transfers Out: ${summary['total_transfers_out']:.2f}")
            print("-" * 40)
            print(f"Net Change: ${summary['net_change']:.2f}")
            print("=" * 40)
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
        
        input("\nPress Enter to continue...")
    
    def _export_transactions(self):
        """Export transactions to file"""
        print("\n💾 Export Transactions")
        
        print("Export formats:")
        print("1. CSV")
        print("2. JSON")
        
        while True:
            choice = input("Select format (1-2): ").strip()
            if choice == '1':
                export_format = 'csv'
                break
            elif choice == '2':
                export_format = 'json'
                break
            else:
                print("❌ Invalid choice. Please select 1-2.")
        
        try:
            result = self.user.get_transaction_history(page_size=1000)  # Get more for export
            transactions = result['transactions']
            
            if not transactions:
                print("No transactions to export.")
                input("Press Enter to continue...")
                return
            
            exported_data = self.user.export_transactions(transactions, export_format)
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            
            with open(filename, 'w') as f:
                f.write(exported_data)
            
            print(f"✓ {len(transactions)} transactions exported to {filename}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
        
        input("\nPress Enter to continue...")
    
    # Settings Operations
    def _update_nicknames(self):
        """Update account nicknames"""
        print("\n🏷️  Update Account Nicknames")
        
        if not self.user.accounts:
            print("No accounts found.")
            input("Press Enter to continue...")
            return
        
        # Show current nicknames
        print("\nCurrent account nicknames:")
        for i, account in enumerate(self.user.accounts, 1):
            nickname = account.nickname or "None"
            print(f"{i}. {account.account_type.capitalize()}: {nickname}")
        
        # Select account to update
        while True:
            try:
                choice = input(f"\nSelect account to update (1-{len(self.user.accounts)}): ").strip()
                account_idx = int(choice) - 1
                if 0 <= account_idx < len(self.user.accounts):
                    selected_account = self.user.accounts[account_idx]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(self.user.accounts)}")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Update nickname
        current_nickname = selected_account.nickname or "None"
        print(f"\nCurrent nickname: {current_nickname}")
        new_nickname = input("Enter new nickname (leave empty to remove): ").strip()
        
        if new_nickname:
            selected_account.update_nickname(new_nickname)
            print(f"✓ Nickname updated to: {new_nickname}")
        elif selected_account.nickname:
            selected_account.update_nickname(None)
            print("✓ Nickname removed")
        else:
            print("No changes made.")
        
        input("\nPress Enter to continue...")
    
    def _change_account_settings(self):
        """Change account settings"""
        print("\n⚙️  Change Account Settings")
        print("This feature will be expanded in future updates.")
        print("Currently available: Account nickname updates (option 1 in this menu)")
        input("\nPress Enter to continue...")
    
    def _view_profile(self):
        """View profile information"""
        print("\n👤 Profile Information")
        print("-" * 30)
        print(f"Username: {self.user.username}")
        print(f"Email: {self.user.email}")
        print(f"Total Accounts: {len(self.user.accounts)}")
        
        if self.user.accounts:
            total_balance = sum(account.balance for account in self.user.accounts)
            print(f"Total Balance: ${total_balance:.2f}")
        
        print(f"Member since: Account creation date not tracked")
        input("\nPress Enter to continue...")
    
    def _session_info(self):
        """Display session information"""
        print("\n🕐 Session Information")
        print("-" * 30)
        
        session_duration = datetime.now() - self.session_start
        minutes_active = int(session_duration.total_seconds() / 60)
        
        time_since_activity = datetime.now() - self.last_activity
        minutes_inactive = int(time_since_activity.total_seconds() / 60)
        
        print(f"Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Session duration: {minutes_active} minutes")
        print(f"Last activity: {minutes_inactive} minutes ago")
        print(f"Session timeout: {self.SESSION_TIMEOUT_MINUTES} minutes")
        print(f"Warning threshold: {self.INACTIVITY_WARNING_MINUTES} minutes")
        
        remaining = self.SESSION_TIMEOUT_MINUTES - minutes_inactive
        if remaining > 0:
            print(f"Time until timeout: {remaining} minutes")
        else:
            print("⚠️  Session should have timed out!")
        
        input("\nPress Enter to continue...")
    
    # Helper Methods
    def _select_account(self, prompt, accounts=None):
        """Helper method to select an account from a list"""
        if accounts is None:
            accounts = self.user.accounts
        
        if not accounts:
            print("No accounts available.")
            return None
        
        print(f"\n{prompt}")
        for i, account in enumerate(accounts, 1):
            print(f"{i}. {account.get_display_name()} (${account.balance:.2f})")
        
        while True:
            try:
                choice = input(f"Select account (1-{len(accounts)}): ").strip()
                account_idx = int(choice) - 1
                if 0 <= account_idx < len(accounts):
                    return accounts[account_idx]
                else:
                    print(f"❌ Please enter a number between 1 and {len(accounts)}")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def _display_transactions(self, transactions, result_info):
        """Helper method to display transaction list"""
        print(f"\nShowing {len(transactions)} of {result_info['total_count']} transactions")
        if result_info['total_pages'] > 1:
            print(f"Page {result_info['page']} of {result_info['total_pages']}")
        
        print("-" * 80)
        print(f"{'Date':<20} {'Account':<20} {'Type':<12} {'Amount':<12}")
        print("-" * 80)
        
        for transaction in transactions:
            date_str = transaction['date'].strftime('%Y-%m-%d %H:%M:%S')
            account_name = transaction['account'][:18] + '..' if len(transaction['account']) > 20 else transaction['account']
            amount_str = f"${transaction['amount']:>8.2f}"
            
            print(f"{date_str:<20} {account_name:<20} {transaction['type']:<12} {amount_str:<12}")
        
        print("-" * 80)


def start_interactive_session(user, users_dict):
    """
    Start an interactive session for the given user
    
    Args:
        user: Authenticated User object
        users_dict: Global users dictionary
        
    Returns:
        None
    """
    session = InteractiveSession(user, users_dict)
    session.run_session()