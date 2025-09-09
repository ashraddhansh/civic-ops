from database import Base, engine
import models  # ensures models are registered with Base

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

if __name__ == "__main__":
    create_tables()
