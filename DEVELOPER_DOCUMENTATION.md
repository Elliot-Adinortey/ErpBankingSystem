# Banking System - Developer Documentation

## Overview

This document provides technical documentation for developers working on the banking system, covering the enhanced architecture, new components, APIs, and development guidelines implemented in Priority 2 user experience enhancements.

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface Layer                       │
├─────────────────────┬───────────────────────────────────────┤
│   Interactive Mode  │        Enhanced CLI Commands          │
│   - Menu System     │        - Account Summary              │
│   - Session Mgmt    │        - Transaction History          │
│   - User Input      │        - Transfer Operations          │
└─────────────────────┴───────────────────────────────────────┤
│                    Business Logic Layer                     │
├─────────────────────────────────────────────────────────────┤
│   Account Manager   │   Transaction Manager │  Audit Logger │
│   - Transfers       │   - History Filtering │  - Operation  │
│   - Nicknames       │   - Batch Processing  │    Tracking   │
│   - Statements      │   - Export/Import     │  - Error Log  │
└─────────────────────────────────────────────────────────────┤
│                 Existing Security & Data Layer              │
│   Session Management │ Password Security │ Data Backup      │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

```
src/
├── core/                    # Core business logic
│   ├── user.py             # Enhanced User class with new methods
│   ├── account.py          # Enhanced Account class with nicknames
│   └── transaction.py      # Transaction handling and history
├── managers/               # Business logic managers
│   ├── transaction_manager.py  # Transaction filtering and export
│   ├── transfer_manager.py     # Transfer operations
│   └── batch_manager.py        # Batch operation processing
├── ui/                     # User interface components
│   └── interactive_session.py  # Interactive mode implementation
└── utils/                  # Utility modules
    ├── audit_logger.py     # Comprehensive audit logging
    ├── error_handler.py    # Enhanced error handling
    ├── help_system.py      # Command help system
    ├── statement_generator.py  # Account statement generation
    └── data_export_import.py   # Data export/import functionality
```

## Core Components

### Enhanced User Class

**File:** `src/core/user.py`

#### New Methods

```python
class User:
    def get_enhanced_summary(self) -> dict:
        """
        Get comprehensive account summary with detailed information
        
        Returns:
            dict: Summary containing account details, balances, and statistics
        """
    
    def get_financial_overview(self) -> dict:
        """
        Get financial overview with totals and recent activity
        
        Returns:
            dict: Financial overview with totals and recent transactions
        """
    
    def transfer_between_accounts(self, from_account: str, to_account: str, 
                                amount: float, memo: str = None) -> tuple:
        """
        Transfer money between user's accounts
        
        Args:
            from_account: Source account identifier
            to_account: Destination account identifier
            amount: Transfer amount
            memo: Optional transfer memo
            
        Returns:
            tuple: (success: bool, message: str, transfer_id: str)
        """
    
    def get_transaction_history(self, account: str = None, start_date: datetime = None,
                              end_date: datetime = None, page: int = 1, 
                              page_size: int = 50) -> dict:
        """
        Get paginated transaction history with filtering
        
        Args:
            account: Filter by specific account
            start_date: Filter start date
            end_date: Filter end date
            page: Page number for pagination
            page_size: Number of transactions per page
            
        Returns:
            dict: Paginated transaction results with metadata
        """
    
    def filter_transactions(self, transactions: list, filters: dict) -> list:
        """
        Apply additional filters to transaction list
        
        Args:
            transactions: List of transactions to filter
            filters: Dictionary of filter criteria
            
        Returns:
            list: Filtered transactions
        """
    
    def get_transaction_summary(self, account: str = None, start_date: datetime = None,
                              end_date: datetime = None) -> dict:
        """
        Get transaction summary statistics
        
        Args:
            account: Filter by specific account
            start_date: Summary start date
            end_date: Summary end date
            
        Returns:
            dict: Summary statistics
        """
```

#### Usage Examples

```python
# Get enhanced account summary
user = User("john", "hashed_password", "john@example.com")
summary = user.get_enhanced_summary()
print(f"Total accounts: {summary['total_accounts']}")
print(f"Total balance: ${summary['total_balance']:.2f}")

# Transfer between accounts
success, message, transfer_id = user.transfer_between_accounts(
    "savings", "current", 100.0, "Monthly transfer"
)
if success:
    print(f"Transfer successful: {transfer_id}")

# Get transaction history with pagination
history = user.get_transaction_history(
    account="savings",
    start_date=datetime(2024, 1, 1),
    page=1,
    page_size=20
)
print(f"Page {history['page']} of {history['total_pages']}")
```

### Enhanced Account Class

**File:** `src/core/account.py`

#### New Features

