"""
Debug script to check admin credentials in database
Run: python debug_login.py
"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

print("=== Database Connection Test ===")
print(f"DB_HOST: {os.environ.get('DB_HOST', 'localhost')}")
print(f"DB_USER: {os.environ.get('DB_USER', 'root')}")
print(f"DB_NAME: {os.environ.get('DB_NAME', 'attendance_db')}")
print()

try:
    db = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "attendance_db")
    )
    cursor = db.cursor(dictionary=True)
    print("✓ Database connected successfully!")
    print()
    
    # Check admin table
    print("=== Admin Table Contents ===")
    cursor.execute("SELECT id, username, password FROM admin")
    admins = cursor.fetchall()
    
    if not admins:
        print("✗ No admin users found!")
    else:
        for admin in admins:
            print(f"ID: {admin['id']}")
            print(f"Username: {admin['username']}")
            print(f"Password: {admin['password']}")
            print(f"Password length: {len(admin['password']) if admin['password'] else 0}")
            print()
    
    # Check teacher table
    print("=== Teacher Table Contents ===")
    cursor.execute("SELECT id, username, password FROM teacher")
    teachers = cursor.fetchall()
    
    if not teachers:
        print("✗ No teachers found!")
    else:
        for teacher in teachers:
            print(f"ID: {teacher['id']}")
            print(f"Username: {teacher['username']}")
            print(f"Password: {teacher['password']}")
            print(f"Password length: {len(teacher['password']) if teacher['password'] else 0}")
            print()
    
    # Test password verification
    print("=== Password Verification Test ===")
    test_password = "admin123"
    
    from werkzeug.security import check_password_hash
    
    for admin in admins:
        stored_pw = admin['password']
        
        # Try hash verification
        try:
            hash_result = check_password_hash(stored_pw, test_password)
            print(f"Hash verification for '{admin['username']}': {hash_result}")
        except Exception as e:
            print(f"Hash verification error: {e}")
        
        # Try plain text comparison
        if stored_pw == test_password:
            print(f"Plain text match: True")
        else:
            print(f"Plain text match: False")
    
    db.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
