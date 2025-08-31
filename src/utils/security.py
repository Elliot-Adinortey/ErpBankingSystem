import bcrypt
import secrets
import json
import os
from datetime import datetime, timedelta

class PasswordManager:
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
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure random session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_session(username: str) -> str:
        """Create a new session for a user"""
        token = SessionManager.generate_session_token()
        expiry = datetime.now() + timedelta(seconds=SessionManager.SESSION_TIMEOUT)
        
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
        backup_filename = f"{os.path.basename(source_file)}.backup_{timestamp}"
        backup_path = os.path.join(DataBackup.BACKUP_DIR, backup_filename)
        
        try:
            # Copy the file
            import shutil
            shutil.copy2(source_file, backup_path)
            
            # Clean up old backups
            DataBackup._cleanup_old_backups(source_file)
            
            print(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    @staticmethod
    def _cleanup_old_backups(source_file: str):
        """Remove old backups, keeping only the most recent ones"""
        if not os.path.exists(DataBackup.BACKUP_DIR):
            return
        
        base_name = os.path.basename(source_file)
        backup_files = []
        
        # Find all backup files for this source
        for filename in os.listdir(DataBackup.BACKUP_DIR):
            if filename.startswith(f"{base_name}.backup_"):
                backup_path = os.path.join(DataBackup.BACKUP_DIR, filename)
                backup_files.append((backup_path, os.path.getctime(backup_path)))
        
        # Sort by creation time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old backups if we exceed the limit
        if len(backup_files) > DataBackup.MAX_BACKUPS:
            for backup_path, _ in backup_files[DataBackup.MAX_BACKUPS:]:
                try:
                    os.remove(backup_path)
                    print(f"Removed old backup: {backup_path}")
                except Exception as e:
                    print(f"Error removing old backup {backup_path}: {e}")
    
    @staticmethod
    def list_backups(source_file: str) -> list:
        """List all available backups for a source file"""
        if not os.path.exists(DataBackup.BACKUP_DIR):
            return []
        
        base_name = os.path.basename(source_file)
        backups = []
        
        for filename in os.listdir(DataBackup.BACKUP_DIR):
            if filename.startswith(f"{base_name}.backup_"):
                backup_path = os.path.join(DataBackup.BACKUP_DIR, filename)
                timestamp = os.path.getctime(backup_path)
                backups.append({
                    'path': backup_path,
                    'filename': filename,
                    'created': datetime.fromtimestamp(timestamp).isoformat()
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups