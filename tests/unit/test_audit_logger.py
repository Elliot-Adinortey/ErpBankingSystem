"""
Unit tests for the audit logging system
"""

import unittest
import tempfile
import shutil
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.audit_logger import (
    AuditLogger, AuditLogEntry, AuditEventType,
    get_audit_logger, initialize_audit_logger
)


class TestAuditLogEntry(unittest.TestCase):
    """Test cases for AuditLogEntry class"""
    
    def test_audit_log_entry_creation(self):
        """Test creating an audit log entry"""
        timestamp = datetime.now()
        entry = AuditLogEntry(
            timestamp=timestamp,
            event_type=AuditEventType.LOGIN_SUCCESS,
            user="testuser",
            session_id="session123",
            operation="User login",
            success=True,
            details={"ip": "127.0.0.1"},
            ip_address="127.0.0.1"
        )
        
        self.assertEqual(entry.timestamp, timestamp)
        self.assertEqual(entry.event_type, AuditEventType.LOGIN_SUCCESS)
        self.assertEqual(entry.user, "testuser")
        self.assertEqual(entry.session_id, "session123")
        self.assertEqual(entry.operation, "User login")
        self.assertTrue(entry.success)
        self.assertEqual(entry.details, {"ip": "127.0.0.1"})
        self.assertEqual(entry.ip_address, "127.0.0.1")
    
    def test_audit_log_entry_to_dict(self):
        """Test converting audit log entry to dictionary"""
        timestamp = datetime.now()
        entry = AuditLogEntry(
            timestamp=timestamp,
            event_type=AuditEventType.DEPOSIT,
            user="testuser",
            session_id="session123",
            operation="Deposit $100",
            success=True,
            details={"amount": 100.0, "account": "savings"}
        )
        
        entry_dict = entry.to_dict()
        
        self.assertEqual(entry_dict['timestamp'], timestamp.isoformat())
        self.assertEqual(entry_dict['event_type'], 'deposit')
        self.assertEqual(entry_dict['user'], 'testuser')
        self.assertEqual(entry_dict['operation'], 'Deposit $100')
        self.assertTrue(entry_dict['success'])
        self.assertEqual(entry_dict['details']['amount'], 100.0)
    
    def test_audit_log_entry_from_dict(self):
        """Test creating audit log entry from dictionary"""
        timestamp = datetime.now()
        entry_dict = {
            'timestamp': timestamp.isoformat(),
            'event_type': 'withdrawal',
            'user': 'testuser',
            'session_id': 'session123',
            'operation': 'Withdraw $50',
            'success': True,
            'details': {'amount': 50.0, 'account': 'current'},
            'ip_address': None,
            'user_agent': None,
            'error_message': None,
            'duration_ms': None
        }
        
        entry = AuditLogEntry.from_dict(entry_dict)
        
        self.assertEqual(entry.timestamp, timestamp)
        self.assertEqual(entry.event_type, AuditEventType.WITHDRAWAL)
        self.assertEqual(entry.user, 'testuser')
        self.assertEqual(entry.operation, 'Withdraw $50')
        self.assertTrue(entry.success)


