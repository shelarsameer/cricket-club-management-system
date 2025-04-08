from app import db, app

def init_db():
    with app.app_context():
        # Drop all tables first
        db.drop_all()
        print("Dropped all existing tables")
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 