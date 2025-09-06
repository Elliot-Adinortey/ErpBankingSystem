# Banking System - Usage Guide

## Quick Start

### 1. First Time Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Register a new user
python main.py register myusername MySecurePass123 my@email.com
```

### 2. Login and Basic Operations
```bash
# Login (creates session token)
python main.py login myusername MySecurePass123

# Check login status
python main.py status

# Create accounts (with optional nicknames)
python main.py add_account savings 1000
python main.py add_account current 500 --overdraft_limit 200

# View all accounts with enhanced display
python main.py list_accounts
python main.py account_summary
python main.py financial_overview

# Banking operations
python main.py deposit savings 250
python main.py withdraw current 100
python main.py view_balance savings

# Transfer between accounts
python main.py transfer savings current 100 --memo "Monthly transfer"

# Logout when done
python main.py logout
```

### 3. Interactive Mode (New!)
```bash
# Start interactive session - login once, perform multiple operations
python main.py interactive

# Follow the menu-driven interface for easy navigation
```

## All Available Commands

### User Management
| Command | Description | Example |
|---------|-------------|---------|
| `register` | Create new user account | `python main.py register john Pass123 john@email.com` |
| `login` | Login and create session | `python main.py login john Pass123` |
| `logout` | Logout and end session | `python main.py logout` |
| `status` | Check login status | `python main.py status` |

### Account Management
| Command | Description | Example |
|---------|-------------|---------|
| `add_account` | Create new bank account | `python main.py add_account savings 1000` |
| `list_accounts` | Show all accounts with nicknames | `python main.py list_accounts` |
| `account_summary` | Detailed account information | `python main.py account_summary` |
| `financial_overview` | Total balances and recent activity | `python main.py financial_overview` |
| `view_balance` | Check specific account balance | `python main.py view_balance savings` |
| `update_account_settings` | Modify account settings | `python main.py update_account_settings savings --nickname "Emergency Fund"` |

### Banking Operations
| Command | Description | Example |
|---------|-------------|---------|
| `deposit` | Add money to account | `python main.py deposit savings 500` |
| `withdraw` | Remove money from account | `python main.py withdraw current 200` |
| `transfer` | Transfer between your accounts | `python main.py transfer savings current 100 --memo "Monthly transfer"` |

### Transaction History & Analysis
| Command | Description | Example |
|---------|-------------|---------|
| `transaction_history` | View transaction history with filters | `python main.py transaction_history --account savings --start_date 2024-01-01` |
| `transaction_summary` | Transaction statistics and summaries | `python main.py transaction_summary --start_date 2024-01-01` |

### Statements & Reports
| Command | Description | Example |
|---------|-------------|---------|
| `generate_statement` | Create account statements | `python main.py generate_statement savings --start_date 2024-01-01 --format text` |
| `export_data` | Export account/transaction data | `python main.py export_data transactions --format csv --account savings` |
| `import_data` | Import transaction data | `python main.py import_data transactions data.csv` |

### Batch Operations
| Command | Description | Example |
|---------|-------------|---------|
| `batch_operations` | Process multiple operations from file | `python main.py batch_operations operations.json` |
| `batch_template` | Create batch operation template | `python main.py batch_template --operations deposit,withdraw` |
| `batch_status` | View batch operation history | `python main.py batch_status` |

### Interactive Mode
| Command | Description | Example |
|---------|-------------|---------|
| `interactive` | Start menu-driven session | `python main.py interactive` |

### Help & Support
| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show detailed command help | `python main.py help transfer` |

### Password Management
| Command | Description | Example |
|---------|-------------|---------|
| `reset_password_init` | Start password reset | `python main.py reset_password_init john` |
| `reset_password_complete` | Complete password reset | `python main.py reset_password_complete TOKEN newpass` |

## Account Types & Features

### Savings Account
- Standard savings account
- No overdraft facility
- Supports nicknames for easy identification
- Example: `python main.py add_account savings 1000`

### Current Account
- Checking account with overdraft option
- Specify overdraft limit when creating
- Supports transfers and overdraft protection
- Example: `python main.py add_account current 500 --overdraft_limit 200`

### Salary Account
- Salary deposit account
- No overdraft facility
- Perfect for direct deposits
- Example: `python main.py add_account salary 2000`

### Account Nicknames
You can assign nicknames to accounts for easier identification:
```bash
# Update account nickname
python main.py update_account_settings savings --nickname "Emergency Fund"
python main.py update_account_settings current --nickname "Daily Expenses"

