"""
Database operations for Re:Gain Bot
"""
import sqlite3
from datetime import datetime
from typing import Optional, List
from config import DATABASE_FILE, TOKEN_SYSTEM, TARGET_TOKENS

class Database:
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                matric_number TEXT UNIQUE NOT NULL,
                full_name TEXT,
                total_tokens INTEGER DEFAULT 0,
                starpoint_eligible BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                photo_file_id TEXT NOT NULL,
                tokens_awarded INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                verified_by INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Verification table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verifications (
                verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL UNIQUE,
                admin_id INTEGER NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT,
                verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(submission_id) REFERENCES submissions(submission_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User operations
    def register_user(self, user_id: int, matric_number: str, full_name: str = None) -> bool:
        """Register a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (user_id, matric_number, full_name)
                VALUES (?, ?, ?)
            ''', (user_id, matric_number, full_name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id: int):
        """Get user by user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        return self.get_user(user_id) is not None
    
    def get_user_by_matric(self, matric_number: str):
        """Get user by matric number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE matric_number = ?', (matric_number,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    # Submission operations
    def create_submission(self, user_id: int, category: str, photo_file_id: str, tokens: int) -> int:
        """Create a new submission"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO submissions (user_id, category, photo_file_id, tokens_awarded)
            VALUES (?, ?, ?, ?)
        ''', (user_id, category, photo_file_id, tokens))
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return submission_id
    
    def get_pending_submissions(self) -> List:
        """Get all pending submissions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, u.matric_number, u.full_name 
            FROM submissions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.status = 'pending'
            ORDER BY s.created_at ASC
        ''')
        submissions = cursor.fetchall()
        conn.close()
        return submissions
    
    def get_submission(self, submission_id: int):
        """Get submission by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM submissions WHERE submission_id = ?', (submission_id,))
        submission = cursor.fetchone()
        conn.close()
        return submission
    
    def approve_submission(self, submission_id: int, admin_id: int) -> bool:
        """Approve a submission and award tokens"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get submission details
            submission = self.get_submission(submission_id)
            if not submission:
                return False
            
            user_id = submission['user_id']
            tokens = submission['tokens_awarded']
            
            # Update submission status
            cursor.execute('''
                UPDATE submissions 
                SET status = 'approved', verified_at = CURRENT_TIMESTAMP, verified_by = ?
                WHERE submission_id = ?
            ''', (admin_id, submission_id))
            
            # Update user tokens
            cursor.execute('''
                UPDATE users 
                SET total_tokens = total_tokens + ?
                WHERE user_id = ?
            ''', (tokens, user_id))
            
            # Check if user reached target
            cursor.execute('SELECT total_tokens FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            if user['total_tokens'] >= TARGET_TOKENS:
                cursor.execute('''
                    UPDATE users 
                    SET starpoint_eligible = 1
                    WHERE user_id = ?
                ''', (user_id,))
            
            # Record verification
            cursor.execute('''
                INSERT INTO verifications (submission_id, admin_id, decision)
                VALUES (?, ?, 'approved')
            ''', (submission_id, admin_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error approving submission: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def reject_submission(self, submission_id: int, admin_id: int, reason: str = None) -> bool:
        """Reject a submission"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE submissions 
                SET status = 'rejected', verified_at = CURRENT_TIMESTAMP, verified_by = ?
                WHERE submission_id = ?
            ''', (admin_id, submission_id))
            
            cursor.execute('''
                INSERT INTO verifications (submission_id, admin_id, decision, reason)
                VALUES (?, ?, 'rejected', ?)
            ''', (submission_id, admin_id, reason))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error rejecting submission: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                u.total_tokens,
                u.starpoint_eligible,
                COUNT(CASE WHEN s.status = 'approved' THEN 1 END) as approved_count,
                COUNT(CASE WHEN s.status = 'pending' THEN 1 END) as pending_count,
                COUNT(CASE WHEN s.status = 'rejected' THEN 1 END) as rejected_count
            FROM users u
            LEFT JOIN submissions s ON u.user_id = s.user_id
            WHERE u.user_id = ?
            GROUP BY u.user_id
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total_tokens': row['total_tokens'],
                'starpoint_eligible': bool(row['starpoint_eligible']),
                'approved_count': row['approved_count'],
                'pending_count': row['pending_count'],
                'rejected_count': row['rejected_count']
            }
        return None

    def get_eligible_users(self) -> List:
        """Get all users who are starpoint eligible"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, matric_number, full_name, total_tokens, created_at
            FROM users
            WHERE starpoint_eligible = 1
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
