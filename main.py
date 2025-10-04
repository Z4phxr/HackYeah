from app import create_app, db
import os

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Import models here to ensure tables are created
        import models
        import users
        import friends
        
        # Force remove existing database if it exists
        db_path = 'travel_tracker.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        
        # Create all tables fresh
        db.create_all()
        print("Database tables created successfully!")
        
        # Verify the schema
        from models import Trip
        print(f"Trip table columns: {list(Trip.__table__.columns.keys())}")
        
    app.run(debug=True)
