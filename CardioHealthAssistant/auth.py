import sqlite3
import hashlib
import os
import uuid
from datetime import datetime, timedelta

class UserAuthentication:
    def __init__(self, db_path='users.db'):
        """
        Initialize user authentication system with SQLite database.
        
        :param db_path: Path to SQLite database file
        """
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create necessary tables for user management."""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id TEXT,
                session_token TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        self.conn.commit()

    def _hash_password(self, password, salt=None):
        """
        Hash password with salt.
        
        :param password: Plain text password
        :param salt: Optional salt, generated if not provided
        :return: Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = os.urandom(32)  # 32 bytes = 256 bits
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',  # Hash digest algorithm
            password.encode('utf-8'),
            salt,
            100000  # Number of iterations
        )
        
        return pwd_hash, salt

    def register_user(self, username, email, password):
        """
        Register a new user.
        
        :param username: Unique username
        :param email: User's email
        :param password: User's password
        :return: User ID or None if registration fails
        """
        try:
            # Check if username or email already exists
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                return None
            
            # Generate user ID
            user_id = str(uuid.uuid4())
            
            # Hash password
            pwd_hash, salt = self._hash_password(password)
            
            # Insert user
            cursor.execute('''
                INSERT INTO users 
                (id, username, email, password_hash, salt) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, email, pwd_hash, salt))
            
            self.conn.commit()
            return user_id
        
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def login(self, username, password):
        """
        Authenticate user and create a session.
        
        :param username: Username
        :param password: Password
        :return: Session token or None if login fails
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            return None
        
        # Unpack user data
        user_id, db_username, email, db_pwd_hash, salt, created_at, last_login = user
        
        # Verify password
        pwd_hash, _ = self._hash_password(password, bytes.fromhex(salt))
        
        if pwd_hash != bytes.fromhex(db_pwd_hash):
            return None
        
        # Create session token
        session_token = str(uuid.uuid4())
        session_expires = datetime.now() + timedelta(hours=24)  # Token valid for 24 hours
        
        cursor.execute('''
            INSERT INTO sessions 
            (user_id, session_token, expires_at) 
            VALUES (?, ?, ?)
        ''', (user_id, session_token, session_expires))
        
        # Update last login
        cursor.execute('''
            UPDATE users 
            SET last_login = ? 
            WHERE id = ?
        ''', (datetime.now(), user_id))
        
        self.conn.commit()
        return session_token

    def validate_session(self, session_token):
        """
        Validate an existing session.
        
        :param session_token: Session token to validate
        :return: User ID if valid, None otherwise
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id FROM sessions 
            WHERE session_token = ? AND expires_at > ?
        ''', (session_token, datetime.now()))
        
        result = cursor.fetchone()
        return result[0] if result else None

    def logout(self, session_token):
        """
        Invalidate a session.
        
        :param session_token: Session token to invalidate
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()

# Global authentication manager
auth_manager = UserAuthentication()
