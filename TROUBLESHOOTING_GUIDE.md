# Banking System - Troubleshooting Guide

## Overview

This guide helps you resolve common issues with the enhanced banking system features, including interactive mode, transfers, transaction history, and data export/import operations.

## Quick Diagnosis

### Check System Status First
```bash
# Always start with these commands
python main.py status                    # Check login status
python main.py list_accounts            # Verify accounts exist
python main.py help                     # Get command overview
```

### Common Quick Fixes
1. **Session Issues**: `python main.py logout` then `python main.py login username password`
2. **Account Issues**: `python main.py list_accounts` to verify account names
3. **Command Issues**: `python main.py help [command]` for syntax help

## Interactive Mode Issues

### Problem: Interactive Mode Won't Start

**Symptoms:**
- Error when running `python main.py interactive`
- Menu doesn't appear
- Session authentication fails

**Solutions:**
1. **Check Login Status**
   ```bash
   python main.py status
   ```
   If not logged in:
   ```bash
   python main.py login username password
   python main.py interactive
   ```

2. **Clear Session and Restart**
   ```bash
   python main.py logout
   python main.py login username password
   python main.py interactive
   ```

3. **Check for Session File Issues**
   ```bash
   # Remove corrupted session file
   rm .session
   python main.py login username password
   python main.py interactive
   ```

### Problem: Menu Not Responding

**Symptoms:**
- Menu appears but selections don't work
- Numbers don't trigger menu actions
- Interface seems frozen

**Solutions:**
1. **Press Enter** to refresh the display
2. **Type valid numbers** (1-6 for main menu)
3. **Force exit and restart**:
   ```bash
   # Press Ctrl+C to exit
   python main.py interactive
   ```

### Problem: Session Timeout Issues

**Symptoms:**
- "Session expired" messages during operations
- Forced logout during interactive session
- Timeout warnings appearing frequently

**Solutions:**
1. **Complete operations quickly** when timeout warning appears
2. **Restart session**:
   ```bash
   python main.py login username password
   python main.py interactive
   ```
3. **Use command line** for single operations if timeouts persist

### Problem: Operations Fail in Interactive Mode

**Symptoms:**
- Menu selections work but operations fail
- Error messages in interactive menus
- Data not saving properly

**Solutions:**
1. **Check account names** in Account Management menu
2. **Verify balances** before transfers or withdrawals
3. **Exit and test with command line**:
   ```bash
   # Exit interactive mode
   # Test individual commands
   python main.py list_accounts
   python main.py account_summary
   ```

## Account Transfer Issues

### Problem: Transfer Validation Fails

**Symptoms:**
- "Account not found" errors
- "Insufficient funds" when balance seems adequate
- Transfer command syntax errors

**Solutions:**
1. **Verify Account Names**
   ```bash
   python main.py list_accounts
   # Use exact account type names: savings, current, salary
   ```

2. **Check Available Balance**
   ```bash
   python main.py account_summary
   # Check both balance and available balance (including overdraft)
   ```

3. **Use Correct Syntax**
   ```bash
   # Correct format
   python main.py transfer savings current 100
   python main.py transfer savings current 100 --memo "Monthly transfer"
   ```

### Problem: Transfer Appears to Succeed But Balances Don't Update

**Symptoms:**
- Transfer confirmation received
- Balances remain unchanged
- Transaction not in history

**Solutions:**
1. **Check Both Account Histories**
   ```bash
   python main.py transaction_history --account savings
   python main.py transaction_history --account current
   ```

2. **Verify Data Persistence**
   ```bash
   python main.py logout
   python main.py login username password
   python main.py account_summary
   ```

3. **Check for Data File Issues**
   ```bash
   # Check if users_data.json is writable
   ls -la users_data.json
   # Check recent backups
   ls -la backups/
   ```

### Problem: Transfer Between Wrong Accounts

**Symptoms:**
- Transferred to/from unintended accounts
- Need to reverse a transfer
- Account names confused

**Solutions:**
1. **Identify the Transfer**
   ```bash
   python main.py transaction_history --type transfer
   ```

2. **Reverse Transfer Manually**
   ```bash
   # Transfer back the same amount
   python main.py transfer [destination] [source] [amount] --memo "Reversal of transfer"
   ```

3. **Use Account Nicknames** to avoid confusion:
   ```bash
   python main.py update_account_settings savings --nickname "Emergency Fund"
   python main.py update_account_settings current --nickname "Daily Expenses"
   ```

## Transaction History Issues

### Problem: No Transactions Found

**Symptoms:**
- "No transactions found" message
- Empty transaction history
- Filters returning no results

**Solutions:**
1. **Check Without Filters**
   ```bash
   python main.py transaction_history
   ```

2. **Verify Account Has Transactions**
   ```bash
   python main.py account_summary
   # Check transaction count for each account
   ```

3. **Check Date Range Filters**
   ```bash
   # Use broader date range
   python main.py transaction_history --start_date 2024-01-01
   # Remove date filters entirely
   python main.py transaction_history --account savings
   ```

### Problem: Date Filter Not Working

**Symptoms:**
- Date filters ignored
- "Invalid date format" errors
- Unexpected date range results

**Solutions:**
1. **Use Correct Date Format**
   ```bash
   # Correct formats
   python main.py transaction_history --start_date 2024-01-15
   python main.py transaction_history --start_date "2024-01-15 14:30"
   
   # Incorrect formats (avoid these)
   python main.py transaction_history --start_date 01/15/2024  # May not work
   ```

2. **Check Date Logic**
   ```bash
   # Ensure start_date is before end_date
   python main.py transaction_history --start_date 2024-01-01 --end_date 2024-12-31
   ```

3. **Test Date Parsing**
   ```bash
   # Use help to see supported formats
   python main.py help transaction_history
   ```

### Problem: Large Transaction History Slow to Load

**Symptoms:**
- Long delays when viewing transaction history
- System appears to hang
- Memory usage increases significantly

**Solutions:**
1. **Use Pagination**
   ```bash
   python main.py transaction_history --page_size 20 --page 1
   ```

2. **Apply Filters**
   ```bash
   # Filter by account
   python main.py transaction_history --account savings
   
   # Filter by date range
   python main.py transaction_history --start_date 2024-06-01
   ```

3. **Export Large Datasets**
   ```bash
   # Export to file instead of viewing
   python main.py export_data transactions --format csv
   ```

## Data Export/Import Issues

### Problem: Export Fails

**Symptoms:**
- "Export failed" error messages
- Files not created
- Permission denied errors

**Solutions:**
1. **Check File Permissions**
   ```bash
   # Ensure current directory is writable
   ls -la .
   # Try exporting to a specific location
   python main.py export_data transactions --format csv --filename /tmp/export.csv
   ```

2. **Check Disk Space**
   ```bash
   df -h .
   # Ensure sufficient disk space for export
   ```

3. **Try Different Format**
   ```bash
   # If CSV fails, try JSON
   python main.py export_data transactions --format json
   ```

### Problem: Import Validation Fails

**Symptoms:**
- "Import validation failed" errors
- Data not imported
- Format errors

**Solutions:**
1. **Check File Format**
   ```bash
   # Ensure CSV has correct headers
   head -5 your_file.csv
   
   # Check JSON structure
   python -m json.tool your_file.json
   ```

2. **Use Export Template**
   ```bash
   # Export existing data to see correct format
   python main.py export_data transactions --format csv --filename template.csv
   # Use template.csv as format reference
   ```

3. **Validate Data Before Import**
   ```bash
   # Use preview mode if available
   python main.py import_data transactions your_file.csv --preview
   ```

### Problem: Exported Data Incomplete

**Symptoms:**
- Missing transactions in export
- Date ranges not applied correctly
- Account filters not working

**Solutions:**
1. **Verify Filter Parameters**
   ```bash
   # Check what data exists
   python main.py transaction_summary --account savings
   
   # Export with explicit parameters
   python main.py export_data transactions --format csv --account savings --start_date 2024-01-01
   ```

2. **Export All Data First**
   ```bash
   # Export everything, then filter externally
   python main.py export_data transactions --format csv
   ```

3. **Check Account Names**
   ```bash
   python main.py list_accounts
   # Ensure account names match exactly
   ```

## Batch Operations Issues

### Problem: Batch File Processing Fails

**Symptoms:**
- "Batch operation failed" errors
- Some operations succeed, others fail
- Invalid batch file format

**Solutions:**
1. **Validate Batch File Format**
   ```bash
   # Create template first
   python main.py batch_template --operations deposit,withdraw
   # Use template as reference for your batch file
   ```

2. **Check JSON Syntax**
   ```bash
   # Validate JSON format
   python -m json.tool your_batch_file.json
   ```

3. **Test Individual Operations**
   ```bash
   # Test operations manually first
   python main.py deposit savings 100
   python main.py withdraw current 50
   # Then add to batch file
   ```

### Problem: Batch Operations Partially Complete

**Symptoms:**
- Some operations in batch succeed
- Others fail with errors
- Inconsistent results

**Solutions:**
1. **Check Batch Status**
   ```bash
   python main.py batch_status
   # Review which operations failed and why
   ```

2. **Use Preview Mode**
   ```bash
   # Validate before executing
   python main.py batch_operations your_file.json --preview
   ```

3. **Process in Smaller Batches**
   ```bash
   # Split large batch files into smaller ones
   # Process incrementally to isolate issues
   ```

## Account Settings Issues

### Problem: Nickname Updates Not Saving