class TestAuditLogger(unittest.TestCase):
    """Test cases for AuditLogger class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.audit_logger = AuditLogger(
            log_directory=self.temp_dir,
            log_file="test_audit.log",
            max_file_size=1024,  # Small size for testing rotation
            backup_count=2
        )
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_audit_logger_initialization(self):
        """Test audit logger initialization"""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertEqual(self.audit_logger.log_directory, self.temp_dir)
        self.assertEqual(self.audit_logger.log_file, "test_audit.log")
        self.assertEqual(self.audit_logger.max_file_size, 1024)
        self.assertEqual(self.audit_logger.backup_count, 2)
    
    def test_log_operation(self):
        """Test logging a basic operation"""
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="testuser",
            operation="Deposit $100 to savings",
            success=True,
            details={"amount": 100.0, "account": "savings"},
            session_id="session123"
        )
        
        # Check that log file was created and contains entry
        log_path = os.path.join(self.temp_dir, "test_audit.log")
        self.assertTrue(os.path.exists(log_path))
        
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn("testuser", log_content)
            self.assertIn("Deposit $100 to savings", log_content)
            self.assertIn("session123", log_content)
    
    def test_log_login_attempt_success(self):
        """Test logging successful login attempt"""
        self.audit_logger.log_login_attempt(
            username="testuser",
            success=True,
            ip_address="127.0.0.1",
            user_agent="TestAgent/1.0",
            session_id="session123"
        )
        
        log_path = os.path.join(self.temp_dir, "test_audit.log")
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn("testuser", log_content)
            self.assertIn("login_success", log_content)
            self.assertIn("127.0.0.1", log_content)
    
    def test_log_login_attempt_failure(self):
        """Test logging failed login attempt"""
        self.audit_logger.log_login_attempt(
            username="testuser",
            success=False,
            ip_address="127.0.0.1",
            failure_reason="Invalid password"
        )
        
        log_path = os.path.join(self.temp_dir, "test_audit.log")
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn("testuser", log_content)
            self.assertIn("login_failure", log_content)
            self.assertIn("Invalid password", log_content)
    
    def test_log_logout(self):
        """Test logging user logout"""
        # First log a login to track session
        self.audit_logger.log_login_attempt(
            username="testuser",
            success=True,
            session_id="session123"
        )
        
        # Then log logout
        self.audit_logger.log_logout(
            username="testuser",
            session_id="session123",
            ip_address="127.0.0.1"
        )
        
        log_path = os.path.join(self.temp_dir, "test_audit.log")
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn("logout", log_content)
            self.assertIn("testuser", log_content)
    
    def test_log_error(self):
        """Test logging errors with context"""
        try:
            raise ValueError("Test error message")
        except ValueError as e:
            self.audit_logger.log_error(
                error=e,
                context={"operation": "test_operation", "data": "test_data"},
                user="testuser",
                session_id="session123"
            )
        
        log_path = os.path.join(self.temp_dir, "test_audit.log")
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn("ValueError", log_content)
            self.assertIn("Test error message", log_content)
            self.assertIn("test_operation", log_content)
    
    def test_log_banking_operation(self):
        """Test logging banking-specific operations"""
        self.audit_logger.log_banking_operation(
            operation_type="deposit",
            user="testuser",
            account_identifier="savings",
            amount=100.0,
            success=True,
            session_id="session123",
            additional_details={"memo": "Salary deposit"}
        )
        
        log_path = os.path.join(self.temp_dir, "test_audit.log")
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn("deposit", log_content)
            self.assertIn("100.0", log_content)
            self.assertIn("savings", log_content)
            self.assertIn("Salary deposit", log_content)
    
    def test_log_system_event(self):
        """Test logging system events"""
        self.audit_logger.log_system_event(
            event="System startup",
            details={"version": "1.0.0", "config": "production"}
        )
        
        log_path = os.path.join(self.temp_dir, "test_audit.log")
        with open(log_path, 'r') as f:
            log_content = f.read()
            self.assertIn("System startup", log_content)
            self.assertIn("1.0.0", log_content)
    
    def test_get_audit_logs_basic(self):
        """Test retrieving audit logs"""
        # Log some test entries
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="user1",
            operation="Test deposit",
            success=True
        )
        
        self.audit_logger.log_operation(
            event_type=AuditEventType.WITHDRAWAL,
            user="user2",
            operation="Test withdrawal",
            success=True
        )
        
        # Retrieve logs
        logs = self.audit_logger.get_audit_logs(limit=10)
        
        self.assertEqual(len(logs), 3)  # 2 operations + 1 system initialization
        self.assertIsInstance(logs[0], AuditLogEntry)
    
    def test_get_audit_logs_with_filters(self):
        """Test retrieving audit logs with filters"""
        # Log test entries
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="user1",
            operation="Test deposit",
            success=True
        )
        
        self.audit_logger.log_operation(
            event_type=AuditEventType.WITHDRAWAL,
            user="user1",
            operation="Test withdrawal",
            success=False
        )
        
        # Filter by user
        logs = self.audit_logger.get_audit_logs(filters={'user': 'user1'})
        self.assertEqual(len(logs), 2)
        
        # Filter by success
        logs = self.audit_logger.get_audit_logs(filters={'success': True})
        self.assertGreaterEqual(len(logs), 1)
        
        # Filter by event type
        logs = self.audit_logger.get_audit_logs(filters={'event_type': 'deposit'})
        self.assertEqual(len(logs), 1)
    
    def test_get_audit_logs_with_date_range(self):
        """Test retrieving audit logs with date range"""
        # Log an entry
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="testuser",
            operation="Test deposit",
            success=True
        )
        
        # Get logs from last hour
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now() + timedelta(hours=1)
        
        logs = self.audit_logger.get_audit_logs(
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertGreaterEqual(len(logs), 1)
        
        # Get logs from future (should be empty)
        future_start = datetime.now() + timedelta(hours=1)
        future_end = datetime.now() + timedelta(hours=2)
        
        logs = self.audit_logger.get_audit_logs(
            start_date=future_start,
            end_date=future_end
        )
        
        self.assertEqual(len(logs), 0)
    
    def test_get_login_attempts(self):
        """Test retrieving login attempts"""
        # Log some login attempts
        self.audit_logger.log_login_attempt("user1", True, "127.0.0.1")
        self.audit_logger.log_login_attempt("user1", False, "127.0.0.1")
        self.audit_logger.log_login_attempt("user2", True, "192.168.1.1")
        
        # Get all login attempts
        attempts = self.audit_logger.get_login_attempts(hours=1)
        self.assertEqual(len(attempts), 3)
        
        # Get failed attempts only
        failed_attempts = self.audit_logger.get_login_attempts(hours=1, failed_only=True)
        self.assertEqual(len(failed_attempts), 1)
        
        # Get attempts for specific user
        user_attempts = self.audit_logger.get_login_attempts(username="user1", hours=1)
        self.assertEqual(len(user_attempts), 2)
    
    def test_get_user_activity(self):
        """Test retrieving user activity"""
        # Log some user activities
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="testuser",
            operation="Deposit",
            success=True
        )
        
        self.audit_logger.log_operation(
            event_type=AuditEventType.WITHDRAWAL,
            user="testuser",
            operation="Withdrawal",
            success=True
        )
        
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="otheruser",
            operation="Deposit",
            success=True
        )
        
        # Get activity for testuser
        activity = self.audit_logger.get_user_activity("testuser", hours=1)
        
        # Filter out system events that don't have a user
        user_activity = [entry for entry in activity if entry.user == "testuser"]
        self.assertEqual(len(user_activity), 2)
        
        # Verify all entries are for testuser
        for entry in user_activity:
            self.assertEqual(entry.user, "testuser")
    
    def test_get_error_logs(self):
        """Test retrieving error logs"""
        # Log some errors
        try:
            raise ValueError("Test error 1")
        except ValueError as e:
            self.audit_logger.log_error(e, {"context": "test1"})
        
        try:
            raise RuntimeError("Test error 2")
        except RuntimeError as e:
            self.audit_logger.log_error(e, {"context": "test2"})
        
        # Log a non-error operation
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="testuser",
            operation="Deposit",
            success=True
        )
        
        # Get error logs
        errors = self.audit_logger.get_error_logs(hours=1)
        self.assertEqual(len(errors), 2)
        
        # Verify all entries are errors
        for entry in errors:
            self.assertEqual(entry.event_type, AuditEventType.ERROR)
            self.assertFalse(entry.success)
    
    def test_get_statistics(self):
        """Test getting audit log statistics"""
        # Log various operations
        self.audit_logger.log_login_attempt("user1", True)
        self.audit_logger.log_login_attempt("user1", False)
        self.audit_logger.log_operation(
            event_type=AuditEventType.DEPOSIT,
            user="user1",
            operation="Deposit",
            success=True
        )
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            self.audit_logger.log_error(e, {"context": "test"})
        
        # Get statistics
        stats = self.audit_logger.get_statistics(hours=1)
        
        self.assertIn('total_events', stats)
        self.assertIn('successful_operations', stats)
        self.assertIn('failed_operations', stats)
        self.assertIn('unique_users', stats)
        self.assertIn('event_types', stats)
        self.assertIn('login_attempts', stats)
        self.assertIn('successful_logins', stats)
        self.assertIn('failed_logins', stats)
        
        self.assertGreaterEqual(stats['total_events'], 4)
        self.assertEqual(stats['successful_logins'], 1)
        self.assertEqual(stats['failed_logins'], 1)
        self.assertGreaterEqual(stats['error_count'], 1)
    
    def test_cleanup_old_sessions(self):
        """Test cleaning up old session data"""
        # Add some sessions
        self.audit_logger._current_sessions["session1"] = {
            "username": "user1",
            "login_time": datetime.now() - timedelta(hours=25),  # Old session
            "ip_address": "127.0.0.1"
        }
        
        self.audit_logger._current_sessions["session2"] = {
            "username": "user2",
            "login_time": datetime.now() - timedelta(minutes=30),  # Recent session
            "ip_address": "127.0.0.1"
        }
        
        # Clean up old sessions
        self.audit_logger.cleanup_old_sessions()
        
        # Check that old session was removed
        self.assertNotIn("session1", self.audit_logger._current_sessions)
        self.assertIn("session2", self.audit_logger._current_sessions)


class TestAuditLoggerSingleton(unittest.TestCase):
    """Test cases for audit logger singleton functionality"""
    
    def test_get_audit_logger_singleton(self):
        """Test that get_audit_logger returns singleton instance"""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        
        self.assertIs(logger1, logger2)
    
    def test_initialize_audit_logger(self):
        """Test initializing audit logger with custom config"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            logger = initialize_audit_logger(
                log_directory=temp_dir,
                log_file="custom_audit.log",
                max_file_size=2048,
                backup_count=3
            )
            
            self.assertEqual(logger.log_directory, temp_dir)
            self.assertEqual(logger.log_file, "custom_audit.log")
            self.assertEqual(logger.max_file_size, 2048)
            self.assertEqual(logger.backup_count, 3)
            
            # Test that subsequent calls return the same instance
            logger2 = get_audit_logger()
            self.assertIs(logger, logger2)
            
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()