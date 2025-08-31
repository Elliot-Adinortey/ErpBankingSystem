#!/usr/bin/env python3
"""
Integration test to verify enhanced account management works with existing system
"""

from user import User, register_user, login_user
from account import Account

def test_integration():
    """Test integration of enhanced features with existing system"""
    print("=== Enhanced Account Management Integration Test ===\n")
    
    # Test user registration and login (existing functionality)
    users = {}
    print("1. Testing user registration...")
    success = register_user(users, "testuser", "TestPass123", "test@example.com")
    assert success, "User registration failed"
    
    print("2. Testing user login...")
    user = login_user(users, "testuser", "TestPass123")
    assert user is not None, "User login failed"
    
    # Test enhanced account creation with nicknames
    print("3. Testing enhanced account creation with nicknames...")
    savings_account = user.create_account_with_nickname("savings", 1000, 0, "Emergency Fund")
    print(f"   Created: {savings_account.get_display_name()} with balance ${savings_account.balance}")
    
    current_account = user.create_account_with_nickname("current", 500, 1000, "Main Checking")
    print(f"   Created: {current_account.get_display_name()} with balance ${current_account.balance}")
    
    # Test account retrieval by nickname and type
    print("4. Testing account retrieval...")
    retrieved_by_nickname = user.get_account("Emergency Fund")
    retrieved_by_type = user.get_account("current")
    assert retrieved_by_nickname == savings_account, "Nickname retrieval failed"
    assert retrieved_by_type == current_account, "Type retrieval failed"
    print("   ✓ Account retrieval by nickname and type works")
    
    # Test nickname updates
    print("5. Testing nickname updates...")
    user.update_account_nickname("savings", "Updated Emergency Fund")
    assert savings_account.nickname == "Updated Emergency Fund", "Nickname update failed"
    print(f"   ✓ Updated nickname to: {savings_account.get_display_name()}")
    
    # Test enhanced summaries
    print("6. Testing enhanced summaries...")
    basic_summary = user.get_accounts_summary()
    enhanced_summary = user.get_enhanced_summary()
    financial_overview = user.get_financial_overview()
    
    print(f"   Basic summary: {basic_summary}")
    print(f"   Total accounts: {enhanced_summary['total_accounts']}")
    print(f"   Total balance: ${enhanced_summary['total_balance']}")
    print(f"   Total available: ${financial_overview['total_available']}")
    
    # Test transactions with activity tracking
    print("7. Testing transactions with activity tracking...")
    original_activity = savings_account.last_activity
    savings_account.deposit(200)
    assert savings_account.last_activity > original_activity, "Activity tracking failed"
    print(f"   ✓ Deposit successful, activity tracked")
    
    # Test AccountManager functionality
    print("8. Testing AccountManager functionality...")
    manager = user.account_manager
    account_list = manager.list_accounts_with_nicknames()
    print(f"   Accounts with nicknames: {len(account_list)}")
    for acc in account_list:
        print(f"     - {acc['display_name']}: ${acc['balance']}")
    
    # Test backward compatibility
    print("9. Testing backward compatibility...")
    old_style_account = Account("salary", 2000, 0)
    user.add_account(old_style_account)
    
    # Should work with old methods
    old_summary = user.get_accounts_summary()
    assert "Salary" in old_summary, "Backward compatibility failed"
    print("   ✓ Old-style account creation and retrieval works")
    
    print("\n=== All integration tests passed! ===")

if __name__ == "__main__":
    test_integration()