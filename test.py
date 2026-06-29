from fastmcp import FastMCP
import os
import sys
import sqlite3

ROOT_DIR = os.path.dirname(__file__)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DB_PATH = os.path.join(ROOT_DIR, "expenses.db")
mcp = FastMCP(name="Expense Tracker")

def init_db():
    """Initializes the SQLite database and creates the expenses table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@mcp.tool()
def add_expense(date: str, amount: float, category: str, subcategory: str = '', note: str = '') -> None:
    """Adds a new expense to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (date, amount, category, subcategory, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, amount, category, subcategory, note))
    conn.commit()
    conn.close()
    return {"status": "ok", "id": cursor.lastrowid}

@mcp.tool()
def list_expenses() -> list[dict]:
    """Lists all expenses in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses ORDER BY id ASC')
    rows = cursor.fetchall()
    conn.close()
    cols = [d[0] for d in cursor.description] #cursor.description provides column names
    return [dict(zip(cols, row)) for row in rows] #converting each row to a dictionary

if __name__ == "__main__":
    mcp.run(transport="sse")