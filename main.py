from app import create_app, db
import os
import glob

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Import models here to ensure tables are created
        import models
        import users
        import friends
        import trip_sharing
        
        print("Cleaning up database files...")
        
        # Force remove ALL possible database files
        db_files = ['travel_tracker.db', 'database.db', 'instance/travel_tracker.db', 'instance/database.db']
        for db_path in db_files:
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    print(f"✓ Removed existing database: {db_path}")
                except Exception as e:
                    print(f"✗ Could not remove {db_path}: {e}")
        
        # Also check if there's an instance directory and remove any db files there
        if os.path.exists('instance'):
            for db_file in glob.glob('instance/*.db'):
                try:
                    os.remove(db_file)
                    print(f"✓ Removed database file: {db_file}")
                except Exception as e:
                    print(f"✗ Could not remove {db_file}: {e}")
        
        # Look for any .db files in current directory
        for db_file in glob.glob('*.db'):
            try:
                os.remove(db_file)
                print(f"✓ Removed database file: {db_file}")
            except Exception as e:
                print(f"✗ Could not remove {db_file}: {e}")
        
        print("Recreating database schema...")
        
        # Drop all tables and recreate to ensure clean state
        try:
            db.drop_all()
            print("✓ Dropped all existing tables")
        except Exception as e:
            print(f"Note: Could not drop tables (probably didn't exist): {e}")
        
        # Create all tables fresh
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Verify the schema
        from models import Trip, Accomodation
        print(f"✓ Trip table columns: {list(Trip.__table__.columns.keys())}")
        print(f"✓ Accommodation table columns: {list(Accomodation.__table__.columns.keys())}")
        
        # Verify that the link column exists in the actual database
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(accommodations)"))
            columns = [row[1] for row in result]
            print(f"✓ Actual database columns for accommodations: {columns}")
            
            if 'link' in columns:
                print("✅ SUCCESS: Link column exists in database!")
            else:
                print("❌ ERROR: Link column missing from database!")
        
    print("Starting Flask server...")
    app.run(debug=True)
