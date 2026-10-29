import sqlite3
import os
from typing import List, Dict, Any


class SQLTool:
    """Tool for executing read-only SQL queries against the Olist SQLite DB."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'olist.db')
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def execute_sql_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a single SELECT query and return rows as list of dicts.
        For safety, only a single SELECT statement is permitted.
        """
        stripped = query.strip().lower()
        if not stripped.startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")
        if ";" in stripped.rstrip(";"):
            raise ValueError("Multiple statements are not allowed.")
        cur = self.conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def list_tables(self) -> List[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row["name"] for row in cur.fetchall()]


# Optional pandas summary tool (reads CSV without modification)
def pandas_summary(csv_path: str) -> Dict[str, Any]:
    import pandas as pd
    df = pd.read_csv(csv_path)
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": df.isnull().sum().to_dict(),
    }
