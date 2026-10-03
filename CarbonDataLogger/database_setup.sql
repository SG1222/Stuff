-- ============================================================
-- Carbon Data Logger - Database Setup Script
-- Creates the database, both tables and the default categories.
-- Run ONCE in the MySQL client:   SOURCE database_setup.sql;
-- (carbon_logger.py also creates these automatically if missing.)
-- ============================================================

CREATE DATABASE IF NOT EXISTS carbon_logger;
USE carbon_logger;

-- Table 1: activity categories with their unit and emission factor
CREATE TABLE IF NOT EXISTS categories (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    category_name   VARCHAR(30) NOT NULL UNIQUE,
    unit            VARCHAR(10) NOT NULL,
    emission_factor DECIMAL(10,3) NOT NULL
);

-- Table 2: one row for every activity recorded by the user
CREATE TABLE IF NOT EXISTS emission_records (
    record_id    INT AUTO_INCREMENT PRIMARY KEY,
    record_date  DATE NOT NULL,
    category_id  INT NOT NULL,
    quantity     DECIMAL(10,2) NOT NULL,
    co2_emission DECIMAL(10,2) NOT NULL,
    note         VARCHAR(100),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Default categories.
-- NOTE: emission factors (kg CO2 per unit) are ILLUSTRATIVE project
-- values for learning purposes only. They can be changed from menu 12.
INSERT INTO categories (category_name, unit, emission_factor) VALUES
    ('Electricity',  'kWh', 0.820),
    ('Car Travel',   'km',  0.170),
    ('Bus Travel',   'km',  0.100),
    ('Train Travel', 'km',  0.040),
    ('LPG',          'kg',  2.980),
    ('Flight',       'km',  0.150);

-- Some sample records for testing (optional)
INSERT INTO emission_records (record_date, category_id, quantity, co2_emission, note) VALUES
    ('2026-08-02', 1, 12.50, 10.25, 'Daily home use'),
    ('2026-08-03', 2, 20.00,  3.40, 'Trip to market'),
    ('2026-08-05', 3, 15.00,  1.50, 'School bus'),
    ('2026-09-01', 5,  2.00,  5.96, 'Cooking gas'),
    ('2026-09-10', 6, 800.00, 120.00, 'Flight to Mumbai');

-- Useful queries for checking the data
SELECT * FROM categories;

SELECT r.record_id, r.record_date, c.category_name, r.quantity, c.unit, r.co2_emission
FROM emission_records r INNER JOIN categories c ON r.category_id = c.category_id
ORDER BY r.record_date;

SELECT c.category_name, COUNT(*), SUM(r.co2_emission)
FROM emission_records r INNER JOIN categories c ON r.category_id = c.category_id
GROUP BY c.category_name;
