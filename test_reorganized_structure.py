#!/usr/bin/env python3
"""
Test script to verify the reorganized file structure is working correctly
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🧪 Testing Reorganized File Structure")
    print("=" * 50)
    
    try:
        # Test core modules
        print("1. Testing core modules...")
        from core.user import User, register_user, login_user
        from core.account import Account
        from core.transaction import Transaction
        print("   ✓ Core modules imported successfully")
        
        # Test managers
        print("2. Testing manager modules...")
        from managers.transaction_manager import TransactionManager
        from managers.transfer_manager import TransferManager
        print("   ✓ Manager modules imported successfully")
        
        # Test UI modules
        print("3. Testing UI modules...")
        from ui.interactive_session import InteractiveSession, start_interactive_session
        print("   ✓ UI modules imported successfully")
        
        # Test utils modules
        print("4. Testing utility modules...")
        from utils.data_storage import save_users_to_file, load_users_from_file
        from utils.email_service import send_email
        from utils.security_utils import PasswordSecurity, SessionManager
        from utils.password_reset import initiate_password_reset, reset_password
        print("   ✓ Utility modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_functionality():
    """Test basic functionality with reorganized modules"""
    print("\n5. Testing basic functionality...")
    
    try:
        from core.user import User
        from core.account import Account
        
        # Create test user
        user = User("testuser", "password123", "test@example.com")
        
        # Create test accounts
        savings = Account("savings", 1000.0, 0, "My Savings")
        current = Account("current", 500.0, 200.0, "Daily Spending")
        
        user.add_account(savings)
        user.add_account(current)
        
        # Test operations
        savings.deposit(100.0)
        savings.withdraw(50.0)
        
        # Test transfer
        success, message, transfer_id = user.transfer_between_accounts("savings", "current", 100.0)
        
        if success:
            print("   ✓ Basic functionality working correctly")
            return True
        else:
            print(f"   ❌ Transfer failed: {message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

def test_main_application():
    """Test that the main application can start"""
    print("\n6. Testing main application startup...")
    
    try:
        # Test that main.py can be imported and run
        import subprocess
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Banking System" in result.stdout:
            print("   ✓ Main application starts correctly")
            return True
        else:
            print(f"   ❌ Main application failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Main application test failed: {e}")
        return False

def main():
    """Run all tests"""
    tests = [
        test_imports,
        test_functionality,
        test_main_application
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! File reorganization successful!")
        print("\n📁 New Structure:")
        print("   src/core/     - Business logic")
        print("   src/managers/ - Operation managers") 
        print("   src/ui/       - User interfaces")
        print("   src/utils/    - Utilities")
        print("   tests/        - Test suite")
        print("   examples/     - Demo files")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)