# Nicknames appear in account listings
python main.py list_accounts
# Output: Emergency Fund (savings): $1,000.00
#         Daily Expenses (current): $500.00
```

## Interactive Mode

### Starting Interactive Mode
Interactive mode allows you to login once and perform multiple operations through a menu-driven interface:

```bash
python main.py interactive
```

### Interactive Menu Structure
```
Main Menu:
1. Account Management
   - List accounts with nicknames and balances
   - Create new accounts
   - View detailed account information
   - Update account settings (nicknames, overdraft limits)

2. Banking Operations
   - Deposit money
   - Withdraw money
   - Transfer between accounts
   - View balances

3. Transaction History
   - View all transactions
   - Filter by date range, account, or amount
   - Export transaction data
   - Generate transaction summaries

4. Account Statements
   - Generate formatted statements
   - Export statements to files
   - Choose date ranges and formats

5. Settings & Profile
   - Update account nicknames
   - Modify overdraft limits
   - View session information

6. Logout
   - End session and return to command line
```

### Interactive Mode Benefits
- **Single Login**: Authenticate once for multiple operations
- **Menu Navigation**: Easy-to-use numbered menu system
- **Session Management**: Automatic timeout handling with warnings
- **Error Recovery**: Helpful error messages with retry options
- **Guided Operations**: Step-by-step prompts for complex operations

## Account-to-Account Transfers

### Basic Transfer
Transfer money between your own accounts:
```bash
python main.py transfer savings current 100
```

### Transfer with Memo
Add a memo to track transfer purpose:
```bash
python main.py transfer savings current 100 --memo "Monthly budget allocation"
```

### Transfer Validation
The system automatically validates:
- Both accounts exist and belong to you
- Sufficient funds (including overdraft limits)
- Valid transfer amounts
- Account ownership

### Transfer Confirmation
After successful transfer, you'll see:
- Transfer confirmation with unique ID
- Updated balances for both accounts
- Transfer details in transaction history

## Transaction History & Analysis

### Basic History
View all transactions for your accounts:
```bash
python main.py transaction_history
```

### Filtered History
Filter transactions by various criteria:
```bash
# By account
python main.py transaction_history --account savings

# By date range
python main.py transaction_history --start_date 2024-01-01 --end_date 2024-12-31

# By transaction type
python main.py transaction_history --type deposit,withdrawal

# By amount range
python main.py transaction_history --min_amount 100 --max_amount 1000

# Combine filters
python main.py transaction_history --account current --start_date 2024-06-01 --type transfer
```

### Pagination
For large transaction histories:
```bash
# View specific page
python main.py transaction_history --page 2 --page_size 20

# Sort by different criteria
python main.py transaction_history --sort_by amount  # or date, type, account
```

### Transaction Summary
Get statistical summaries:
```bash
# Overall summary
python main.py transaction_summary

# Account-specific summary
python main.py transaction_summary --account savings

# Date range summary
python main.py transaction_summary --start_date 2024-01-01 --end_date 2024-12-31
```

## Data Export & Import

### Export Transaction Data
Export your transaction data in various formats:
```bash
# Export all transactions to CSV
python main.py export_data transactions --format csv

# Export specific account transactions
python main.py export_data transactions --format csv --account savings

# Export with date range
python main.py export_data transactions --format json --start_date 2024-01-01

# Custom filename
python main.py export_data transactions --format csv --filename my_transactions.csv
```

### Export Account Data
Export account information:
```bash
# Export all account data
python main.py export_data accounts --format json

# Full backup (accounts + transactions)
python main.py export_data full_backup --format json
```

### Import Transaction Data
Import transaction data from files:
```bash
# Import from CSV file
python main.py import_data transactions transactions.csv

# Import with validation preview
python main.py import_data transactions transactions.csv --preview
```

## Account Statements

### Generate Statements
Create formatted account statements:
```bash
# Basic statement for account
python main.py generate_statement savings

# Statement for date range
python main.py generate_statement savings --start_date 2024-01-01 --end_date 2024-12-31

# Export statement to file
python main.py generate_statement savings --export --filename statement.txt

# Different formats
python main.py generate_statement savings --format detailed --export
```

## Batch Operations

### Create Batch Template
Generate template files for batch operations:
```bash
# Create template for multiple operation types
python main.py batch_template --operations deposit,withdraw,transfer

# Specify output file
python main.py batch_template --operations deposit --filename my_batch.json
```

### Process Batch Operations
Execute multiple operations from a file:
```bash
# Process batch file
python main.py batch_operations batch_file.json

# Preview mode (validate without executing)
python main.py batch_operations batch_file.json --preview
```

### Batch Status
View batch operation history:
```bash
python main.py batch_status
```

## Session Management

### How Sessions Work
1. **Login** creates a session token (valid for 2 hours)
2. **Token** is automatically saved to `.session` file
3. **Operations** use the saved token automatically
4. **Logout** invalidates the token and removes the file
5. **Interactive mode** maintains session throughout the session

### Manual Token Usage
If you need to use a specific token:
```bash
python main.py deposit savings 100 --token YOUR_TOKEN_HERE
```

### Session Troubleshooting
```bash
# Check if you're logged in
python main.py status

