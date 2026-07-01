from app import app
from models import db, SiteSettings, BeforeAfter, Promotion
import sqlite3
import os

def migrate_database():
    with app.app_context():
        # Get database path from app config
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = db_uri.replace('sqlite:///', '')
        
        # Make the path absolute
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.path.dirname(__file__), db_path)
        
        print(f"Database path: {db_path}")
        
        # Connect to SQLite database directly
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if site_settings table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='site_settings'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Check current schema
                cursor.execute("PRAGMA table_info(site_settings)")
                columns = [row[1] for row in cursor.fetchall()]
                print(f"Current columns: {columns}")
                
                # Check if phone column exists
                if 'phone' not in columns:
                    # Drop the old table
                    cursor.execute("DROP TABLE site_settings")
                    print("Dropped old site_settings table")
                else:
                    print("Table already has required columns, skipping migration")
            
            # Create the table with all columns if it doesn't exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='site_settings'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE site_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        site_name VARCHAR(100) NOT NULL,
                        logo_url VARCHAR(200) NOT NULL,
                        phone VARCHAR(20),
                        email VARCHAR(100),
                        address TEXT,
                        whatsapp_number VARCHAR(20),
                        business_hours VARCHAR(100),
                        facebook_url VARCHAR(200),
                        instagram_url VARCHAR(200),
                        twitter_url VARCHAR(200),
                        pinterest_url VARCHAR(200),
                        updated_at DATETIME
                    )
                """)
                print("Created site_settings table with all columns")
                
                # Insert default data
                cursor.execute("""
                    INSERT INTO site_settings 
                    (site_name, logo_url, phone, email, address, whatsapp_number, business_hours, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    'ASHA Beauty Salon',
                    'https://via.placeholder.com/150x50?text=ASHA',
                    '+91 98765 43210',
                    'info@ashabeautysalon.com',
                    '123 Beauty Street, Fashion District',
                    '919876543210',
                    'Mon-Sat: 9AM - 8PM'
                ))
                print("Inserted default site settings")
            
            # Create before_after table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='before_after'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE before_after (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(100) NOT NULL,
                        before_image VARCHAR(200) NOT NULL,
                        after_image VARCHAR(200) NOT NULL,
                        service_type VARCHAR(50) NOT NULL,
                        description TEXT,
                        featured BOOLEAN DEFAULT 0,
                        created_at DATETIME
                    )
                """)
                print("Created before_after table")
            
            # Create promotion table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promotion'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE promotion (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(100) NOT NULL,
                        description TEXT NOT NULL,
                        image_url VARCHAR(200),
                        discount_percentage INTEGER,
                        valid_from DATE,
                        valid_until DATE,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME
                    )
                """)
                print("Created promotion table")
            
            conn.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_database()
