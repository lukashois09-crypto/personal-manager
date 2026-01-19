import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "personal.db")

def connect():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def create_table():
    """Create the users table if it doesn't exist."""
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                telefonnummer TEXT,
                berufstitel TEXT   
            )        
        """)
        conn.commit()

def insert_sample():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, telefonnummer, berufstitel) VALUES (?, ?, ?, ?)",
                    ("Alice Müller", "alice@example.com", "123456789", "Manager"))
        cur.execute("INSERT INTO users (name, email, telefonnummer, berufstitel) VALUES (?, ?, ?, ?)",
                    ("Tom Becker", "tom@example.com", "987654321", "Techniker"))
        conn.commit()

def get_employees_basic():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, berufstitel FROM users")
        return cur.fetchall()
    
def add_user(name, email, telefonnummer, berufstitel):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, telefonnummer, berufstitel) VALUES (?, ?, ?, ?)",
                    (name, email, telefonnummer, berufstitel)
        )
        conn.commit()

def delete_user(user_id):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

def update_user(user_id, name, email, telefonnummer, berufstitel):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users 
            SET name = ?, email = ?, telefonnummer = ?, berufstitel = ?
            WHERE id = ?
        """, (name, email, telefonnummer, berufstitel, user_id))
        conn.commit()

def get_employee_details(user_id):
    """Return full details of one employee."""
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT name, berufstitel, email, telefonnummer FROM users WHERE id = ?",
            (user_id,)
        )
        return cur.fetchone()


def search_employees(search_term):
    """Return basic employee data filtered by name or berufstitel."""
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, berufstitel
            FROM users
            WHERE LOWER(name) LIKE ? OR LOWER(berufstitel) LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        return cur.fetchall()
