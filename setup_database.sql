-- Run these SQL commands in Railway MySQL Console to set up your database

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

-- Create teacher table
CREATE TABLE IF NOT EXISTS teacher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    subject VARCHAR(50),
    standard VARCHAR(20),
    division VARCHAR(10)
);

-- Create admin table
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    standard VARCHAR(20) NOT NULL,
    division VARCHAR(10) NOT NULL,
    UNIQUE KEY unique_student (standard, division, roll)
);

-- Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    standard VARCHAR(20) NOT NULL,
    division VARCHAR(10) NOT NULL,
    UNIQUE KEY unique_attendance (student_id, date),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- Insert default admin (plain text password - works with the login code)
INSERT INTO admin (username, password) 
VALUES ('admin', 'admin123');
