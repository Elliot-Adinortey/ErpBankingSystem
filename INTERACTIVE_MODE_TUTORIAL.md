# Interactive Mode Tutorial

## Overview

Interactive Mode is a menu-driven interface that allows you to perform multiple banking operations within a single authenticated session. Instead of logging in for each command, you login once and navigate through intuitive menus to complete your banking tasks.

## Getting Started

### Starting Interactive Mode

1. **Login and Start Interactive Session**
   ```bash
   python main.py interactive
   ```

2. **You'll see the main menu:**
   ```
   ============================================================
     BANKING SYSTEM - Interactive Mode
     Welcome, [your_username]!
   ============================================================
   1. Account Management
   2. Banking Operations
   3. Transaction History
   4. Account Statements
   5. Settings & Profile
   6. Logout
   ============================================================
   Session active for: 0 minutes
   ============================================================
   ```

### Navigation Basics

- **Select Options**: Type the number (1-6) and press Enter
- **Go Back**: Most submenus have a "Back to Main Menu" option
- **Exit Anytime**: Choose option 6 to logout, or use Ctrl+C to force exit
- **Session Timeout**: Sessions automatically timeout after 30 minutes of inactivity

## Menu Walkthrough

### 1. Account Management

This menu helps you manage your bank accounts:

```
Account Management Menu:
1. List All Accounts
2. Account Summary (Detailed)
3. Financial Overview
4. Create New Account
5. Update Account Settings
6. Back to Main Menu
```

#### Common Tasks:

**View Your Accounts**
- Choose option 1 for a simple list with balances
- Choose option 2 for detailed account information
- Choose option 3 for financial overview with totals

**Create New Account**
- Choose option 4
- Follow prompts for account type, initial balance, and optional overdraft limit
- Optionally set a nickname for easy identification

**Update Account Settings**
- Choose option 5
- Select the account to modify
- Update nickname or overdraft limit

### 2. Banking Operations

This menu handles deposits, withdrawals, and transfers:

```
Banking Operations Menu:
1. Deposit Money
2. Withdraw Money
3. Transfer Between Accounts
4. View Account Balance
5. Back to Main Menu
```

#### Common Tasks:

**Make a Deposit**
- Choose option 1
- Select the account from your list
- Enter the deposit amount
- Confirm the transaction

**Withdraw Money**
- Choose option 2
- Select the account
- Enter withdrawal amount
- System checks available balance (including overdraft)

**Transfer Between Accounts**
- Choose option 3
- Select source account (where money comes from)
- Select destination account (where money goes to)
- Enter transfer amount
- Optionally add a memo
- Confirm the transfer

### 3. Transaction History

This menu provides access to your transaction records:

```
Transaction History Menu:
1. View Recent Transactions
2. View All Transactions
3. Filter Transactions
4. Transaction Summary
5. Export Transaction Data
6. Back to Main Menu
```

#### Common Tasks:

**View Recent Activity**
- Choose option 1 for last 10 transactions
- Choose option 2 for complete history with pagination

**Filter Transactions**
- Choose option 3
- Set filters for:
  - Specific account
  - Date range
  - Transaction type (deposit, withdrawal, transfer)
  - Amount range

**Get Transaction Summary**
- Choose option 4
- View statistics like total deposits, withdrawals, net change
- Filter by account or date range

**Export Data**
- Choose option 5
- Select format (CSV or JSON)
- Choose what to export (all transactions or filtered set)

### 4. Account Statements

Generate and export formatted account statements:

```
Account Statements Menu:
1. Generate Statement (View)
2. Generate and Export Statement
3. Back to Main Menu
```

#### Common Tasks:

**View Statement**
- Choose option 1
- Select account
- Choose date range (or use default current month)
- View formatted statement on screen

**Export Statement**
- Choose option 2
- Select account and date range
- Choose export format (text or detailed)
- Statement saved to file

### 5. Settings & Profile

Manage your account settings and preferences:

```
Settings & Profile Menu:
1. Update Account Nicknames
2. Modify Overdraft Limits
3. View Session Information
4. Back to Main Menu
```

#### Common Tasks:

**Set Account Nicknames**
- Choose option 1
- Select account to rename
- Enter new nickname (e.g., "Emergency Fund", "Daily Expenses")

**Adjust Overdraft Limits**
- Choose option 2
- Select current account
- Set new overdraft limit

**Check Session Info**
- Choose option 3
- View session duration, timeout warnings, and activity

### 6. Logout

Safely end your interactive session:
- Invalidates your session token
- Clears temporary session data
- Returns to command line

## Interactive Mode Features

### Session Management

**Automatic Timeout Protection**
- Sessions timeout after 30 minutes of inactivity
- Warning appears at 25 minutes
- Automatic logout prevents unauthorized access

