-- Lược đồ cho bài 06. Chạy lại được nhiều lần: xoá bảng cũ rồi tạo lại.
-- Các ràng buộc mà bài 02 phải tự kiểm tra bằng Python, ở đây do MySQL đảm bảo.

DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;

CREATE TABLE classes (
    id          INT UNSIGNED PRIMARY KEY,
    class_name  VARCHAR(50)  NOT NULL,
    CONSTRAINT class_name_not_blank CHECK (TRIM(class_name) <> '')
);

CREATE TABLE students (
    id        INT UNSIGNED PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    birthday  DATE         NOT NULL,
    phone     CHAR(10)     NOT NULL,
    class_id  INT UNSIGNED NOT NULL,
    CONSTRAINT student_phone_format CHECK (phone REGEXP '^0[0-9]{9}$'),
    -- RESTRICT: không xoá được lớp còn sinh viên
    CONSTRAINT student_class FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE RESTRICT,
    INDEX student_by_class (class_id)
);

CREATE TABLE teachers (
    id             INT UNSIGNED PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    birthday       DATE         NOT NULL,
    phone          CHAR(10)     NOT NULL,
    head_of_class  INT UNSIGNED NULL,
    CONSTRAINT teacher_phone_format CHECK (phone REGEXP '^0[0-9]{9}$'),
    CONSTRAINT teacher_class FOREIGN KEY (head_of_class) REFERENCES classes (id) ON DELETE RESTRICT,
    -- Mỗi lớp tối đa một chủ nhiệm. UNIQUE cho phép nhiều giá trị NULL (giáo viên không chủ nhiệm lớp nào).
    CONSTRAINT one_head_per_class UNIQUE (head_of_class)
);