**Symptoms:**
- Nickname changes don't persist
- Old nicknames still appear
- Update commands succeed but changes lost

**Solutions:**
1. **Verify Update Command**
   ```bash
   python main.py update_account_settings savings --nickname "Emergency Fund"
   # Check immediately
   python main.py list_accounts
   ```

2. **Check Data Persistence**
   ```bash
   python main.py logout
   python main.py login username password
   python main.py list_accounts
   ```

3. **Check File Permissions**
   ```bash
   ls -la users_data.json
   # Ensure file is writable
   ```

### Problem: Overdraft Limit Changes Not Applied

**Symptoms:**
- Overdraft limit updates fail
- Limits revert to previous values
- Transfer validation uses old limits

**Solutions:**
1. **Use Correct Account Type**
   ```bash
   # Only current accounts support overdraft
   python main.py update_account_settings current --overdraft_limit 500
   ```

2. **Verify Account Type**
   ```bash
   python main.py account_summary
   # Check which accounts are current accounts
   ```

3. **Test Limit Application**
   ```bash
   # Try a withdrawal that would use overdraft
   python main.py withdraw current [amount_over_balance]
   ```

## System-Level Issues

### Problem: Data Corruption or Loss

**Symptoms:**
- Accounts missing
- Balances incorrect
- Transaction history lost

**Solutions:**
1. **Check Recent Backups**
   ```bash
   ls -la backups/
   # Find most recent backup
   ```

2. **Restore from Backup**
   ```bash
   # Copy backup to main file (CAUTION: This overwrites current data)
   cp backups/users_data_backup_[timestamp].json users_data.json
   ```

3. **Verify Data Integrity**
   ```bash
   python main.py status
   python main.py list_accounts
   python main.py account_summary
   ```

### Problem: Performance Issues

**Symptoms:**
- Slow command execution
- Long delays in interactive mode
- High memory usage

**Solutions:**
1. **Check Data File Size**
   ```bash
   ls -lh users_data.json
   # Large files may cause performance issues
   ```

2. **Clean Up Old Sessions**
   ```bash
   python main.py logout
   rm .session active_sessions.json
   python main.py login username password
   ```

3. **Use Pagination and Filters**
   ```bash
   # Limit data retrieval
   python main.py transaction_history --page_size 10
   python main.py transaction_history --start_date 2024-06-01
   ```

### Problem: Permission Errors

**Symptoms:**
- "Permission denied" errors
- Cannot write to files
- Cannot create backups

**Solutions:**
1. **Check File Permissions**
   ```bash
   ls -la users_data.json .session backups/
   chmod 644 users_data.json
   chmod 755 backups/
   ```

2. **Check Directory Permissions**
   ```bash
   ls -la .
   # Ensure current directory is writable
   ```

3. **Run with Appropriate Permissions**
   ```bash
   # Ensure you have write access to the banking system directory
   ```

## Getting Additional Help

### Built-in Help System
```bash
# General help
python main.py help

# Command-specific help
python main.py help [command]
python main.py [command] -h

# Interactive mode help
python main.py help interactive
```

### Diagnostic Commands
```bash
# System status
python main.py status

# Account verification
python main.py list_accounts
python main.py account_summary

# Session information
python main.py status

# Recent activity
python main.py transaction_history --page_size 5
```

### Log Files
```bash
# Check audit logs for errors
tail -50 logs/audit.log

# Look for recent errors
grep -i error logs/audit.log
```

### Recovery Procedures

**Complete System Reset (Last Resort)**
1. **Backup Current Data**
   ```bash
   cp users_data.json users_data_backup_manual.json
   ```

2. **Clear All Sessions**
   ```bash
   python main.py logout
   rm .session active_sessions.json
   ```

3. **Test Basic Functionality**
   ```bash
   python main.py login username password
   python main.py list_accounts
   ```

4. **Restore from Backup if Needed**
   ```bash
   cp backups/users_data_backup_[recent_timestamp].json users_data.json
   ```

---

## Prevention Tips

### Regular Maintenance
- **Regular Backups**: System creates automatic backups, but export data regularly
- **Session Hygiene**: Always logout when finished
- **Monitor Disk Space**: Ensure adequate space for data files and backups
- **Update Regularly**: Keep the system updated with latest features

### Best Practices
- **Use Interactive Mode**: For multiple operations, use interactive mode
- **Verify Operations**: Always check results after important operations
- **Use Descriptive Memos**: Add memos to transfers for better tracking
- **Set Account Nicknames**: Use meaningful nicknames for easier identification

### Monitoring
- **Check Audit Logs**: Regularly review logs/audit.log for issues
- **Monitor Performance**: Watch for slow operations that might indicate problems
- **Validate Data**: Periodically export and verify your data integrity

---

*For additional support, refer to the Usage Guide and Interactive Mode Tutorial, or use the built-in help system.*