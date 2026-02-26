-- ================================================================
-- VisionAssist — Database Setup Script
-- Tanggung jawab: Backend & Database Developer
--
-- Cara pakai:
--   mysql -u root -p < database/setup.sql
-- ================================================================

CREATE DATABASE IF NOT EXISTS visionassist_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE visionassist_db;

CREATE TABLE IF NOT EXISTS tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(255)    NOT NULL,
    description TEXT,
    deadline    DATE,
    priority    ENUM('low', 'medium', 'high') DEFAULT 'medium',
    status      ENUM('pending', 'in_progress', 'done') DEFAULT 'pending',
    category    VARCHAR(100),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Contoh data awal (hapus jika tidak perlu)
INSERT INTO tasks (title, description, deadline, priority, category) VALUES
('Tugas Algoritma Bab 5',    'Implementasi Binary Search Tree',   '2025-03-10', 'high',   'Kuliah'),
('Laporan Praktikum Jarkom',  'Topologi jaringan dan subnetting',  '2025-03-15', 'medium', 'Kuliah'),
('Proposal Skripsi',          'Draft bab 1 dan 2',                '2025-04-01', 'high',   'Skripsi'),
('Latihan Soal UTS',          'Soal latihan hal. 50-80',          '2025-03-20', 'low',    'Kuliah');

SELECT CONCAT('✅ Setup selesai! Tabel tasks berisi ', COUNT(*), ' data.') AS status
FROM tasks;
