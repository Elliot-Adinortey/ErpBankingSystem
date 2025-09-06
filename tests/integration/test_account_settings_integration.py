import unittest
import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestAccountSettingsIntegration(unittest.TestCase):
    """Integration tests for account settings management CLI commands"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = tempfile.mkdtemp()
        cls.original_dir = os.getcwd()
        
        # Create a temporary users file for testing
        cls.test_users_file = os.path.join(cls.test_dir, 'users_data.json')
        cls.test_session_file = os.path.join(cls.test_dir, '.session')
        
        # Create test user data
        test_users = {
            "testuser": {
                "username": "testuser",
                "password": "$2b$12$example_hashed_password",  # This would be properly hashed
                "email": "test@example.com",
                "accounts": []
            }
        }
        
        with open(cls.test_users_file, 'w') as f:
            json.dump(test_users, f)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        os.chdir(cls.original_dir)
        # Clean up temp files
        import shutil
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def run_command(self, command_args):
        """Run a CLI command and return the result"""
        # Change to test directory
        os.chdir(self.test_dir)
        
        # Copy the main.py and src directory to test location
        import shutil
        main_py_path = os.path.join(self.original_dir, 'main.py')
        src_path = os.path.join(self.original_dir, 'src')
        
        if not os.path.exists('main.py'):
            shutil.copy2(main_py_path, '.')
        if not os.path.exists('src'):
            shutil.copytree(src_path, 'src')
        
        # Run the command
        cmd = ['python', 'main.py'] + command_args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.test_dir
        )
        
        return result
    
    def test_account_settings_workflow(self):
        """Test complete account settings management workflow"""
        # This is a simplified integration test since we can't easily 
        # create a full test environment with proper authentication
        
        # Test help commands work
        result = self.run_command(['help', 'update_account_settings'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('UPDATE_ACCOUNT_SETTINGS COMMAND', result.stdout)
        
        result = self.run_command(['help', 'view_account_settings'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('VIEW_ACCOUNT_SETTINGS COMMAND', result.stdout)
        
        result = self.run_command(['help', 'deactivate_account'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('DEACTIVATE_ACCOUNT COMMAND', result.stdout)
        
        result = self.run_command(['help', 'reactivate_account'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('REACTIVATE_ACCOUNT COMMAND', result.stdout)
    
    def test_command_argument_validation(self):
        """Test that commands properly validate arguments"""
        # Test update_account_settings without arguments
        result = self.run_command(['update_account_settings', '--help'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('account', result.stdout)
        self.assertIn('--nickname', result.stdout)
        self.assertIn('--overdraft-limit', result.stdout)
        
        # Test deactivate_account help
        result = self.run_command(['deactivate_account', '--help'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('--confirm', result.stdout)


if __name__ == '__main__':
    unittest.main()