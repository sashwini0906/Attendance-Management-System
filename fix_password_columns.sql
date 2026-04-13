<<<<<<< HEAD
-- Fix password column size to accommodate hashed passwords
ALTER TABLE admin MODIFY password VARCHAR(255);
ALTER TABLE teacher MODIFY password VARCHAR(255);

-- Verify the changes
SHOW COLUMNS FROM admin LIKE 'password';
SHOW COLUMNS FROM teacher LIKE 'password';
=======
-- Fix password column size to accommodate hashed passwords
ALTER TABLE admin MODIFY password VARCHAR(255);
ALTER TABLE teacher MODIFY password VARCHAR(255);

-- Verify the changes
SHOW COLUMNS FROM admin LIKE 'password';
SHOW COLUMNS FROM teacher LIKE 'password';
>>>>>>> a741fce4340050b093253c89486b1f4e20183baf
