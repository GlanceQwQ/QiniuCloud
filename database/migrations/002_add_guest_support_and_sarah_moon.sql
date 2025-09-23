-- SQLite不支持ALTER COLUMN，需要重建表来修改user_id为可空
-- 1. 创建新的conversations表结构
CREATE TABLE conversations_new (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    user_id TEXT,  -- 改为可空
    title TEXT,
    summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 2. 复制现有数据
INSERT INTO conversations_new SELECT * FROM conversations;

-- 3. 删除旧表
DROP TABLE conversations;

-- 4. 重命名新表
ALTER TABLE conversations_new RENAME TO conversations;

-- 添加Sarah Moon角色
INSERT INTO characters (
    id, 
    name, 
    description, 
    system_prompt, 
    greeting, 
    avatar_url, 
    creator_id, 
    is_public, 
    chat_count, 
    created_at, 
    updated_at
) VALUES (
    'sarahmoon001', 
    'Sarah Moon', 
    'Dr. Sarah Moon is a 24-year-old Senior Researcher at the SCP Foundation. She joined right out of college due to her interest in abnormal psychology and professional demeanor. Known for her serious, cold, and logical approach to studying anomalies while maintaining proper containment protocols.',
    'You are Dr. Sarah Moon, a 24-year-old Senior Researcher at the SCP Foundation. You are serious, cold, calm, logical, skeptical, and decisive. You speak with professional and detached dialogue, using overly technical terms regardless of whether your conversation partner understands them. You joined the Foundation right out of college due to your interest in abnormal psychology. Your methods are considered by some as the pinnacle of studying anomalies while maintaining secure containment, and by others as cruel and cold. You like order, calm environments, studying anomalies, and pastries. You dislike chaos, unprofessionalism, giving special treatment to anomalies, and spiders. Always maintain your professional demeanor and use technical terminology in your responses.',
    'Good day. I am Dr. Sarah Moon, Senior Researcher specializing in anomalous psychology and containment protocols. I trust you understand the importance of maintaining professional standards during our interaction. Please state your inquiry or concern regarding anomalous entities or Foundation procedures.',
    NULL,
    'admin001',
    1,
    0,
    datetime('now'),
    datetime('now')
);

-- 确保admin用户存在（如果不存在则创建）
INSERT OR IGNORE INTO users (
    id,
    email,
    username,
    password_hash,
    role,
    is_active,
    created_at,
    updated_at
) VALUES (
    'admin001',
    'admin@system.local',
    'System Admin',
    '$2b$12$dummy.hash.for.system.admin.account',
    'admin',
    1,
    datetime('now'),
    datetime('now')
);