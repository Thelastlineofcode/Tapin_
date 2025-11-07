"""
Database migration script to add category and image_url columns to listing table
"""
import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), 'data.db')

def migrate_database():
    print("🔄 Starting database migration...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(listing)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add category column if it doesn't exist
        if 'category' not in columns:
            print("➕ Adding 'category' column to listing table...")
            cursor.execute("ALTER TABLE listing ADD COLUMN category VARCHAR(100)")
            print("✓ Added 'category' column")
        else:
            print("ℹ️  'category' column already exists")
        
        # Add image_url column if it doesn't exist
        if 'image_url' not in columns:
            print("➕ Adding 'image_url' column to listing table...")
            cursor.execute("ALTER TABLE listing ADD COLUMN image_url VARCHAR(500)")
            print("✓ Added 'image_url' column")
        else:
            print("ℹ️  'image_url' column already exists")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
