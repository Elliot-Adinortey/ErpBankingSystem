#!/usr/bin/env python3
"""
Migration script to hash existing plain text passwords
Run this once to upgrade existing user data to use hashed passwords
"""

import json
import os
from .security_utils import PasswordSecurity, DataBackup

DATA_FILE = "users_data.json"

def migrate_passwords():
    """Migrate plain text passwords to hashed passwords"""
    
    if not os.path.exists(DATA_FILE):
        print("No data file found. Nothing to migrate.")
        return
    
    # Create backup before migration
    backup_path = DataBackup.create_backup(DATA_FILE)
    if backup_path:
        print(f"Backup created: {os.path.basename(backup_path)}")
    
    try:
        with open(DATA_FILE, 'r') as f:
            users_data = json.load(f)
        
        migrated_count = 0
        
        for username, user_data in users_data.items():
            password = user_data.get('password', '')
            
            # Check if password is already hashed (bcrypt hashes start with $2b$)
            if not password.startswith('$2b$'):
                print(f"Migrating password for user: {username}")
                hashed_password = PasswordSecurity.hash_password(password)
                user_data['password'] = hashed_password
                migrated_count += 1
            else:
                print(f"Password already hashed for user: {username}")
        
        if migrated_count > 0:
            # Save the updated data
            with open(DATA_FILE, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            print(f"\nMigration completed successfully!")
            print(f"Migrated {migrated_count} user passwords to secure hashes.")
        else:
            print("\nNo passwords needed migration. All passwords are already hashed.")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        print("Please check the backup file if data was corrupted.")

if __name__ == "__main__":
    print("Password Migration Script")
    print("=" * 30)
    
    response = input("This will hash all plain text passwords. Continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        migrate_passwords()
    else:
        print("Migration cancelled.")