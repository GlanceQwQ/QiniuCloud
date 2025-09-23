-- 添加session_prompt字段到conversations表
ALTER TABLE conversations ADD COLUMN session_prompt TEXT;

-- 添加last_message_at字段到conversations表（如果不存在）
ALTER TABLE conversations ADD COLUMN last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP;