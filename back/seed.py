from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app import models, auth

def seed_users():
    db = SessionLocal()
    try:
        # Check if users exist
        admin = db.query(models.User).filter(models.User.email == "admin@designer-panel.com").first()
        if not admin:
            admin_user = models.User(
                username="admin",
                email="admin@designer-panel.com",
                hashed_password=auth.get_password_hash("des!gnPanel321"),
                role=models.Role.Admin
            )
            db.add(admin_user)
            
        user = db.query(models.User).filter(models.User.email == "user@designer-panel.com").first()
        if not user:
            standard_user = models.User(
                username="user",
                email="user@designer-panel.com",
                hashed_password=auth.get_password_hash("user123"),
                role=models.Role.User
            )
            db.add(standard_user)
            
        db.commit()
        print("Database seeded with default users successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
