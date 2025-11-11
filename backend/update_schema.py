"""Update the password_hash column to be larger"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db

with app.app_context():
    print("Updating password_hash column to VARCHAR(256)...")
    try:
        # Using raw SQL to alter the column
        db.session.execute(db.text("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(256)"))
        db.session.commit()
        print("✓ Column updated successfully!")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
