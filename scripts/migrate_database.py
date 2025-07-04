#!/usr/bin/env python3
"""
Database migration script to add the transcript column to existing databases.
"""
import sqlite3
import sys
from src.config import settings

def migrate_database():
    """Add transcript column to existing database."""
    db_path = settings.database_url.replace('sqlite:///', '')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if transcript column already exists
        cursor.execute("PRAGMA table_info(processed_videos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'transcript' not in columns:
            print("🔧 Adding transcript column to database...")
            cursor.execute("ALTER TABLE processed_videos ADD COLUMN transcript TEXT")
            conn.commit()
            print("✅ Database migration completed successfully!")
        else:
            print("ℹ️  Database already has transcript column, no migration needed.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()