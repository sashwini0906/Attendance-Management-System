-- Run this to add the subject column to your existing teacher table
USE attendance_db;
ALTER TABLE teacher ADD COLUMN subject VARCHAR(50) AFTER full_name;