```python
class Account:
    def __init__(self, account_type: str, balance: float = 0, 
                 overdraft_limit: float = 0, nickname: str = None):
        """
        Enhanced Account constructor with nickname support
        
        Args:
            account_type: Type of account (savings, current, salary)
            balance: Initial balance
            overdraft_limit: Overdraft limit for current accounts
            nickname: Optional account nickname
        """
        self.nickname = nickname
        self.created_date = datetime.now()
        self.last_activity = datetime.now()
    
    def get_display_name(self) -> str:
        """
        Get display name including nickname if available
        
        Returns:
            str: Display name in format "Nickname (type)" or just "type"
        """
    
    def update_nickname(self, nickname: str) -> None:
        """Update account nickname"""
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
    
    def get_available_balance(self) -> float:
        """Get available balance including overdraft"""
```

## Manager Classes

### TransactionManager

**File:** `src/managers/transaction_manager.py`

```python
class TransactionManager:
    """Manages transaction history, filtering, and export operations"""
    
    def __init__(self, user: User):
        self.user = user
    
    def get_filtered_transactions(self, filters: dict) -> list:
        """
        Get transactions with applied filters
        
        Args:
            filters: Dictionary containing filter criteria:
                - account: str - Filter by account
                - start_date: datetime - Start date filter
                - end_date: datetime - End date filter
                - transaction_types: list - Filter by transaction types
                - min_amount: float - Minimum amount filter
                - max_amount: float - Maximum amount filter
        
        Returns:
            list: Filtered transactions
        """
    
    def export_transactions(self, transactions: list, format: str) -> str:
        """
        Export transactions to specified format
        
        Args:
            transactions: List of transactions to export
            format: Export format ('csv' or 'json')
            
        Returns:
            str: Exported data as string
        """
    
    def get_transaction_statistics(self, transactions: list) -> dict:
        """
        Calculate statistics for transaction list
        
        Args:
            transactions: List of transactions
            
        Returns:
            dict: Statistics including totals, averages, counts
        """
```

### TransferManager

**File:** `src/managers/transfer_manager.py`

```python
class TransferManager:
    """Manages account-to-account transfer operations"""
    
    def __init__(self, user: User):
        self.user = user
    
    def validate_transfer(self, from_account: str, to_account: str, 
                         amount: float) -> tuple:
        """
        Validate transfer parameters
        
        Args:
            from_account: Source account identifier
            to_account: Destination account identifier
            amount: Transfer amount
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
    
    def execute_transfer(self, from_account: str, to_account: str, 
                        amount: float, memo: str = None) -> tuple:
        """
        Execute validated transfer
        
        Args:
            from_account: Source account identifier
            to_account: Destination account identifier
            amount: Transfer amount
            memo: Optional transfer memo
            
        Returns:
            tuple: (success: bool, message: str, transfer_id: str)
        """
    
    def generate_transfer_id(self) -> str:
        """Generate unique transfer ID"""
```

### BatchManager

**File:** `src/managers/batch_manager.py`

```python
class BatchManager:
    """Manages batch operation processing"""
    
    def __init__(self, user: User):
        self.user = user
    
    def validate_batch_file(self, filepath: str) -> tuple:
        """
        Validate batch operation file
        
        Args:
            filepath: Path to batch file
            
        Returns:
            tuple: (is_valid: bool, errors: list, operations: list)
        """
    
    def execute_batch_operations(self, operations: list, preview: bool = False) -> dict:
        """
        Execute batch operations
        
        Args:
            operations: List of operation dictionaries
            preview: If True, validate only without executing
            
        Returns:
            dict: Execution results with success/failure counts
        """
    
    def create_batch_template(self, operation_types: list) -> dict:
        """
        Create batch operation template
        
        Args:
            operation_types: List of operation types to include
            
        Returns:
            dict: Template structure for batch operations
        """
```

## Interactive Mode System

### InteractiveSession Class

**File:** `src/ui/interactive_session.py`

```python
class InteractiveSession:
    """Manages interactive menu-driven banking sessions"""
    
    SESSION_TIMEOUT_MINUTES = 30
    INACTIVITY_WARNING_MINUTES = 25
    
    def __init__(self, user: User, users_dict: dict):
        """
        Initialize interactive session
        
        Args:
            user: Authenticated User object
            users_dict: Global users dictionary for saving changes
        """
    
    def display_main_menu(self) -> None:
        """Display main menu with session information"""
    
    def handle_menu_selection(self, choice: str) -> bool:
        """
        Handle menu selection and route to appropriate handler
        
        Args:
            choice: User's menu choice
            
        Returns:
            bool: True to continue session, False to exit
        """
    
    def run_session(self) -> None:
        """Main session loop with timeout handling"""
    
    def _check_session_timeout(self) -> bool:
        """Check if session has timed out"""
    
    def _should_show_timeout_warning(self) -> bool:
        """Determine if timeout warning should be shown"""
```

