from fastmcp import FastMCP
import os
import sys
import sqlite3

ROOT_DIR = os.path.dirname(__file__)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DB_PATH = "/tmp/expenses.db"
CATEGORIES_PATH = os.path.join(ROOT_DIR, "categories.json")
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
def list_expenses(start_date, end_date) -> list[dict]:
    """Lists all expenses in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = 'SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id ASC'
    params = [start_date, end_date]
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    cols = [d[0] for d in cursor.description] #cursor.description provides column names
    return [dict(zip(cols, row)) for row in rows] #converting each row to a dictionary

@mcp.tool()
def summarize(start_date, end_date, category=None):
    """Summarizes expenses in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = 'SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?'
    params = [start_date, end_date]
    if category:
        query += ' AND category = ?'
        params.append(category)
    query += ' GROUP BY category ORDER BY category ASC'
    cursor.execute(query, params)
    cols = [d[0] for d in cursor.description] #cursor.description provides column names
    return [dict(zip(cols, row)) for row in cursor.fetchall()] #converting each row to a dictionary

@mcp.resource("expense://categories",mime_type="application/json")
def categories():
    with open(CATEGORIES_PATH, 'r', encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    #mcp.run(transport="sse") --> standard protocol
    mcp.run(transport="http", host="0.0.0.0", port=8000)