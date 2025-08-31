import bcrypt
import secrets
import string
from datetime import datetime, timedelta
import json
import os

class PasswordSecurity:
    """Handles secure password operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

class SessionManager:
    """Handles user sessions and authentication tokens"""
    
    SESSION_FILE = "active_sessions.json"
    SESSION_TIMEOUT = timedelta(hours=2)  # 2 hour timeout
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure random session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_session(username: str) -> str:
        """Create a new session for a user"""
        token = SessionManager.generate_session_token()
        expiry = datetime.now() + SessionManager.SESSION_TIMEOUT
        
        sessions = SessionManager._load_sessions()
        sessions[token] = {
            "username": username,
            "created": datetime.now().isoformat(),
            "expires": expiry.isoformat()
        }
        
        SessionManager._save_sessions(sessions)
        return token
    
    @staticmethod
    def validate_session(token: str) -> str:
        """Validate a session token and return username if valid"""
        sessions = SessionManager._load_sessions()
        
        if token not in sessions:
            return None
        
        session = sessions[token]
        expiry = datetime.fromisoformat(session["expires"])
        
        if datetime.now() > expiry:
            # Session expired, remove it
            del sessions[token]
            SessionManager._save_sessions(sessions)
            return None
        
        return session["username"]
    
    @staticmethod
    def invalidate_session(token: str) -> bool:
        """Invalidate a specific session"""
        sessions = SessionManager._load_sessions()
        
        if token in sessions:
            del sessions[token]
            SessionManager._save_sessions(sessions)
            return True
        
        return False
    
    @staticmethod
    def cleanup_expired_sessions():
        """Remove all expired sessions"""
        sessions = SessionManager._load_sessions()
        current_time = datetime.now()
        
        expired_tokens = []
        for token, session in sessions.items():
            expiry = datetime.fromisoformat(session["expires"])
            if current_time > expiry:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del sessions[token]
        
        if expired_tokens:
            SessionManager._save_sessions(sessions)
            print(f"Cleaned up {len(expired_tokens)} expired sessions")
    
    @staticmethod
    def _load_sessions() -> dict:
        """Load sessions from file"""
        if not os.path.exists(SessionManager.SESSION_FILE):
            return {}
        
        try:
            with open(SessionManager.SESSION_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return {}
    
    @staticmethod
    def _save_sessions(sessions: dict):
        """Save sessions to file"""
        try:
            with open(SessionManager.SESSION_FILE, 'w') as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")

class DataBackup:
    """Handles data backup and recovery"""
    
    BACKUP_DIR = "backups"
    MAX_BACKUPS = 10
    
    @staticmethod
    def create_backup(source_file: str) -> str:
        """Create a timestamped backup of a data file"""
        if not os.path.exists(source_file):
            return None
        
        # Create backup directory if it doesn't exist
        os.makedirs(DataBackup.BACKUP_DIR, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(source_file)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(DataBackup.BACKUP_DIR, backup_filename)
        
        try:
            # Copy the file
            with open(source_file, 'r') as src:
                with open(backup_path, 'w') as dst:
                    dst.write(src.read())
            
            # Clean up old backups
            DataBackup._cleanup_old_backups(name, ext)
            
            return backup_path
        
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    @staticmethod
    def _cleanup_old_backups(base_name: str, extension: str):
        """Remove old backups, keeping only the most recent MAX_BACKUPS"""
        if not os.path.exists(DataBackup.BACKUP_DIR):
            return
        
        # Find all backup files for this base name
        backup_files = []
        for filename in os.listdir(DataBackup.BACKUP_DIR):
            if filename.startswith(f"{base_name}_backup_") and filename.endswith(extension):
                filepath = os.path.join(DataBackup.BACKUP_DIR, filename)
                backup_files.append((filepath, os.path.getctime(filepath)))
        
        # Sort by creation time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old backups
        for filepath, _ in backup_files[DataBackup.MAX_BACKUPS:]:
            try:
                os.remove(filepath)
                print(f"Removed old backup: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"Error removing backup {filepath}: {e}")

def validate_data_integrity(data_file: str) -> bool:
    """Validate the integrity of a JSON data file"""
    if not os.path.exists(data_file):
        return False
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        # Basic structure validation
        if not isinstance(data, dict):
            return False
        
        # Validate each user entry
        for username, user_data in data.items():
            if not isinstance(user_data, dict):
                return False
            
            required_fields = ['username', 'password', 'email', 'accounts']
            if not all(field in user_data for field in required_fields):
                return False
            
            # Validate accounts structure
            if not isinstance(user_data['accounts'], list):
                return False
            
            for account in user_data['accounts']:
                if not isinstance(account, dict):
                    return False
                
                account_fields = ['account_type', 'balance', 'overdraft_limit', 'transactions']
                if not all(field in account for field in account_fields):
                    return False
        
        return True
    
    except Exception as e:
        print(f"Data validation error: {e}")
        return False