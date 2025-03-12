import sqlite3
import json
import os
import pickle
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aliscan.db')

def init_db():
    """Initialize the database and create necessary tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        alignment_file TEXT,
        state_pickle BLOB,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def store_state(session_id, state, alignment_file=None):
    """Store or update state in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Check if session exists
    cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
    if cursor.fetchone():
        # Update existing session
        cursor.execute(
            "UPDATE sessions SET state_pickle = ?, updated_at = ? WHERE session_id = ?",
            (pickle.dumps(state), now, session_id)
        )
    else:
        # Create new session
        cursor.execute(
            "INSERT INTO sessions (session_id, alignment_file, state_pickle, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, alignment_file, pickle.dumps(state), now, now)
        )
    
    conn.commit()
    conn.close()
    return session_id

def get_state(session_id):
    """Retrieve state from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT state_pickle FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return pickle.loads(row['state_pickle'])
    return None

def get_alignment_file(session_id):
    """Get the alignment file path for a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT alignment_file FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return row['alignment_file']
    return None

def delete_session(session_id):
    """Delete a session from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    
    conn.commit()
    conn.close()
