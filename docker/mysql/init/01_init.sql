-- 智能学习系统数据库初始化脚本
-- 创建时间: 2024

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 使用数据库
USE smart_learning;

-- 用户表
CREATE TABLE IF NOT EXISTS t_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码(BCrypt加密)',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    avatar VARCHAR(255) COMMENT '头像URL',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色: user/admin',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/disabled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 坐姿检测记录表
CREATE TABLE IF NOT EXISTS t_posture_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    status VARCHAR(20) NOT NULL COMMENT '检测状态: good/bad/unknown',
    gesture_type VARCHAR(100) COMMENT '姿态类型',
    message VARCHAR(500) COMMENT '检测信息',
    confidence DECIMAL(5,4) COMMENT '置信度',
    key_points JSON COMMENT '关键点数据',
    image_path VARCHAR(255) COMMENT '图片路径',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES t_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='坐姿检测记录表';

-- 题目记录表
CREATE TABLE IF NOT EXISTS t_question_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    question_text TEXT COMMENT '题目内容',
    answer TEXT COMMENT '答案',
    steps JSON COMMENT '解题步骤',
    knowledge_points JSON COMMENT '知识点',
    subject VARCHAR(50) COMMENT '学科',
    success BOOLEAN DEFAULT FALSE COMMENT '是否成功解答',
    provider VARCHAR(50) COMMENT 'AI提供商',
    error_message VARCHAR(500) COMMENT '错误信息',
    image_path VARCHAR(255) COMMENT '图片路径',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_subject (subject),
    INDEX idx_success (success),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES t_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目记录表';

-- 学习计划表
CREATE TABLE IF NOT EXISTS t_study_plan (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    goal VARCHAR(500) COMMENT '学习目标',
    weak_points JSON COMMENT '薄弱知识点',
    strong_points JSON COMMENT '擅长知识点',
    available_hours INT DEFAULT 2 COMMENT '每日可用时间(小时)',
    plan_data JSON COMMENT '计划数据',
    timeline VARCHAR(50) COMMENT '时间线',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/completed/archived',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES t_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习计划表';

-- AI对话记录表
CREATE TABLE IF NOT EXISTS t_chat_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    subject VARCHAR(50) COMMENT '学科',
    question TEXT NOT NULL COMMENT '用户问题',
    answer TEXT COMMENT 'AI回答',
    hints JSON COMMENT '提示',
    knowledge JSON COMMENT '相关知识点',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_subject (subject),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES t_user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI对话记录表';

-- 知识库表
CREATE TABLE IF NOT EXISTS t_knowledge (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '标题',
    content TEXT NOT NULL COMMENT '内容',
    subject VARCHAR(50) COMMENT '学科',
    tags JSON COMMENT '标签',
    embedding VECTOR(1536) COMMENT '向量嵌入(如果支持)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_subject (subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表';

-- 插入默认管理员账户 (密码: admin123，使用BCrypt加密)
-- 注意: 实际部署时请修改密码
-- INSERT INTO t_user (username, password, email, role, status) VALUES
-- ('admin', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYqVqxqZ', 'admin@smartlearning.com', 'admin', 'active');

SELECT 'Database initialized successfully!' AS message;