# If session expired, login again
python main.py login username password

# If having issues, logout and login fresh
python main.py logout
python main.py login username password
```

## Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one number
- Valid email format required

### Data Protection
- Passwords are hashed with bcrypt
- Automatic backups before each save
- Session tokens expire after 2 hours
- Data integrity validation on load

## Error Messages & Troubleshooting

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "No session token found" | Not logged in | Run `python main.py login username password` |
| "Invalid or expired session" | Session timeout | Login again |
| "User not found" | Wrong username | Check spelling or register new user |
| "Incorrect password" | Wrong password | Check password or use password reset |
| "Account not found" | Account doesn't exist | Use `list_accounts` to see available accounts |
| "Insufficient funds" | Not enough money | Check balance with `view_balance` or `account_summary` |
| "Transfer validation failed" | Invalid transfer parameters | Check account names and available balance |
| "Invalid date format" | Wrong date format in commands | Use YYYY-MM-DD format (e.g., 2024-01-15) |
| "Batch operation failed" | Error in batch file | Check batch file format and validate operations |
| "Export/Import error" | File access or format issues | Check file permissions and format specifications |

### Enhanced Error Handling

The system now provides more helpful error messages:

- **Suggested Commands**: When you use invalid commands, the system suggests correct alternatives
- **Available Options**: Error messages show available accounts, valid formats, etc.
- **Context Help**: Errors include relevant help text and examples
- **Recovery Instructions**: Clear steps to resolve common issues

### Interactive Mode Troubleshooting

| Issue | Solution |
|-------|----------|
| Menu not responding | Press Enter or type a valid menu number (1-6) |
| Session timeout warning | Complete current operation quickly or restart session |
| Operation failed in menu | Check error message and retry with correct parameters |
| Can't exit interactive mode | Use menu option 6 or Ctrl+C to force exit |

### Transaction History Issues

| Issue | Solution |
|-------|----------|
| No transactions found | Check date range and account filters |
| Large history slow to load | Use pagination with `--page` and `--page_size` |
| Export fails | Check file permissions and available disk space |
| Date filter not working | Use YYYY-MM-DD format for dates |

### Transfer Problems

| Issue | Solution |
|-------|----------|
| Transfer between accounts fails | Verify both accounts exist with `list_accounts` |
| Insufficient funds error | Check available balance including overdraft |
| Transfer not showing in history | Wait a moment and check both account histories |
| Invalid account names | Use exact account type names (savings, current, salary) |

## Tips and Best Practices

### Daily Usage
1. **Use Interactive Mode** for multiple operations - login once, do everything
2. **Set Account Nicknames** for easier identification and management
3. **Use `account_summary`** for comprehensive account overview
4. **Check `financial_overview`** for total balance and recent activity
5. **Regular Transaction Reviews** with `transaction_history` and filters
6. **Export Data Regularly** for personal record keeping

### Efficient Workflows
1. **Morning Routine**: `interactive` → Account Summary → Recent Transactions
2. **Monthly Review**: Generate statements and export transaction data
3. **Budget Management**: Use transfer commands for fund allocation
4. **Batch Operations**: Use batch files for repetitive tasks

### Security Tips
1. **Use strong passwords** meeting all requirements
2. **Don't share session tokens** with others
3. **Logout** when using shared computers
4. **Keep backups** of important data (automatic backups are created)
5. **Monitor audit logs** for suspicious activity
6. **Use interactive mode** on trusted devices only

### Performance Tips
1. **Use pagination** for large transaction histories
2. **Filter transactions** by date range to improve performance
3. **Export large datasets** rather than viewing in terminal
4. **Use batch operations** for multiple similar transactions

### Troubleshooting
1. **Check status first** when commands fail
2. **Re-login** if session issues occur
3. **Use `help` command** for detailed command information
4. **Check account names** with `list_accounts` or `account_summary`
5. **Use exact account type names**: `savings`, `current`, `salary`
6. **Validate date formats** before using in commands

## File Structure

```
banking-system/
├── main.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── .env                            # Email configuration
├── .gitignore                      # Git ignore rules
├── users_data.json                 # User data (auto-generated)
├── .session                        # Current session token (auto-generated)
├── active_sessions.json            # Session storage (auto-generated)
├── src/                            # Source code modules
│   ├── core/                       # Core business logic
│   │   ├── user.py                 # User management and authentication
│   │   ├── account.py              # Account operations and management
│   │   └── transaction.py          # Transaction handling
│   ├── managers/                   # Business logic managers
│   │   ├── transaction_manager.py  # Transaction history and filtering
│   │   ├── transfer_manager.py     # Account-to-account transfers
│   │   └── batch_manager.py        # Batch operation processing
│   ├── ui/                         # User interface components
│   │   └── interactive_session.py  # Interactive mode interface
│   └── utils/                      # Utility modules
│       ├── security_utils.py       # Security and session management
│       ├── data_storage.py         # Data persistence and backups
│       ├── audit_logger.py         # Operation logging and audit trails
│       ├── error_handler.py        # Enhanced error handling
│       ├── help_system.py          # Command help and documentation
│       ├── statement_generator.py  # Account statement generation
│       ├── data_export_import.py   # Data export/import functionality
│       ├── email_service.py        # Email notifications
│       └── password_reset.py       # Password reset functionality
├── backups/                        # Automatic data backups (auto-generated)
├── logs/                           # System and audit logs (auto-generated)
│   └── audit.log                   # Audit trail log
├── exports/                        # Exported data files (auto-generated)
├── statements/                     # Generated statements (auto-generated)
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   └── integration/                # Integration tests
└── examples/                       # Example scripts and demos
```

## Advanced Usage

### Environment Variables
```bash
# Set session token as environment variable
export SESSION_TOKEN=your_token_here
python main.py deposit savings 100

