# Banking System

A comprehensive banking system with interactive user interface, account management, and secure transaction processing.

## 🚀 Features

- **User Management**: Registration, authentication, and profile management
- **Multiple Account Types**: Savings, Current, and Salary accounts
- **Banking Operations**: Deposits, withdrawals, and account-to-account transfers
- **Interactive Mode**: Menu-driven interface with session management
- **Transaction History**: Filtering, searching, and detailed reporting
- **Security**: Password hashing, session management, and audit logging
- **Data Persistence**: JSON-based storage with automatic backups
- **Email Notifications**: Transaction confirmations and alerts

## 📁 Project Structure

```
banking-system/
├── main.py                          # Main entry point
├── test_reorganized_structure.py    # Structure verification test
├── requirements.txt                 # Project dependencies
├── README.md                        # This file
├── src/                            # Source code
│   ├── core/                       # Core business logic
│   │   ├── user.py                 # User management and operations
│   │   ├── account.py              # Account operations
│   │   └── transaction.py          # Transaction models
│   ├── managers/                   # Business operation managers
│   │   ├── transaction_manager.py  # Transaction history management
│   │   └── transfer_manager.py     # Transfer operations
│   ├── ui/                         # User interface
│   │   └── interactive_session.py  # Interactive mode and menus
│   ├── utils/                      # Utility modules
│   │   ├── data_storage.py         # Data persistence
│   │   ├── email_service.py        # Email notifications
│   │   ├── security_utils.py       # Security and encryption
│   │   ├── password_reset.py       # Password reset functionality
│   │   ├── security.py             # Additional security features
│   │   └── migrate_passwords.py    # Password migration utility
│   └── __init__.py
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   │   └── test_*.py               # Individual component tests
│   ├── integration/                # Integration tests
│   └── __init__.py
├── examples/                       # Demo and example files
│   └── demo_transfer_system.py     # Transfer system demo
├── backups/                        # Data backups
└── .kiro/                          # Project specifications
    └── specs/
```

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd banking-system
   ```

2. **Install dependencies** (optional - uses only Python standard library):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## 💻 Usage

### Command Line Interface

```bash
# Register a new user
python main.py register --username john --password secret123 --email john@example.com

# Login
python main.py login --username john --password secret123

# Start interactive mode (after login)
python main.py interactive

# View help
python main.py --help
```

### Available Commands

- `register` - Register a new user
- `login` - Login to existing account
- `add_account` - Create a new account
- `deposit` - Deposit money
- `withdraw` - Withdraw money
- `transfer` - Transfer between accounts
- `view_balance` - Check account balance
- `list_accounts` - List all accounts
- `account_summary` - Detailed account information
- `financial_overview` - Complete financial summary
- `transaction_history` - View transaction history
- `interactive` - Start interactive mode
- `logout` - End session
- `reset_password_init` - Initiate password reset
- `reset_password_complete` - Complete password reset

### Interactive Mode

After logging in, use the `interactive` command to access the menu-driven interface:

1. **Account Management**
   - List accounts with details
   - Create new accounts
   - View account summaries
   - Update account settings

2. **Banking Operations**
   - Deposit money
   - Withdraw money
   - Transfer between accounts
   - View current balances

3. **Transaction History**
   - View all transactions
   - Filter by account, date, or type
   - Export transaction data
   - Generate summaries

4. **Settings & Profile**
   - Update account nicknames
   - View profile information
   - Session management
   - Help and documentation

## 🧪 Testing

### Run All Tests
```bash
# Run unit tests
python -m unittest discover tests/unit -v

# Test reorganized structure
python test_reorganized_structure.py

# Run specific test file
python -m unittest tests.unit.test_interactive_session -v
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality
- **Structure Tests**: File organization verification
- **Manual Testing**: User interaction flows

## 🔒 Security Features

- **Password Hashing**: bcrypt-based secure password storage
- **Session Management**: Automatic timeout and cleanup
- **Data Encryption**: Sensitive data protection
- **Audit Logging**: Operation tracking and monitoring
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error messages

## 📊 Architecture

### Core Components

- **User Class**: Manages user accounts and authentication
- **Account Class**: Handles individual account operations
- **Transaction Classes**: Models different transaction types
- **Managers**: Business logic for complex operations
- **Interactive Session**: Menu-driven user interface
- **Security Utils**: Authentication and encryption
- **Data Storage**: JSON-based persistence with backups

### Design Patterns

- **Repository Pattern**: Data access abstraction
- **Command Pattern**: CLI command handling
- **Observer Pattern**: Event notifications
- **Factory Pattern**: Account and transaction creation
- **Singleton Pattern**: Session and security managers

## 🚧 Development

### Adding New Features

1. **Core Logic**: Add to `src/core/` modules
2. **UI Features**: Extend `src/ui/` components
3. **Utilities**: Add to `src/utils/` modules
4. **Tests**: Create tests in `tests/unit/` or `tests/integration/`

### Code Quality

- **Modular Design**: Clear separation of concerns
- **Error Handling**: Comprehensive exception management
- **Documentation**: Inline comments and docstrings
- **Type Safety**: Consistent data types and validation
- **Performance**: Efficient algorithms and data structures

## 📈 Future Enhancements

- [ ] Web-based interface
- [ ] Database integration (PostgreSQL/MySQL)
- [ ] REST API endpoints
- [ ] Mobile application support
- [ ] Advanced reporting and analytics
- [ ] Multi-currency support
- [ ] Integration with external banking APIs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues, please:
1. Check the documentation
2. Run the test suite
3. Review the project structure
4. Create an issue with detailed information

---

**Banking System** - Secure, reliable, and user-friendly banking operations.