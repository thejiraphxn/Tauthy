import sqlite3
import uuid
import bcrypt
from datetime import datetime
DB_NAME = "db/data_database.db"

def get_db_connection():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            user_username TEXT UNIQUE NOT NULL,
            user_password TEXT NOT NULL,
            user_firstname TEXT NOT NULL,
            user_lastname TEXT NOT NULL,
            user_email TEXT,
            user_created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS history (
            hs_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            hs_input_text TEXT NOT NULL,
            hs_result_ai REAL,
            hs_result_human REAL,
            hs_user_feedback TEXT,
            hs_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    ''')

    conn.commit()
    conn.close()

# ==============================
# USER FUNCTIONS
# ==============================

def hash_password(password):
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(password, hashed_password):
    """Verify password against hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def create_user(firstname, lastname, username, password, email=None):
    """Register a new user."""
    conn = get_db_connection()
    cur = conn.cursor()

    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(password)

    try:
        cur.execute('''
            INSERT INTO users (user_id, user_username, user_password, user_firstname, user_lastname, user_email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, hashed_pw, firstname, lastname, email))

        conn.commit()
        return True, "User registered successfully."

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    finally:
        conn.close()

def login(username, password):
    """Login user and return user data if success."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT * FROM users WHERE user_username = ?
    ''', (username,))

    user = cur.fetchone()
    conn.close()

    if user and verify_password(password, user['user_password']):
        return True, dict(user)
    else:
        return False, "Invalid username or password."


def save_input(user_id, input_text, result_ai, result_human):
    """Save input data along with prediction results."""
    conn = get_db_connection()
    cur = conn.cursor()

    hs_id = str(uuid.uuid4())

    cur.execute('''
        INSERT INTO history (hs_id, user_id, hs_input_text, hs_result_ai, hs_result_human)
        VALUES (?, ?, ?, ?, ?)
    ''', (hs_id, user_id, input_text, result_ai, result_human))

    conn.commit()
    conn.close()

    return hs_id 

def update_feedback(hs_id, feedback):
    """Update user feedback for specific input."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        UPDATE history
        SET hs_user_feedback = ?
        WHERE hs_id = ?
    ''', (feedback, hs_id))

    conn.commit()
    conn.close()

def get_user_history(user_id):
    """Get all input history for a specific user."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT * FROM history
        WHERE user_id = ?
        ORDER BY hs_created_at DESC
    ''', (user_id,))

    results = cur.fetchall()
    conn.close()

    return [dict(row) for row in results]
