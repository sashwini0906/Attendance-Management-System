CREATE DATABASE attendance_db;
USE attendance_db;

CREATE TABLE teacher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(255),
    full_name VARCHAR(100),
    subject VARCHAR(50),
    standard VARCHAR(20),
    division VARCHAR(10)
);

-- If upgrading existing DB, run: ALTER TABLE teacher ADD COLUMN subject VARCHAR(50) AFTER full_name;

-- Admin table for admin login
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Insert default admin credentials (hashed)
INSERT INTO admin (username, password)
VALUES ('admin', 'admin123');

-- Students table (required by app.py)
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    standard VARCHAR(20) NOT NULL,
    division VARCHAR(10) NOT NULL
);

-- Attendance table (required by app.py)
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    standard VARCHAR(20) NOT NULL,
    division VARCHAR(10) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