# Email configuration in .env file
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
```

### Automation and Scripting
```bash
# Automated daily operations
python main.py login john pass123
python main.py financial_overview
python main.py transaction_summary --start_date $(date -d '7 days ago' +%Y-%m-%d)
python main.py export_data transactions --format csv --filename daily_export.csv
python main.py logout

# Batch processing for multiple transactions
python main.py batch_template --operations deposit,transfer --filename monthly_ops.json
# Edit monthly_ops.json with your transactions
python main.py batch_operations monthly_ops.json
```

### Data Management
```bash
# Regular backup routine
python main.py export_data full_backup --format json --filename backup_$(date +%Y%m%d).json

# Monthly statement generation
python main.py generate_statement savings --start_date 2024-01-01 --end_date 2024-01-31 --export

# Transaction analysis
python main.py transaction_history --start_date 2024-01-01 --export_format csv
python main.py transaction_summary --account savings --start_date 2024-01-01
```

### Integration Examples
```bash
# Export for external analysis
python main.py export_data transactions --format csv --filename analysis.csv
# Import the CSV into Excel, Google Sheets, or other tools

# Automated reporting
python main.py financial_overview > monthly_report.txt
python main.py transaction_summary --start_date $(date -d '1 month ago' +%Y-%m-%d) >> monthly_report.txt
```

## Command Reference Quick Guide

### Most Used Commands
```bash
# Quick account overview
python main.py account_summary

# Recent transactions
python main.py transaction_history --page_size 10

# Transfer money
python main.py transfer savings current 100

# Interactive mode (recommended for multiple operations)
python main.py interactive
```

### Data Export Commands
```bash
# Export all transactions
python main.py export_data transactions --format csv

# Export account data
python main.py export_data accounts --format json

# Generate statement
python main.py generate_statement savings --export
```

### Filtering and Analysis
```bash
# Filter by date
python main.py transaction_history --start_date 2024-01-01

# Filter by amount
python main.py transaction_history --min_amount 100

# Get summary statistics
python main.py transaction_summary --account savings
```

---

## Getting Help

### Built-in Help System
```bash
# General help
python main.py -h
python main.py help

# Command-specific help
python main.py help transfer
python main.py help transaction_history
python main.py help interactive

# Detailed command help
python main.py COMMAND -h
```

### Common Help Topics
- **Getting Started**: Use `python main.py help` for overview
- **Interactive Mode**: Use `python main.py help interactive` for menu guide
- **Transfers**: Use `python main.py help transfer` for transfer options
- **Transaction History**: Use `python main.py help transaction_history` for filtering
- **Data Export**: Use `python main.py help export_data` for export formats

### Troubleshooting Resources
1. **Check Status**: `python main.py status` - verify login state
2. **Error Messages**: Read error messages carefully - they include helpful suggestions
3. **Account List**: `python main.py list_accounts` - verify account names
4. **Help Commands**: Use built-in help for command syntax
5. **Interactive Mode**: Try operations in interactive mode for guided experience

### Support and Documentation
- **Usage Guide**: This document covers all features and commands
- **Error Handling**: Enhanced error messages provide specific guidance
- **Interactive Help**: Interactive mode includes contextual help
- **Command Examples**: All commands include usage examples in help text

---

**Need Help?**
- Use `python main.py help` for comprehensive command help
- Use `python main.py help COMMAND` for specific command details
- Try `python main.py interactive` for guided menu-driven operations
- Check error messages for specific guidance and suggestions
- Ensure you're logged in before performing banking operations