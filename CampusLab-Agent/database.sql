-- PostgreSQL Database Schema for CampusLab Agent

-- Drop existing tables if they exist
DROP TABLE IF EXISTS fault_reports CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS systems CASCADE;
DROP TABLE IF EXISTS labs CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'faculty', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Labs Table
CREATE TABLE labs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    description TEXT
);

-- Create Systems Table
CREATE TABLE systems (
    id SERIAL PRIMARY KEY,
    lab_id INTEGER REFERENCES labs(id) ON DELETE CASCADE,
    system_number INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'reserved', 'faulty')),
    CONSTRAINT unique_lab_system_number UNIQUE (lab_id, system_number)
);

-- Create Bookings Table
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    system_id INTEGER REFERENCES systems(id) ON DELETE CASCADE,
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_booking_times CHECK (start_time < end_time)
);

-- Create Fault Reports Table
CREATE TABLE fault_reports (
    id SERIAL PRIMARY KEY,
    system_id INTEGER REFERENCES systems(id) ON DELETE SET NULL,
    reported_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    issue_type VARCHAR(50) NOT NULL CHECK (issue_type IN ('keyboard', 'mouse', 'monitor', 'network', 'power', 'other')),
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'repaired')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for performance optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_bookings_date_time ON bookings(booking_date, start_time, end_time);
CREATE INDEX idx_systems_lab_status ON systems(lab_id, status);
CREATE INDEX idx_fault_reports_status ON fault_reports(status);

-- Seed Initial Data
INSERT INTO users (name, email, password_hash, role) VALUES
('Admin User', 'admin@campus.edu', 'pbkdf2:sha256:260000$w5Q9Z...$adminpasswordhash', 'admin'),
('Dr. Alan Turing', 'alan@campus.edu', 'pbkdf2:sha256:260000$w5Q9Z...$facultypasswordhash', 'faculty'),
('John Doe', 'john@campus.edu', 'pbkdf2:sha256:260000$w5Q9Z...$studentpasswordhash', 'student');

INSERT INTO labs (name, capacity, open_time, close_time, description) VALUES
('Lab A - AI & Data Science', 20, '08:00:00', '20:00:00', 'High performance GPU workstations for AI and ML training.'),
('Lab B - Software Engineering', 25, '08:00:00', '22:00:00', 'General computer science lab with full dev stack tools.'),
('Lab C - Hardware & Networking', 15, '09:00:00', '18:00:00', 'Cisco networking racks and hardware troubleshooting kits.');

-- Seed Systems for Lab A (20 systems)
INSERT INTO systems (lab_id, system_number, status)
SELECT 1, generate_series(1, 20), 'available';

-- Seed Systems for Lab B (25 systems)
INSERT INTO systems (lab_id, system_number, status)
SELECT 2, generate_series(1, 25), 'available';

-- Seed Systems for Lab C (15 systems)
INSERT INTO systems (lab_id, system_number, status)
SELECT 3, generate_series(1, 15), 'available';
