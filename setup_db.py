from app import create_app, db
import models
import users

# Create the app
app = create_app()

# Create all tables
with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Database created successfully!")
    
    # Test the schema
    from models import Trip
    from users import User
    
    print("\nTesting Trip table schema...")
    trip_columns = Trip.__table__.columns.keys()
    print(f"Trip columns: {trip_columns}")
    
    print("\nTesting User table schema...")
    user_columns = User.__table__.columns.keys()
    print(f"User columns: {user_columns}")
    
    if 'user_id' in trip_columns:
        print("✓ user_id column exists in Trip table")
    else:
        print("✗ user_id column missing in Trip table")
        
    print("Database setup complete!")
