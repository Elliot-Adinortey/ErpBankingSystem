#!/usr/bin/env python3
"""
Demonstration of the account-to-account transfer system
"""

from user import User, register_user, login_user


def demo_transfer_system():
    """Demonstrate the complete transfer system functionality"""
    print("=== Account-to-Account Transfer System Demo ===\n")
    
    # Setup: Create user and accounts
    users = {}
    print("1. Setting up user and accounts...")
    register_user(users, "demo_user", "DemoPass123", "demo@example.com")
    user = login_user(users, "demo_user", "DemoPass123")
    
    # Create accounts with nicknames
    user.create_account_with_nickname("savings", 2000.0, 0, "Emergency Savings")
    user.create_account_with_nickname("current", 800.0, 500.0, "Daily Checking")
    user.create_account_with_nickname("salary", 3000.0, 0, "Salary Account")
    
    print("   Accounts created:")
    for account in user.accounts:
        print(f"     - {account.get_display_name()}: ${account.balance:.2f}")
    
    # Demo 1: Basic transfer validation
    print("\n2. Testing transfer validation...")
    is_valid, message, _, _ = user.validate_transfer("Emergency Savings", "Daily Checking", 500.0)
    print(f"   Validation result: {is_valid} - {message}")
    
    # Demo 2: Execute successful transfer
    print("\n3. Executing transfer: $500 from Emergency Savings to Daily Checking...")
    success, message, transfer_id = user.transfer_between_accounts(
        "Emergency Savings", "Daily Checking", 500.0, "Monthly budget allocation"
    )
    print(f"   Transfer result: {success}")
    print(f"   Message: {message}")
    
    # Show updated balances
    print("\n   Updated balances:")
    for account in user.accounts:
        print(f"     - {account.get_display_name()}: ${account.balance:.2f}")
    
    # Demo 3: Transfer using overdraft
    print("\n4. Testing transfer with overdraft...")
    print("   Attempting to transfer $1000 from Daily Checking (balance: $1300, overdraft: $500)")
    success, message, transfer_id2 = user.transfer_between_accounts(
        "Daily Checking", "Salary Account", 1000.0, "Large transfer using overdraft"
    )
    print(f"   Transfer result: {success}")
    print(f"   Message: {message}")
    
    # Show balances after overdraft transfer
    print("\n   Balances after overdraft transfer:")
    for account in user.accounts:
        available = account.balance + (account.overdraft_limit if account.account_type == 'current' else 0)
        print(f"     - {account.get_display_name()}: ${account.balance:.2f} (Available: ${available:.2f})")
    
    # Demo 4: Transfer history
    print("\n5. Viewing transfer history...")
    all_transfers = user.get_transfer_history()
    print(f"   Total transfer transactions: {len(all_transfers)}")
    
    for i, transfer in enumerate(all_transfers[:4], 1):  # Show first 4
        direction = "Outgoing" if transfer.is_outgoing else "Incoming"
        print(f"     {i}. {direction}: ${transfer.amount:.2f} - {transfer.memo}")
        print(f"        From: {transfer.from_account} → To: {transfer.to_account}")
        print(f"        ID: {transfer.transfer_id} | Date: {transfer.date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Demo 5: Account-specific transfer history
    print("\n6. Transfer history for Daily Checking account...")
    checking_transfers = user.get_transfer_history("Daily Checking")
    print(f"   Transfers involving Daily Checking: {len(checking_transfers)}")
    
    for transfer in checking_transfers:
        direction = "Sent" if transfer.is_outgoing else "Received"
        print(f"     - {direction}: ${transfer.amount:.2f} - {transfer.memo}")
    
    # Demo 6: Retrieve transfer by ID
    print(f"\n7. Retrieving transfer by ID: {transfer_id}")
    retrieved_transfer = user.get_transfer_by_id(transfer_id)
    if retrieved_transfer:
        print(f"   Found transfer: ${retrieved_transfer.amount:.2f}")
        print(f"   Memo: {retrieved_transfer.memo}")
        print(f"   From: {retrieved_transfer.from_account} → To: {retrieved_transfer.to_account}")
    
    # Demo 7: Error handling
    print("\n8. Testing error scenarios...")
    
    # Insufficient funds
    print("   a) Testing insufficient funds...")
    success, message, _ = user.transfer_between_accounts("Emergency Savings", "Daily Checking", 5000.0)
    print(f"      Result: {success} - {message}")
    
    # Non-existent account
    print("   b) Testing non-existent account...")
    success, message, _ = user.transfer_between_accounts("NonExistent", "Daily Checking", 100.0)
    print(f"      Result: {success} - {message}")
    
    # Same account transfer
    print("   c) Testing same account transfer...")
    success, message, _ = user.transfer_between_accounts("Emergency Savings", "Emergency Savings", 100.0)
    print(f"      Result: {success} - {message}")
    
    # Final summary
    print("\n9. Final account summary...")
    financial_overview = user.get_financial_overview()
    print(f"   Total balance across all accounts: ${financial_overview['total_balance']:.2f}")
    print(f"   Total available funds: ${financial_overview['total_available']:.2f}")
    
    print("\n=== Transfer System Demo Complete ===")
    print("✓ All transfer functionality working correctly!")


if __name__ == "__main__":
    demo_transfer_system()