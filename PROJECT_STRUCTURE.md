# Banking System - Project Structure (Updated)

## ✅ Reorganization Complete

The banking system codebase has been successfully reorganized into a clean, modular structure.

## 📁 Current Directory Organization

```
ErpBankingSystem/
├── main.py                          # Main application entry point
├── test_reorganized_structure.py    # Structure verification test
├── README.md                        # Project documentation
├── PROJECT_STRUCTURE.md             # This file
├── PROJECT_ANALYSIS.md              # Project analysis
├── SECURITY_IMPROVEMENTS.md         # Security documentation
├── USAGE_GUIDE.md                   # Usage instructions
├── requirements.txt                 # Python dependencies
├── users_data.json                  # User data storage
├── active_sessions.json             # Active session tracking
├── .session                         # Current session token
├── .env                            # Environment variables
├── .gitignore                      # Git ignore rules
│
├── src/                            # 📦 Source Code
│   ├── __init__.py
│   ├── core/                       # 🏗️ Core Business Logic
│   │   ├── __init__.py
│   │   ├── user.py                 # User management and operations
│   │   ├── account.py              # Account operations and models
│   │   └── transaction.py          # Transaction data models
│   │
│   ├── managers/                   # 🎯 Business Operation Managers
│   │   ├── __init__.py
│   │   ├── transfer_manager.py     # Transfer operations and validation
│   │   └── transaction_manager.py  # Transaction history management
│   │
│   ├── ui/                         # 🖥️ User Interface Components
│   │   ├── __init__.py
│   │   └── interactive_session.py  # Interactive menu system
│   │
│   └── utils/                      # 🔧 Utility Functions
│       ├── __init__.py
│       ├── data_storage.py         # Data persistence and backups
│       ├── email_service.py        # Email notifications
│       ├── security_utils.py       # Security and encryption
│       ├── password_reset.py       # Password reset functionality
│       ├── security.py             # Additional security features
│       └── migrate_passwords.py    # Password migration utility
│
├── tests/                          # 🧪 Test Suite
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_interactive_session.py
│   │   ├── test_interactive_menu_integration.py
│   │   ├── test_transaction_manager.py
│   │   ├── test_transfer_*.py
│   │   └── test_enhanced_*.py
│   │
│   └── integration/                # Integration tests
│       └── __init__.py
│
├── examples/                       # 📚 Demo and Example Files
│   └── demo_transfer_system.py     # Transfer system demonstration
│
├── backups/                        # 💾 Data Backups
│   └── (automatic backup files)
│
└── .kiro/                          # 📋 Project Specifications
    └── specs/
        └── user-experience-enhancements/
            ├── requirements.md
            ├── design.md
            └── tasks.md
│       ├── __init__.py
│       ├── data_storage.py    # Data persistence
│       ├── security_utils.py  # Security and encryption
│       ├── email_service.py   # Email notifications
│       └── password_reset.py  # Password reset functionality
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── unit/                  # Unit tests
│   │   ├── __init__.py
│   │   ├── test_interactive_session.py
│   │   ├── test_interactive_menu_integration.py
│   │   ├── test_transaction_manager.py
│   │   ├── test_transfer_*.py
│   │   └── ...
│   │
│   └── integration/           # Integration tests
│       ├── __init__.py
│       └── test_integration.py
│
├── backups/                   # Data backups
├── .kiro/                     # Kiro IDE configuration
│   └── specs/                 # Feature specifications
└── docs/                      # Documentation
    ├── PROJECT_ANALYSIS.md
    ├── SECURITY_IMPROVEMENTS.md
    └── USAGE_GUIDE.md
```

## Module Dependencies

### Core Modules
- `user.py`: Depends on account.py, security_utils.py, managers
- `account.py`: Depends on transaction.py
- `transaction.py`: No dependencies (data model)

### Managers
- `transfer_manager.py`: Depends on core.transaction
- `transaction_manager.py`: No external dependencies

### UI Components
- `interactive_session.py`: Depends on utils (security, data_storage)

### Utilities
- `data_storage.py`: Depends on all core modules
- `security_utils.py`: No dependencies (utility functions)
- `email_service.py`: No dependencies
- `password_reset.py`: Depends on email_service

## Key Features by Module

### Core (`src/core/`)
- **User Management**: Registration, authentication, profile management
- **Account Operations**: Account creation, balance management, transactions
- **Transaction Model**: Data structure for all financial transactions

### Managers (`src/managers/`)
- **Transfer Management**: Account-to-account transfers with validation
- **Transaction History**: Filtering, pagination, export functionality

### UI (`src/ui/`)
- **Interactive Session**: Menu-driven interface with timeout management
- **Banking Operations**: Deposits, withdrawals, transfers through menus
- **Account Management**: Account creation and settings through UI

### Utilities (`src/utils/`)
- **Data Persistence**: JSON-based storage with backup management
- **Security**: Password hashing, session management, data validation
- **Email Service**: Password reset and notification emails
- **Password Reset**: Secure token-based password recovery

## Testing Structure

### Unit Tests (`tests/unit/`)
- Individual component testing
- Mock-based isolation testing
- Edge case validation

### Integration Tests (`tests/integration/`)
- End-to-end workflow testing
- Cross-module interaction testing
- System behavior validation

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a clear responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Testability**: Clear module boundaries enable focused testing
4. **Scalability**: New features can be added without affecting existing code
5. **Reusability**: Utility modules can be reused across different components
6. **Documentation**: Clear structure makes the codebase self-documenting