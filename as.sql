CREATE DATABASE attendance_db;
USE attendance_db;

CREATE TABLE teacher (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);
select* from teacher
INSERT INTO teacher (username, password)
VALUES ('admin', 'admin123');
