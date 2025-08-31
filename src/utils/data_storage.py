import json
import os
from datetime import datetime
from src.core.user import User
from src.core.account import Account
from src.core.transaction import Transaction
from src.utils.security_utils import DataBackup, validate_data_integrity

DATA_FILE = "users_data.json"

def save_users_to_file(users):
    """Save users dictionary to JSON file with backup and validation"""
    try:
        # Create backup before saving
        if os.path.exists(DATA_FILE):
            backup_path = DataBackup.create_backup(DATA_FILE)
            if backup_path:
                print(f"Backup created: {os.path.basename(backup_path)}")
        
        users_data = {}
        for username, user in users.items():
            users_data[username] = {
                "username": user.username,
                "password": user.password,  # Now stores hashed password
                "email": user.email,
                "accounts": []
            }
            
            # Serialize accounts
            for account in user.accounts:
                account_data = {
                    "account_type": account.account_type,
                    "balance": account.balance,
                    "overdraft_limit": account.overdraft_limit,
                    "transactions": []
                }
                
                # Serialize transactions
                for transaction in account.transactions:
                    transaction_data = {
                        "amount": transaction.amount,
                        "transaction_type": transaction.transaction_type,
                        "date": transaction.date.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    account_data["transactions"].append(transaction_data)
                
                users_data[username]["accounts"].append(account_data)
        
        # Write to temporary file first
        temp_file = DATA_FILE + ".tmp"
        with open(temp_file, 'w') as f:
            json.dump(users_data, f, indent=2)
        
        # Validate the temporary file
        if validate_data_integrity(temp_file):
            # Replace the original file
            os.replace(temp_file, DATA_FILE)
            print(f"Data saved successfully to {DATA_FILE}")
        else:
            os.remove(temp_file)
            raise Exception("Data validation failed after save")
        
    except Exception as e:
        print(f"Error saving data: {e}")
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)

def load_users_from_file():
    """Load users dictionary from JSON file with validation"""
    users = {}
    
    if not os.path.exists(DATA_FILE):
        print(f"No existing data file found. Starting with empty user database.")
        return users
    
    # Validate data integrity before loading
    if not validate_data_integrity(DATA_FILE):
        print("Warning: Data file appears to be corrupted!")
        
        # Try to find a recent backup
        backup_dir = "backups"
        if os.path.exists(backup_dir):
            backup_files = [f for f in os.listdir(backup_dir) if f.startswith("users_data_backup_")]
            if backup_files:
                # Get the most recent backup
                backup_files.sort(reverse=True)
                latest_backup = os.path.join(backup_dir, backup_files[0])
                
                if validate_data_integrity(latest_backup):
                    print(f"Restoring from backup: {backup_files[0]}")
                    # Copy backup to main file
                    with open(latest_backup, 'r') as src:
                        with open(DATA_FILE, 'w') as dst:
                            dst.write(src.read())
                else:
                    print("No valid backup found. Starting with empty database.")
                    return users
            else:
                print("No backups available. Starting with empty database.")
                return users
        else:
            print("No backup directory found. Starting with empty database.")
            return users
    
    try:
        with open(DATA_FILE, 'r') as f:
            users_data = json.load(f)
        
        for username, user_data in users_data.items():
            # Create user object with hashed password
            user = User(user_data["username"], user_data["password"], user_data["email"], is_hashed=True)
            
            # Recreate accounts
            for account_data in user_data["accounts"]:
                account = Account(
                    account_data["account_type"],
                    account_data["balance"],
                    account_data["overdraft_limit"]
                )
                
                # Recreate transactions
                for transaction_data in account_data["transactions"]:
                    transaction_date = datetime.strptime(
                        transaction_data["date"], 
                        "%Y-%m-%d %H:%M:%S"
                    )
                    transaction = Transaction(
                        transaction_data["amount"],
                        transaction_data["transaction_type"],
                        transaction_date
                    )
                    account.transactions.append(transaction)
                
                user.accounts.append(account)
            
            users[username] = user
        
        print(f"Loaded {len(users)} users from {DATA_FILE}")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Starting with empty user database.")
    
    return users