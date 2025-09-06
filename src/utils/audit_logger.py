"""
Audit Logging System for Banking Application

This module provides comprehensive audit logging functionality including:
- Operation tracking with timestamps and user context
- Login attempt logging with success/failure tracking
- Error logging with detailed context information
- Log rotation and file management
- Audit log filtering and search functionality
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from logging.handlers import RotatingFileHandler
import threading
from dataclasses import dataclass, asdict
from enum import Enum


class AuditEventType(Enum):
    """Enumeration of audit event types"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    ACCOUNT_CREATE = "account_create"
    ACCOUNT_UPDATE = "account_update"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    BALANCE_INQUIRY = "balance_inquiry"
    TRANSACTION_HISTORY = "transaction_history"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    BATCH_OPERATION = "batch_operation"
    SESSION_EXPIRED = "session_expired"
    ERROR = "error"
    SYSTEM_EVENT = "system_event"


@dataclass
class AuditLogEntry:
    """
    Represents a single audit log entry with all relevant information
    """
    timestamp: datetime
    event_type: AuditEventType
    user: Optional[str]
    session_id: Optional[str]
    operation: str
    success: bool
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['event_type'] = self.event_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLogEntry':
        """Create audit entry from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['event_type'] = AuditEventType(data['event_type'])
        return cls(**data)


class AuditLogger:
    """
    Comprehensive audit logging system with operation tracking,
    log rotation, and filtering capabilities
    """
    
    def __init__(self, 
                 log_directory: str = "logs",
                 log_file: str = "audit.log",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 log_level: int = logging.INFO):
        """
        Initialize audit logger with configuration
        
        Args:
            log_directory: Directory to store log files
            log_file: Name of the main log file
            max_file_size: Maximum size of log file before rotation (bytes)
            backup_count: Number of backup files to keep
            log_level: Logging level
        """
        self.log_directory = log_directory
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.log_level = log_level
        
        # Thread lock for concurrent access
        self._lock = threading.Lock()
        
        # Create log directory if it doesn't exist
        os.makedirs(log_directory, exist_ok=True)
        
        # Set up logging configuration
        self._setup_logger()
        
        # Current session tracking
        self._current_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize audit logger
        self.log_system_event("audit_logger_initialized", {
            "log_directory": log_directory,
            "log_file": log_file,
            "max_file_size": max_file_size,
            "backup_count": backup_count
        })
    
    def _setup_logger(self) -> None:
        """Set up the logging configuration with rotation"""
        log_path = os.path.join(self.log_directory, self.log_file)
        
        # Create logger
        self.logger = logging.getLogger('audit_logger')
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create rotating file handler
        handler = RotatingFileHandler(
            log_path,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # Create formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def log_operation(self, 
                     event_type: Union[AuditEventType, str],
                     user: Optional[str],
                     operation: str,
                     success: bool = True,
                     details: Optional[Dict[str, Any]] = None,
                     session_id: Optional[str] = None,
                     ip_address: Optional[str] = None,
                     duration_ms: Optional[int] = None,
                     error_message: Optional[str] = None) -> None:
        """
        Log a banking operation with full context
        
        Args:
            event_type: Type of event being logged
            user: Username performing the operation
            operation: Description of the operation
            success: Whether the operation was successful
            details: Additional operation details
            session_id: Session identifier
            ip_address: IP address of the user
            duration_ms: Operation duration in milliseconds
        """
        with self._lock:
            # Convert string event type to enum if needed
            if isinstance(event_type, str):
                try:
                    event_type = AuditEventType(event_type)
                except ValueError:
                    event_type = AuditEventType.SYSTEM_EVENT
            
            # Create audit entry
            entry = AuditLogEntry(
                timestamp=datetime.now(),
                event_type=event_type,
                user=user,
                session_id=session_id,
                operation=operation,
                success=success,
                details=details or {},
                ip_address=ip_address,
                duration_ms=duration_ms,
                error_message=error_message
            )
            
            # Log the entry
            self._write_log_entry(entry)
    
    def log_login_attempt(self, 
                         username: str, 
                         success: bool, 
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None,
                         session_id: Optional[str] = None,
                         failure_reason: Optional[str] = None) -> None:
        """
        Log login attempts with success/failure tracking
        
        Args:
            username: Username attempting to login
            success: Whether login was successful
            ip_address: IP address of login attempt
            user_agent: User agent string
            session_id: Session ID if login successful
            failure_reason: Reason for login failure
        """
        event_type = AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILURE
        
        details = {
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        if not success and failure_reason:
            details["failure_reason"] = failure_reason
        
        if success and session_id:
            details["session_id"] = session_id
            # Track session
            self._current_sessions[session_id] = {
                "username": username,
                "login_time": datetime.now(),
                "ip_address": ip_address
            }
        
        self.log_operation(
            event_type=event_type,
            user=username if success else None,
            operation=f"Login attempt for user: {username}",
            success=success,
            details=details,
            session_id=session_id,
            ip_address=ip_address
        )
    
    def log_logout(self, 
                  username: str, 
                  session_id: Optional[str] = None,
                  ip_address: Optional[str] = None) -> None:
        """
        Log user logout
        
        Args:
            username: Username logging out
            session_id: Session ID being terminated
            ip_address: IP address of logout
        """
        details = {"username": username}
        
        # Calculate session duration if we have session info
        if session_id and session_id in self._current_sessions:
            session_info = self._current_sessions[session_id]
            session_duration = datetime.now() - session_info["login_time"]
            details["session_duration_minutes"] = int(session_duration.total_seconds() / 60)
            
            # Remove from current sessions
            del self._current_sessions[session_id]
        
        self.log_operation(
            event_type=AuditEventType.LOGOUT,
            user=username,
            operation=f"User logout: {username}",
            success=True,
            details=details,
            session_id=session_id,
            ip_address=ip_address
        )
    
    def log_error(self, 
                 error: Exception, 
                 context: Dict[str, Any],
                 user: Optional[str] = None,
                 session_id: Optional[str] = None,
                 operation: Optional[str] = None) -> None:
        """
        Log errors with detailed context information
        
        Args:
            error: Exception that occurred
            context: Context information about the error
            user: User associated with the error
            session_id: Session ID when error occurred
            operation: Operation being performed when error occurred
        """
        details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        # Add stack trace for debugging (truncated for security)
        import traceback
        stack_trace = traceback.format_exc()
        details["stack_trace"] = stack_trace[:1000] + "..." if len(stack_trace) > 1000 else stack_trace
        
        self.log_operation(
            event_type=AuditEventType.ERROR,
            user=user,
            operation=operation or f"Error occurred: {type(error).__name__}",
            success=False,
            details=details,
            session_id=session_id,
            error_message=str(error)
        )
    
    def log_banking_operation(self,
                            operation_type: str,
                            user: str,
                            account_identifier: str,
                            amount: Optional[float] = None,
                            success: bool = True,
                            session_id: Optional[str] = None,
                            additional_details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log banking-specific operations (deposits, withdrawals, transfers)
        
        Args:
            operation_type: Type of banking operation
            user: Username performing operation
            account_identifier: Account involved in operation
            amount: Amount involved (if applicable)
            success: Whether operation was successful
            session_id: Session ID
            additional_details: Additional operation-specific details
        """
        # Map operation types to audit event types
        event_type_mapping = {
            "deposit": AuditEventType.DEPOSIT,
            "withdrawal": AuditEventType.WITHDRAWAL,
            "withdraw": AuditEventType.WITHDRAWAL,
            "transfer": AuditEventType.TRANSFER,
            "balance_inquiry": AuditEventType.BALANCE_INQUIRY,
            "account_create": AuditEventType.ACCOUNT_CREATE,
            "account_update": AuditEventType.ACCOUNT_UPDATE
        }
        
        event_type = event_type_mapping.get(operation_type.lower(), AuditEventType.SYSTEM_EVENT)
        
        details = {
            "operation_type": operation_type,
            "account_identifier": account_identifier
        }
        
        if amount is not None:
            details["amount"] = amount
        
        if additional_details:
            details.update(additional_details)
        
        operation_desc = f"{operation_type.capitalize()}"
        if amount is not None:
            operation_desc += f" ${amount:.2f}"
        operation_desc += f" - Account: {account_identifier}"
        
        self.log_operation(
            event_type=event_type,
            user=user,
            operation=operation_desc,
            success=success,
            details=details,
            session_id=session_id
        )
    
    def log_system_event(self, 
                        event: str, 
                        details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log system-level events
        
        Args:
            event: Description of system event
            details: Additional event details
        """
        self.log_operation(
            event_type=AuditEventType.SYSTEM_EVENT,
            user=None,
            operation=f"System event: {event}",
            success=True,
            details=details or {}
        )
    
    def _write_log_entry(self, entry: AuditLogEntry) -> None:
        """
        Write audit entry to log file
        
        Args:
            entry: Audit log entry to write
        """
        try:
            # Convert entry to JSON for structured logging
            log_data = entry.to_dict()
            log_message = json.dumps(log_data, ensure_ascii=False)
            
            # Write to log file
            if entry.success:
                self.logger.info(log_message)
            else:
                self.logger.error(log_message)
                
        except Exception as e:
            # Fallback logging if JSON serialization fails
            fallback_message = f"AUDIT_LOG_ERROR: {entry.operation} | User: {entry.user} | Error: {str(e)}"
            self.logger.error(fallback_message)
    
    def get_audit_logs(self, 
                      filters: Optional[Dict[str, Any]] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      limit: int = 1000) -> List[AuditLogEntry]:
        """
        Retrieve audit logs with filtering options
        
        Args:
            filters: Dictionary of filters to apply
            start_date: Start date for log retrieval
            end_date: End date for log retrieval
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries matching criteria
        """
        entries = []
        log_path = os.path.join(self.log_directory, self.log_file)
        
        try:
            # Read from current log file and backup files
            log_files = [log_path]
            
            # Add backup files
            for i in range(1, self.backup_count + 1):
                backup_file = f"{log_path}.{i}"
                if os.path.exists(backup_file):
                    log_files.append(backup_file)
            
            # Process log files in reverse order (newest first)
            for log_file in log_files:
                if not os.path.exists(log_file):
                    continue
                    
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in reversed(f.readlines()):
                        if len(entries) >= limit:
                            break
                            
                        try:
                            # Parse log line
                            if '|' in line and '{' in line:
                                # Extract JSON part from log line
                                json_part = line.split('|', 3)[-1].strip()
                                log_data = json.loads(json_part)
                                entry = AuditLogEntry.from_dict(log_data)
                                
                                # Apply filters
                                if self._matches_filters(entry, filters, start_date, end_date):
                                    entries.append(entry)
                                    
                        except (json.JSONDecodeError, ValueError, KeyError):
                            # Skip malformed log entries
                            continue
                
                if len(entries) >= limit:
                    break
        
        except Exception as e:
            self.log_error(e, {"operation": "get_audit_logs"})
        
        return entries[:limit]
    
    def _matches_filters(self, 
                        entry: AuditLogEntry,
                        filters: Optional[Dict[str, Any]],
                        start_date: Optional[datetime],
                        end_date: Optional[datetime]) -> bool:
        """
        Check if audit entry matches the specified filters
        
        Args:
            entry: Audit log entry to check
            filters: Filters to apply
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            True if entry matches all filters
        """
        # Date range filter
        if start_date and entry.timestamp < start_date:
            return False
        if end_date and entry.timestamp > end_date:
            return False
        
        # Apply other filters
        if filters:
            for key, value in filters.items():
                if key == 'user':
                    # For login failures, user might be None, so check details too
                    if entry.user != value:
                        if 'username' in entry.details and entry.details['username'] == value:
                            pass  # Match found in details
                        else:
                            return False
                elif key == 'event_type':
                    if isinstance(value, str):
                        if entry.event_type.value != value:
                            return False
                    elif isinstance(value, list):
                        if entry.event_type.value not in value:
                            return False
                elif key == 'success' and entry.success != value:
                    return False
                elif key == 'session_id' and entry.session_id != value:
                    return False
                elif key == 'operation' and value.lower() not in entry.operation.lower():
                    return False
        
        return True
    
    def get_login_attempts(self, 
                          username: Optional[str] = None,
                          hours: int = 24,
                          failed_only: bool = False) -> List[AuditLogEntry]:
        """
        Get recent login attempts
        
        Args:
            username: Filter by specific username
            hours: Number of hours to look back
            failed_only: Only return failed attempts
            
        Returns:
            List of login attempt entries
        """
        start_date = datetime.now() - timedelta(hours=hours)
        
        filters = {
            'event_type': [AuditEventType.LOGIN_SUCCESS.value, AuditEventType.LOGIN_FAILURE.value]
        }
        
        if failed_only:
            filters['event_type'] = [AuditEventType.LOGIN_FAILURE.value]
        
        if username:
            filters['user'] = username
        
        return self.get_audit_logs(filters=filters, start_date=start_date)
    
    def get_user_activity(self, 
                         username: str,
                         hours: int = 24) -> List[AuditLogEntry]:
        """
        Get recent activity for a specific user
        
        Args:
            username: Username to get activity for
            hours: Number of hours to look back
            
        Returns:
            List of user activity entries
        """
        start_date = datetime.now() - timedelta(hours=hours)
        filters = {'user': username}
        
        return self.get_audit_logs(filters=filters, start_date=start_date)
    
    def get_error_logs(self, hours: int = 24) -> List[AuditLogEntry]:
        """
        Get recent error logs
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of error log entries
        """
        start_date = datetime.now() - timedelta(hours=hours)
        filters = {'event_type': AuditEventType.ERROR.value}
        
        return self.get_audit_logs(filters=filters, start_date=start_date)
    
    def cleanup_old_sessions(self) -> None:
        """Clean up old session tracking data"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_info in self._current_sessions.items():
            # Consider sessions older than 24 hours as expired
            if current_time - session_info["login_time"] > timedelta(hours=24):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._current_sessions[session_id]
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get audit log statistics for the specified time period
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary containing statistics
        """
        start_date = datetime.now() - timedelta(hours=hours)
        entries = self.get_audit_logs(start_date=start_date, limit=10000)
        
        stats = {
            'total_events': len(entries),
            'successful_operations': sum(1 for e in entries if e.success),
            'failed_operations': sum(1 for e in entries if not e.success),
            'unique_users': len(set(e.user for e in entries if e.user)),
            'event_types': {},
            'users_activity': {},
            'error_count': sum(1 for e in entries if e.event_type == AuditEventType.ERROR),
            'login_attempts': sum(1 for e in entries if e.event_type in [AuditEventType.LOGIN_SUCCESS, AuditEventType.LOGIN_FAILURE]),
            'successful_logins': sum(1 for e in entries if e.event_type == AuditEventType.LOGIN_SUCCESS),
            'failed_logins': sum(1 for e in entries if e.event_type == AuditEventType.LOGIN_FAILURE)
        }
        
        # Count event types
        for entry in entries:
            event_type = entry.event_type.value
            stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
        
        # Count user activity
        for entry in entries:
            if entry.user:
                stats['users_activity'][entry.user] = stats['users_activity'].get(entry.user, 0) + 1
        
        return stats
    
    def get_recent_operations(self, 
                             user: Optional[str] = None,
                             operation_type: Optional[str] = None,
                             hours: int = 24,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent operations with filtering
        
        Args:
            user: Filter by specific user
            operation_type: Filter by operation type (e.g., 'batch_operations')
            hours: Number of hours to look back
            limit: Maximum number of operations to return
            
        Returns:
            List of operation dictionaries
        """
        start_date = datetime.now() - timedelta(hours=hours)
        
        filters = {}
        if user:
            filters['user'] = user
        if operation_type:
            filters['operation'] = operation_type
        
        entries = self.get_audit_logs(filters=filters, start_date=start_date, limit=limit)
        
        # Convert to dictionaries for easier handling
        operations = []
        for entry in entries:
            operations.append({
                'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'event_type': entry.event_type.value,
                'user': entry.user,
                'operation': entry.operation,
                'success': entry.success,
                'details': entry.details,
                'session_id': entry.session_id
            })
        
        return operations


# Global audit logger instance
_audit_logger_instance: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """
    Get the global audit logger instance (singleton pattern)
    
    Returns:
        AuditLogger instance
    """
    global _audit_logger_instance
    
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    
    return _audit_logger_instance


def initialize_audit_logger(log_directory: str = "logs",
                           log_file: str = "audit.log",
                           max_file_size: int = 10 * 1024 * 1024,
                           backup_count: int = 5) -> AuditLogger:
    """
    Initialize the global audit logger with custom configuration
    
    Args:
        log_directory: Directory to store log files
        log_file: Name of the main log file
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured AuditLogger instance
    """
    global _audit_logger_instance
    
    _audit_logger_instance = AuditLogger(
        log_directory=log_directory,
        log_file=log_file,
        max_file_size=max_file_size,
        backup_count=backup_count
    )
    
    return _audit_logger_instance