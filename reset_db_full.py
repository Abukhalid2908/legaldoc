
import pymysql
from database import engine, SessionLocal
from models import Base, User
from passlib.context import CryptContext

# Auth Config
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def reset_database():
    print("Resetting database...")
    
    # 1. Drop Database if exists
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            cursor.execute("DROP DATABASE IF EXISTS db_perjanjian")
            cursor.execute("CREATE DATABASE db_perjanjian")
        connection.close()
        print("Database 'db_perjanjian' recreated.")
    except Exception as e:
        print(f"Error recreating database: {e}")
        return

    # 2. Create Tables
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return
        
    # 3. Create Default Admin
    db = SessionLocal()
    try:
        admin_user = User(
            username="admin", 
            password_hash=pwd_context.hash("admin123"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("Default admin created: admin / admin123")
    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