#### Menu Handler Methods

```python
def _handle_account_management(self) -> bool:
    """Handle account management submenu"""

def _handle_banking_operations(self) -> bool:
    """Handle banking operations submenu"""

def _handle_transaction_history(self) -> bool:
    """Handle transaction history submenu"""

def _handle_account_statements(self) -> bool:
    """Handle account statements submenu"""

def _handle_settings(self) -> bool:
    """Handle settings and profile submenu"""
```

## Utility Components

### AuditLogger

**File:** `src/utils/audit_logger.py`

```python
class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = log_file
    
    def log_login_attempt(self, username: str, success: bool, 
                         session_id: str = None, failure_reason: str = None) -> None:
        """Log login attempts with success/failure tracking"""
    
    def log_logout(self, username: str, session_id: str) -> None:
        """Log user logout events"""
    
    def log_banking_operation(self, operation_type: str, user: str, 
                            account_identifier: str, amount: float = None,
                            success: bool = True, session_id: str = None,
                            additional_details: dict = None) -> None:
        """Log banking operations with full context"""
    
    def log_operation(self, event_type: AuditEventType, user: str, 
                     operation: str, success: bool = True,
                     session_id: str = None, details: dict = None) -> None:
        """Log general operations"""
    
    def log_error(self, error: Exception, context: dict = None,
                 user: str = None, session_id: str = None) -> None:
        """Log errors with context information"""
```

### ErrorHandler

**File:** `src/utils/error_handler.py`

```python
class ErrorHandler:
    """Enhanced error handling with context-aware messages"""
    
    @staticmethod
    def handle_session_expired() -> str:
        """Handle session expiration with helpful message"""
    
    @staticmethod
    def handle_insufficient_funds(available: float, requested: float, 
                                account_name: str) -> str:
        """Handle insufficient funds with balance information"""
    
    @staticmethod
    def handle_invalid_account(account_name: str, available_accounts: list) -> str:
        """Handle invalid account with suggestions"""
    
    @staticmethod
    def suggest_command_fix(invalid_command: str, available_commands: list) -> str:
        """Suggest command corrections for invalid input"""
    
    @staticmethod
    def handle_transfer_validation_error(error_type: str, context: dict) -> str:
        """Handle transfer validation errors with specific guidance"""
```

### HelpSystem

**File:** `src/utils/help_system.py`

```python
class HelpSystem:
    """Comprehensive command help and documentation system"""
    
    COMMAND_HELP = {
        # Dictionary containing detailed help for all commands
    }
    
    @staticmethod
    def get_command_help(command: str, detailed: bool = False) -> str:
        """
        Get help text for specific command
        
        Args:
            command: Command name
            detailed: Whether to return detailed help
            
        Returns:
            str: Help text for command
        """
    
    @staticmethod
    def get_all_commands() -> list:
        """Get list of all available commands"""
    
    @staticmethod
    def search_commands(query: str) -> list:
        """Search commands by keyword"""
```

## Data Export/Import System

### DataExportImportManager

**File:** `src/utils/data_export_import.py`

```python
class DataExportImportManager:
    """Manages data export and import operations"""
    
    def __init__(self, user: User):
        self.user = user
    
    def export_data(self, data_type: str, format: str, **kwargs) -> str:
        """
        Export user data in specified format
        
        Args:
            data_type: Type of data to export ('transactions', 'accounts', 'full_backup')
            format: Export format ('csv', 'json')
            **kwargs: Additional export parameters
            
        Returns:
            str: Path to exported file
        """
    
    def import_data(self, data_type: str, filepath: str, preview: bool = False) -> dict:
        """
        Import data from file
        
        Args:
            data_type: Type of data to import
            filepath: Path to import file
            preview: If True, validate only without importing
            
        Returns:
            dict: Import results with success/failure information
        """
    
    def validate_import_data(self, data_type: str, data: any) -> tuple:
        """
        Validate import data format and content
        
        Args:
            data_type: Type of data being imported
            data: Data to validate
            
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
```

## API Reference

### Command Line Interface

#### New Commands

```bash
# Enhanced account management
python main.py list_accounts                    # List accounts with nicknames
python main.py account_summary                  # Detailed account information
python main.py financial_overview               # Financial overview with totals

# Account-to-account transfers
python main.py transfer <from> <to> <amount> [--memo "text"]

# Transaction history and analysis
python main.py transaction_history [options]
python main.py transaction_summary [options]

# Data export/import
python main.py export_data <type> --format <format> [options]
python main.py import_data <type> <filepath> [options]

# Batch operations
python main.py batch_operations <filepath> [--preview]
python main.py batch_template --operations <types>
python main.py batch_status

# Account statements
python main.py generate_statement <account> [options]

# Interactive mode
python main.py interactive

# Enhanced help
python main.py help [command]
```

