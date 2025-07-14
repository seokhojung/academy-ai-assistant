-- Academy AI Assistant Database Initialization
-- This script will be executed when the PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create additional indexes for better performance
CREATE INDEX IF NOT EXISTS idx_student_email ON student(email);
CREATE INDEX IF NOT EXISTS idx_teacher_email ON teacher(email);
CREATE INDEX IF NOT EXISTS idx_material_title ON material(title);
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);

-- Insert sample data (optional)
INSERT INTO student (name, email, phone, grade, parent_name, parent_phone, address, enrollment_date, status)
VALUES 
    ('김철수', 'kim@example.com', '010-1234-5678', '고등학교 1학년', '김부모', '010-8765-4321', '서울시 강남구', '2024-01-15', 'active'),
    ('이영희', 'lee@example.com', '010-2345-6789', '고등학교 2학년', '이부모', '010-9876-5432', '서울시 서초구', '2024-01-20', 'active'),
    ('박민수', 'park@example.com', '010-3456-7890', '고등학교 3학년', '박부모', '010-0987-6543', '서울시 마포구', '2024-02-01', 'active')
ON CONFLICT (email) DO NOTHING;

INSERT INTO teacher (name, email, phone, subject, hire_date, status)
VALUES 
    ('김선생', 'teacher.kim@example.com', '010-1111-2222', '수학', '2024-01-01', 'active'),
    ('이선생', 'teacher.lee@example.com', '010-3333-4444', '영어', '2024-01-01', 'active'),
    ('박선생', 'teacher.park@example.com', '010-5555-6666', '과학', '2024-01-01', 'active')
ON CONFLICT (email) DO NOTHING;

INSERT INTO material (title, description, subject, grade_level, file_path, upload_date, status)
VALUES 
    ('수학 기초 문제집', '고등학교 1학년 수학 기초 문제집', '수학', '고등학교 1학년', '/materials/math_basic.pdf', '2024-01-15', 'active'),
    ('영어 문법 교재', '고등학교 2학년 영어 문법 교재', '영어', '고등학교 2학년', '/materials/english_grammar.pdf', '2024-01-20', 'active'),
    ('과학 실험 가이드', '고등학교 3학년 과학 실험 가이드', '과학', '고등학교 3학년', '/materials/science_lab.pdf', '2024-02-01', 'active')
ON CONFLICT (title) DO NOTHING; 