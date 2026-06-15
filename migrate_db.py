"""
One-time migration script: adds the new columns required for the
AI-Powered Recommendation & Verification features to an existing
scholarship.db SQLite database.

Run this ONCE after pulling the updated code, if you have an existing
scholarship.db with the old schema:

    python migrate_db.py

If your scholarship.db is brand new (or you delete it), db.create_all()
in app.py will already create the correct schema and this script is not
needed.
"""
import sqlite3

DB_PATH = "scholarship.db"

NEW_COLUMNS = [
    ("gender", "VARCHAR(20)"),
    ("recommended_scholarship", "VARCHAR(120)"),
    ("recommendation_score", "FLOAT"),
    ("eligibility_score", "FLOAT"),
    ("explanation", "TEXT"),
]


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for col_name, col_type in NEW_COLUMNS:
        if not column_exists(cursor, "application", col_name):
            print(f"Adding column '{col_name}' ({col_type}) to 'application' table...")
            cursor.execute(f"ALTER TABLE application ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column '{col_name}' already exists, skipping.")

    conn.commit()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()