#### Command Options

**Transaction History Options:**
```bash
--account <account>          # Filter by account
--start_date <YYYY-MM-DD>    # Start date filter
--end_date <YYYY-MM-DD>      # End date filter
--type <types>               # Filter by transaction types
--min_amount <amount>        # Minimum amount filter
--max_amount <amount>        # Maximum amount filter
--page <number>              # Page number for pagination
--page_size <number>         # Items per page
--sort_by <field>            # Sort by field (date, amount, type, account)
--export_format <format>     # Export format (csv, json)
```

**Export Data Options:**
```bash
--format <format>            # Export format (csv, json)
--account <account>          # Filter by account (for transactions)
--start_date <date>          # Start date filter
--end_date <date>            # End date filter
--filename <filename>        # Custom output filename
```

### Error Codes and Messages

#### Common Error Codes

```python
# Session errors
SESSION_EXPIRED = "Session has expired. Please login again."
SESSION_NOT_FOUND = "No active session found. Please login first."

# Account errors
ACCOUNT_NOT_FOUND = "Account '{account}' not found. Available accounts: {accounts}"
INSUFFICIENT_FUNDS = "Insufficient funds. Available: ${available}, Requested: ${requested}"

# Transfer errors
TRANSFER_SAME_ACCOUNT = "Cannot transfer to the same account"
TRANSFER_INVALID_AMOUNT = "Transfer amount must be positive"

# Data errors
EXPORT_FAILED = "Export operation failed: {reason}"
IMPORT_VALIDATION_FAILED = "Import validation failed: {errors}"

# Batch errors
BATCH_FILE_INVALID = "Batch file format is invalid: {errors}"
BATCH_OPERATION_FAILED = "Batch operation failed: {operation} - {reason}"
```

## Development Guidelines

### Code Style

1. **Follow PEP 8** for Python code style
2. **Use type hints** for function parameters and return values
3. **Document all public methods** with docstrings
4. **Use meaningful variable names** that describe their purpose
5. **Keep functions focused** on single responsibilities

### Error Handling

1. **Use specific exception types** rather than generic Exception
2. **Provide helpful error messages** with context and suggestions
3. **Log errors appropriately** using the AuditLogger
4. **Validate input parameters** before processing
5. **Handle edge cases** gracefully

### Testing Guidelines

1. **Write unit tests** for all new functionality
2. **Test error conditions** as well as success paths
3. **Use mock objects** for external dependencies
4. **Test interactive mode** components separately
5. **Include integration tests** for complete workflows

### Security Considerations

1. **Validate all user input** before processing
2. **Use session tokens** for authentication
3. **Log security events** appropriately
4. **Protect sensitive data** in logs and exports
5. **Implement proper access controls**

### Performance Guidelines

1. **Use pagination** for large data sets
2. **Implement efficient filtering** algorithms
3. **Cache frequently accessed data** when appropriate
4. **Optimize database queries** (for future database integration)
5. **Monitor memory usage** for large operations

## Extension Points

### Adding New Commands

1. **Create command handler** function in `main.py`
2. **Add argument parser** configuration
3. **Implement business logic** in appropriate manager class
4. **Add help text** to HelpSystem
5. **Add audit logging** for the operation
6. **Write tests** for the new functionality

### Adding New Interactive Menus

1. **Create menu handler** method in InteractiveSession
2. **Add menu display** logic
3. **Implement user input** handling
4. **Add error handling** and validation
5. **Update main menu** to include new option

### Adding New Export Formats

1. **Extend DataExportImportManager** with new format handler
2. **Implement format-specific** export logic
3. **Add validation** for the new format
4. **Update command line** options
5. **Add format to help** documentation

### Adding New Audit Events

1. **Define new AuditEventType** in audit_logger.py
2. **Implement logging method** for the event type
3. **Add event logging** to relevant operations
4. **Update audit log** filtering and search
5. **Document the new event** type

## Database Integration (Future)

### Preparation for Database Migration

The current JSON-based storage can be migrated to a database system:

1. **Abstract data access** through repository pattern
2. **Define database schema** based on current JSON structure
3. **Implement migration scripts** for existing data
4. **Add database connection** management
5. **Update all data access** to use database queries

### Recommended Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    account_type VARCHAR(20) NOT NULL,
    nickname VARCHAR(100),
    balance DECIMAL(10,2) DEFAULT 0,
    overdraft_limit DECIMAL(10,2) DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    memo TEXT,
    transfer_id VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100),
    operation VARCHAR(255) NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    details JSON,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Conclusion

This developer documentation provides a comprehensive guide to the enhanced banking system architecture and components. The modular design allows for easy extension and maintenance while providing robust functionality for banking operations.

For additional technical details, refer to the source code comments and docstrings in each module.