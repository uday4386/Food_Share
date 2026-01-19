from app import app, db, User, Donation, FoodRequest
from sqlalchemy import text

def reset_database():
    with app.app_context():
        try:
            # Delete all rows from tables
            num_donations = db.session.query(Donation).delete()
            num_requests = db.session.query(FoodRequest).delete()
            num_users = db.session.query(User).delete()
            
            # Commit changes
            db.session.commit()
            
            print(f"Database cleared successfully.")
            print(f"Deleted {num_donations} donations.")
            print(f"Deleted {num_requests} requests.")
            print(f"Deleted {num_users} users.")
            
            # Re-create admin user
            # We deleted all users, so we should restore the default admin for convenience
            # or just leave it empty if strictly requested. 
            # The prompt asked to "clear the database content".
            # Usually users want to be able to login as admin after valid reset.
            # I'll check if I should recreate admin. The app.py creates admin on startup if missing!
            # So simply clearing is fine, next app run will recreate admin.
            
        except Exception as e:
            db.session.rollback()
            print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
