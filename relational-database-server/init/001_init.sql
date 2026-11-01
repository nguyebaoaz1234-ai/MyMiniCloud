-- 1. Database cơ bản (minicloud)
CREATE DATABASE IF NOT EXISTS minicloud;
USE minicloud;
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO notes (title) VALUES ('Hello from MariaDB!');

-- 2. Database mở rộng (studentdb)
CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10) NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    major VARCHAR(50) NOT NULL
);

INSERT INTO students (student_id, fullname, dob, major) VALUES
('52400003', 'Dao Nguyen Bao', '2006-05-15', 'Software Engineering'),
('52400039', 'Nguyen Minh Quan', '2006-08-20', 'Information Systems'),
('52400033', 'Tran Hoang Nam', '2006-11-02', 'Computer Science'),
('52400327', 'Le Thanh Dat', '2006-03-10', 'Cybersecurity');