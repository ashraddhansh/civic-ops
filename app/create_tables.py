from app.database import Base, engine
import app.models  # ensures models are registered with Base

def drop_tables():
    """Drop all tables - use with caution!"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped successfully")

def create_tables():
    """Create all tables based on models"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

def recreate_tables():
    """Drop and recreate all tables - use for schema changes"""
    print("Recreating tables...")
    drop_tables()
    create_tables()
    print("Tables recreated successfully")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "drop":
            drop_tables()
        elif command == "recreate":
            recreate_tables()
        elif command == "create":
            create_tables()
        else:
            print("Usage: python create_tables.py [create|drop|recreate]")
    else:
        create_tables()
