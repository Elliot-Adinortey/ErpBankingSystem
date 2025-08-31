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

# Create accounts
python main.py add_account savings 1000
python main.py add_account current 500 --overdraft_limit 200

# View all accounts
python main.py list_accounts

# Banking operations
python main.py deposit savings 250
python main.py withdraw current 100
python main.py view_balance savings

# Logout when done
python main.py logout
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
| `list_accounts` | Show all accounts | `python main.py list_accounts` |
| `view_balance` | Check account balance | `python main.py view_balance savings` |

### Banking Operations
| Command | Description | Example |
|---------|-------------|---------|
| `deposit` | Add money to account | `python main.py deposit savings 500` |
| `withdraw` | Remove money from account | `python main.py withdraw current 200` |

### Password Management
| Command | Description | Example |
|---------|-------------|---------|
| `reset_password_init` | Start password reset | `python main.py reset_password_init john` |
| `reset_password_complete` | Complete password reset | `python main.py reset_password_complete TOKEN newpass` |

## Account Types

### Savings Account
- Standard savings account
- No overdraft facility
- Example: `python main.py add_account savings 1000`

### Current Account
- Checking account with overdraft option
- Specify overdraft limit when creating
- Example: `python main.py add_account current 500 --overdraft_limit 200`

### Salary Account
- Salary deposit account
- No overdraft facility
- Example: `python main.py add_account salary 2000`

## Session Management

### How Sessions Work
1. **Login** creates a session token (valid for 2 hours)
2. **Token** is automatically saved to `.session` file
3. **Operations** use the saved token automatically
4. **Logout** invalidates the token and removes the file

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

## Error Messages

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "No session token found" | Not logged in | Run `python main.py login username password` |
| "Invalid or expired session" | Session timeout | Login again |
| "User not found" | Wrong username | Check spelling or register new user |
| "Incorrect password" | Wrong password | Check password or use password reset |
| "Account not found" | Account doesn't exist | Use `list_accounts` to see available accounts |
| "Insufficient funds" | Not enough money | Check balance with `view_balance` |

## Tips and Best Practices

### Daily Usage
1. **Login once** at the start of your session
2. **Use `list_accounts`** to see your accounts overview
3. **Check `status`** if you're unsure about login state
4. **Logout** when finished for security

### Security Tips
1. **Use strong passwords** meeting all requirements
2. **Don't share session tokens** with others
3. **Logout** when using shared computers
4. **Keep backups** of important data (automatic backups are created)

### Troubleshooting
1. **Check status first** when commands fail
2. **Re-login** if session issues occur
3. **Check account names** with `list_accounts`
4. **Use exact account type names**: `savings`, `current`, `salary`

## File Structure

```
banking-system/
├── main.py                 # Main application
├── user.py                 # User management
├── account.py              # Account operations
├── security_utils.py       # Security features
├── data_storage.py         # Data persistence
├── users_data.json         # User data (auto-generated)
├── .session               # Current session (auto-generated)
├── active_sessions.json   # Session storage (auto-generated)
├── backups/               # Automatic backups (auto-generated)
├── requirements.txt       # Python dependencies
├── .env                   # Email configuration
└── .gitignore            # Git ignore rules
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

### Batch Operations
```bash
# Multiple operations in sequence
python main.py login john pass123
python main.py add_account savings 1000
python main.py add_account current 500 --overdraft_limit 200
python main.py deposit savings 500
python main.py list_accounts
python main.py logout
```

---

**Need Help?**
- Use `python main.py -h` for command help
- Use `python main.py COMMAND -h` for specific command help
- Check error messages for specific guidance
- Ensure you're logged in before performing operations