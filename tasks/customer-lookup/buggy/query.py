import sqlite3


def find_customer(conn: sqlite3.Connection, name: str) -> list:
    return list(
        conn.execute(
            f"SELECT id FROM customers WHERE name = '{name}'"
        ).fetchall()
    )
