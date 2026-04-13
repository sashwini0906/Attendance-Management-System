"""
Run this script to reset the admin password to 'admin123'
Usage: python reset_admin.py
"""
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

# Connect to database
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", ""),
    database=os.environ.get("DB_NAME", "attendance_db")
)
cursor = db.cursor()

# Generate hashed password
hashed_pw = generate_password_hash("admin123")

# Update admin password
cursor.execute("UPDATE admin SET password = %s WHERE username = 'admin'", (hashed_pw,))
db.commit()

print(f"Admin password reset successfully!")
print(f"Username: admin")
print(f"Password: admin123")
print(f"Hash stored: {hashed_pw[:50]}...")
