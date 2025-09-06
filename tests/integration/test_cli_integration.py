"""
CLI Integration Tests

This module tests the command-line interface integration with all components,
ensuring CLI commands work correctly with the underlying system.
"""

import unittest
import sys
import os
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration with all system components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = tempfile.mkdtemp()
        cls.original_dir = os.getcwd()
        
        # Copy necessary files to test directory
        cls._setup_test_environment()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.chdir(cls.original_dir)
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    @classmethod
    def _setup_test_environment(cls):
        """Set up test environment with necessary files"""
        # Copy main.py and src directory
        main_py_source = os.path.join(cls.original_dir, 'main.py')
        src_source = os.path.join(cls.original_dir, 'src')
        
        main_py_dest = os.path.join(cls.test_dir, 'main.py')
        src_dest = os.path.join(cls.test_dir, 'src')
        
        if os.path.exists(main_py_source):
            shutil.copy2(main_py_source, main_py_dest)
        
        if os.path.exists(src_source):
            shutil.copytree(src_source, src_dest)
        
        # Create test users file
        cls.test_users_file = os.path.join(cls.test_dir, 'users_data.json')
        cls._create_test_users_file()
        
        # Change to test directory
        os.chdir(cls.test_dir)
    
    @classmethod
    def _create_test_users_file(cls):
        """Create test users file with pre-configured user"""
        import bcrypt
        
        # Create hashed password
        password = "TestPass123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        test_users = {
            "testuser": {
                "username": "testuser",
                "password": hashed.decode('utf-8'),
                "email": "test@example.com",
                "accounts": [
                    {
                        "account_type": "savings",
                        "balance": 1000.0,
                        "overdraft_limit": 0.0,
                        "nickname": "Test Savings",
                        "transactions": [],
                        "created_date": "2024-01-01T00:00:00",
                        "last_activity": "2024-01-01T00:00:00"
                    },
                    {
                        "account_type": "current",
                        "balance": 500.0,
                        "overdraft_limit": 200.0,
                        "nickname": "Test Current",
                        "transactions": [],
                        "created_date": "2024-01-01T00:00:00",
                        "last_activity": "2024-01-01T00:00:00"
                    }
                ]
            }
        }
        
        with open(cls.test_users_file, 'w') as f:
            json.dump(test_users, f, indent=2)
    
    def run_cli_command(self, args, input_data=None):
        """Run a CLI command and return the result"""
        cmd = [sys.executable, 'main.py'] + args
        
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            cwd=self.test_dir,
            timeout=30
        )
        
        return result
    
    def create_session_token(self):
        """Create a session token for authenticated commands"""
        # Login to create session
        result = self.run_cli_command([
            'login', 'testuser', 'TestPass123'
        ])
        
        if result.returncode == 0 and os.path.exists('.session'):
            with open('.session', 'r') as f:
                return f.read().strip()
        
        return None
    
    def test_user_registration_and_login_cli(self):
        """Test user registration and login through CLI"""
        # Test registration
        result = self.run_cli_command([
            'register', 'newuser', 'NewPass123', 'new@example.com'
        ])
        
        self.assertEqual(result.returncode, 0, f"Registration failed: {result.stderr}")
        self.assertIn("registered successfully", result.stdout.lower())
        
        # Test login
        result = self.run_cli_command([
            'login', 'newuser', 'NewPass123'
        ])
        
        self.assertEqual(result.returncode, 0, f"Login failed: {result.stderr}")
        self.assertIn("login successful", result.stdout.lower())
        
        # Verify session file was created
        self.assertTrue(os.path.exists('.session'))
    
    def test_account_management_cli(self):
        """Test account management commands through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token, "Failed to create session token")
        
        # Test account listing
        result = self.run_cli_command(['list_accounts', '--token', token])
        self.assertEqual(result.returncode, 0, f"List accounts failed: {result.stderr}")
        self.assertIn("Test Savings", result.stdout)
        self.assertIn("Test Current", result.stdout)
        
        # Test account summary
        result = self.run_cli_command(['account_summary', '--token', token])
        self.assertEqual(result.returncode, 0, f"Account summary failed: {result.stderr}")
        self.assertIn("Account Summary", result.stdout)
        self.assertIn("Total Balance", result.stdout)
        
        # Test financial overview
        result = self.run_cli_command(['financial_overview', '--token', token])
        self.assertEqual(result.returncode, 0, f"Financial overview failed: {result.stderr}")
        self.assertIn("Financial Overview", result.stdout)
        
        # Test adding new account
        result = self.run_cli_command([
            'add_account', 'salary', '--balance', '2000', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Add account failed: {result.stderr}")
        
        # Verify new account was added
        result = self.run_cli_command(['list_accounts', '--token', token])
        self.assertIn("Salary", result.stdout)
    
    def test_banking_operations_cli(self):
        """Test banking operations through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Test deposit
        result = self.run_cli_command([
            'deposit', 'savings', '200', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Deposit failed: {result.stderr}")
        
        # Test withdrawal
        result = self.run_cli_command([
            'withdraw', 'current', '100', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Withdrawal failed: {result.stderr}")
        
        # Test balance check
        result = self.run_cli_command([
            'view_balance', 'savings', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"View balance failed: {result.stderr}")
        self.assertIn("Balance:", result.stdout)
        
        # Verify balance reflects deposit
        self.assertIn("1200", result.stdout)  # 1000 + 200
    
    def test_transfer_operations_cli(self):
        """Test transfer operations through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Test transfer between accounts
        result = self.run_cli_command([
            'transfer', 'savings', 'current', '300',
            '--memo', 'CLI test transfer',
            '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Transfer failed: {result.stderr}")
        self.assertIn("Transfer", result.stdout)
        self.assertIn("completed successfully", result.stdout)
        
        # Verify balances after transfer
        result = self.run_cli_command(['view_balance', 'savings', '--token', token])
        self.assertIn("700", result.stdout)  # 1000 - 300
        
        result = self.run_cli_command(['view_balance', 'current', '--token', token])
        self.assertIn("800", result.stdout)  # 500 + 300
    
    def test_transaction_history_cli(self):
        """Test transaction history commands through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Perform some transactions first
        self.run_cli_command(['deposit', 'savings', '150', '--token', token])
        self.run_cli_command(['withdraw', 'current', '75', '--token', token])
        
        # Test transaction history
        result = self.run_cli_command([
            'transaction_history', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Transaction history failed: {result.stderr}")
        self.assertIn("Transaction History", result.stdout)
        
        # Test filtered transaction history
        result = self.run_cli_command([
            'transaction_history', '--account', 'savings', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Filtered history failed: {result.stderr}")
        self.assertIn("Test Savings", result.stdout)
        
        # Test transaction summary
        result = self.run_cli_command([
            'transaction_summary', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Transaction summary failed: {result.stderr}")
        self.assertIn("Transaction Summary", result.stdout)
        self.assertIn("Total Transactions", result.stdout)
    
    def test_interactive_mode_cli(self):
        """Test interactive mode through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Test interactive mode startup (will exit immediately due to EOF)
        result = self.run_cli_command([
            'interactive', '--token', token
        ], input_data='\n')  # Send newline to exit
        
        # Interactive mode should start successfully even if it exits immediately
        self.assertEqual(result.returncode, 0, f"Interactive mode failed: {result.stderr}")
        self.assertIn("interactive", result.stdout.lower())
    
    def test_help_system_cli(self):
        """Test help system through CLI"""
        # Test general help
        result = self.run_cli_command(['help'])
        self.assertEqual(result.returncode, 0, f"Help failed: {result.stderr}")
        self.assertIn("Banking System", result.stdout)
        self.assertIn("Available commands", result.stdout)
        
        # Test specific command help
        result = self.run_cli_command(['help', 'transfer'])
        self.assertEqual(result.returncode, 0, f"Transfer help failed: {result.stderr}")
        self.assertIn("TRANSFER COMMAND", result.stdout)
        self.assertIn("Examples:", result.stdout)
        
        # Test help for account management
        result = self.run_cli_command(['help', 'account_summary'])
        self.assertEqual(result.returncode, 0, f"Account summary help failed: {result.stderr}")
        self.assertIn("ACCOUNT_SUMMARY COMMAND", result.stdout)
    
    def test_data_export_cli(self):
        """Test data export functionality through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Perform some transactions to have data to export
        self.run_cli_command(['deposit', 'savings', '100', '--token', token])
        self.run_cli_command(['withdraw', 'current', '50', '--token', token])
        
        # Test transaction export
        result = self.run_cli_command([
            'export_data', 'transactions', 'csv', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Transaction export failed: {result.stderr}")
        self.assertIn("exported successfully", result.stdout.lower())
        
        # Test account export
        result = self.run_cli_command([
            'export_data', 'accounts', 'json', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Account export failed: {result.stderr}")
        self.assertIn("exported successfully", result.stdout.lower())
        
        # Test full backup
        result = self.run_cli_command([
            'export_data', 'full_backup', 'json', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Full backup failed: {result.stderr}")
        self.assertIn("exported successfully", result.stdout.lower())
    
    def test_statement_generation_cli(self):
        """Test statement generation through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Perform some transactions
        self.run_cli_command(['deposit', 'savings', '200', '--token', token])
        self.run_cli_command(['withdraw', 'savings', '50', '--token', token])
        
        # Test statement generation
        result = self.run_cli_command([
            'generate_statement', 'savings', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Statement generation failed: {result.stderr}")
        self.assertIn("ACCOUNT STATEMENT", result.stdout)
        self.assertIn("Test Savings", result.stdout)
        
        # Test statement export
        result = self.run_cli_command([
            'generate_statement', 'savings', '--export', '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Statement export failed: {result.stderr}")
        self.assertIn("exported to", result.stdout.lower())
    
    def test_batch_operations_cli(self):
        """Test batch operations through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Create batch file
        batch_operations = [
            {"operation": "deposit", "account": "savings", "amount": 100.0},
            {"operation": "withdraw", "account": "current", "amount": 50.0},
            {"operation": "transfer", "from_account": "savings", "to_account": "current", "amount": 75.0}
        ]
        
        batch_file = 'test_batch.json'
        with open(batch_file, 'w') as f:
            json.dump(batch_operations, f)
        
        # Test batch execution
        result = self.run_cli_command([
            'batch_operations', batch_file, '--token', token
        ])
        self.assertEqual(result.returncode, 0, f"Batch operations failed: {result.stderr}")
        self.assertIn("Batch operations completed", result.stdout)
        
        # Verify batch operations were executed
        result = self.run_cli_command(['account_summary', '--token', token])
        self.assertIn("Total Balance", result.stdout)
    
    def test_session_management_cli(self):
        """Test session management through CLI"""
        # Test login creates session
        result = self.run_cli_command([
            'login', 'testuser', 'TestPass123'
        ])
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists('.session'))
        
        # Test status command
        result = self.run_cli_command(['status'])
        self.assertEqual(result.returncode, 0, f"Status failed: {result.stderr}")
        self.assertIn("Logged in as testuser", result.stdout)
        
        # Test logout
        result = self.run_cli_command(['logout'])
        self.assertEqual(result.returncode, 0, f"Logout failed: {result.stderr}")
        self.assertIn("Logged out successfully", result.stdout)
        
        # Verify session file is removed
        self.assertFalse(os.path.exists('.session'))
        
        # Test status after logout
        result = self.run_cli_command(['status'])
        self.assertIn("Not logged in", result.stdout)
    
    def test_error_handling_cli(self):
        """Test error handling through CLI"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Test insufficient funds error
        result = self.run_cli_command([
            'withdraw', 'savings', '5000', '--token', token
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("insufficient", result.stderr.lower())
        
        # Test invalid account error
        result = self.run_cli_command([
            'deposit', 'nonexistent', '100', '--token', token
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())
        
        # Test invalid transfer
        result = self.run_cli_command([
            'transfer', 'savings', 'nonexistent', '100', '--token', token
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())
        
        # Test operations without authentication
        result = self.run_cli_command(['deposit', 'savings', '100'])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authentication", result.stderr.lower())
    
    def test_command_argument_validation_cli(self):
        """Test command argument validation through CLI"""
        # Test missing arguments
        result = self.run_cli_command(['deposit'])
        self.assertNotEqual(result.returncode, 0)
        
        result = self.run_cli_command(['transfer', 'savings'])
        self.assertNotEqual(result.returncode, 0)
        
        # Test invalid argument types
        result = self.run_cli_command(['deposit', 'savings', 'invalid_amount'])
        self.assertNotEqual(result.returncode, 0)
        
        # Test help for commands with missing args
        result = self.run_cli_command(['deposit', '--help'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout.lower())
    
    def test_cli_integration_with_all_components(self):
        """Test CLI integration with all system components"""
        token = self.create_session_token()
        self.assertIsNotNone(token)
        
        # Test complete workflow through CLI
        
        # 1. Create new account
        result = self.run_cli_command([
            'add_account', 'salary', '--balance', '3000', '--token', token
        ])
        self.assertEqual(result.returncode, 0)
        
        # 2. Perform banking operations
        self.run_cli_command(['deposit', 'salary', '500', '--token', token])
        self.run_cli_command(['withdraw', 'current', '100', '--token', token])
        
        # 3. Transfer between accounts
        result = self.run_cli_command([
            'transfer', 'salary', 'savings', '400',
            '--memo', 'Integration test',
            '--token', token
        ])
        self.assertEqual(result.returncode, 0)
        
        # 4. Check transaction history
        result = self.run_cli_command([
            'transaction_history', '--token', token
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Integration test", result.stdout)
        
        # 5. Generate summary
        result = self.run_cli_command([
            'account_summary', '--token', token
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total Accounts: 3", result.stdout)
        
        # 6. Export data
        result = self.run_cli_command([
            'export_data', 'transactions', 'csv', '--token', token
        ])
        self.assertEqual(result.returncode, 0)
        
        # 7. Generate statement
        result = self.run_cli_command([
            'generate_statement', 'savings', '--token', token
        ])
        self.assertEqual(result.returncode, 0)
        
        # 8. Logout
        result = self.run_cli_command(['logout'])
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()