**Activity Tracking**
- System tracks your activity
- Session timer resets with each operation
- Current session duration displayed in main menu

### Error Handling

**Helpful Error Messages**
- Clear explanations when operations fail
- Suggestions for fixing common issues
- Option to retry failed operations

**Input Validation**
- Validates account names, amounts, and dates
- Shows available options when input is invalid
- Prevents invalid operations before execution

### User Experience Features

**Smart Account Selection**
- Shows account nicknames alongside types
- Displays current balances for context
- Validates account existence before operations

**Operation Confirmation**
- Confirms important operations (transfers, large withdrawals)
- Shows updated balances after transactions
- Provides transaction IDs for record keeping

**Progress Feedback**
- Shows operation status (processing, completed, failed)
- Displays results immediately
- Provides next step suggestions

## Tips for Effective Use

### Daily Banking Routine

1. **Start with Overview**
   - Main Menu → 1 (Account Management) → 3 (Financial Overview)
   - Get snapshot of all account balances and recent activity

2. **Review Recent Activity**
   - Main Menu → 3 (Transaction History) → 1 (Recent Transactions)
   - Check for any unexpected transactions

3. **Perform Banking Operations**
   - Use Menu 2 for deposits, withdrawals, transfers
   - Take advantage of guided prompts and validation

4. **Monthly Review**
   - Generate statements for record keeping
   - Export transaction data for analysis
   - Update account settings as needed

### Efficiency Tips

**Use Nicknames**
- Set meaningful nicknames for accounts
- Makes account selection faster and clearer
- Examples: "Emergency Fund", "Daily Expenses", "Vacation Savings"

**Batch Similar Operations**
- Do all deposits/withdrawals in one session
- Use transfer menu for fund allocation
- Export data at the end of session

**Take Advantage of Filters**
- Use transaction filters to find specific transactions
- Filter by date range for monthly reviews
- Export filtered data for targeted analysis

### Security Best Practices

**Session Hygiene**
- Always logout when finished (Menu option 6)
- Don't leave interactive sessions unattended
- Pay attention to timeout warnings

**Verify Operations**
- Review account balances after transactions
- Check transaction confirmations
- Use transaction history to verify operations

**Safe Environment**
- Use interactive mode only on trusted devices
- Ensure privacy when entering sensitive information
- Log out if you need to step away

## Troubleshooting

### Common Issues

**Menu Not Responding**
- Press Enter to refresh the display
- Type a valid menu number (1-6)
- Use Ctrl+C to force exit if needed

**Session Timeout**
- Complete current operation quickly
- Restart interactive mode if session expires
- Login again and resume operations

**Invalid Account Names**
- Use Account Management menu to see available accounts
- Check account nicknames vs. account types
- Verify spelling of account identifiers

**Operation Failures**
- Read error messages carefully
- Check account balances and limits
- Verify input formats (amounts, dates)
- Use help options in menus

### Getting Help

**In-Menu Help**
- Most menus include help options
- Error messages provide specific guidance
- Use "Back to Main Menu" to restart navigation

**Command Line Help**
- Exit interactive mode and use: `python main.py help interactive`
- Get specific command help: `python main.py help [command]`
- Check system status: `python main.py status`

### Recovery Procedures

**If Session Becomes Unresponsive**
1. Try pressing Enter to refresh
2. Use Ctrl+C to force exit
3. Login again: `python main.py interactive`

**If Operations Fail Repeatedly**
1. Exit interactive mode
2. Check login status: `python main.py status`
3. Try individual commands to isolate issue
4. Restart interactive mode

**If Data Seems Incorrect**
1. Use Account Management → Account Summary to verify data
2. Check Transaction History for recent changes
3. Exit and use command line to verify: `python main.py list_accounts`

## Advanced Interactive Features

### Keyboard Shortcuts

- **Ctrl+C**: Force exit (emergency exit)
- **Enter**: Refresh current menu display
- **Numbers 1-6**: Quick menu selection

### Session Information

The main menu displays:
- Current username
- Session duration
- Timeout warnings (when approaching 30-minute limit)
- Last activity timestamp

### Integration with Command Line

You can switch between interactive mode and command line:
1. Exit interactive mode (option 6)
2. Run individual commands as needed
3. Return to interactive mode: `python main.py interactive`

Your session token remains valid for both modes until logout or timeout.

---

## Conclusion

Interactive Mode provides a user-friendly way to manage your banking operations efficiently. By learning the menu structure and following the tips in this tutorial, you can perform complex banking tasks with ease while maintaining security and accuracy.

For additional help, use the built-in help system or refer to the main Usage Guide for detailed command information.