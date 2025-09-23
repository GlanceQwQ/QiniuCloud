#!/usr/bin/env python3
"""
数据库迁移脚本
"""

import sys
import os
from sqlalchemy import create_engine, text
from config import settings

def run_migration(sql_file_path):
    """执行SQL迁移文件"""
    # 检查文件是否存在
    if not os.path.exists(sql_file_path):
        print(f"错误: 迁移文件不存在: {sql_file_path}")
        return False
    
    # 创建数据库连接
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
    
    try:
        # 读取SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL语句
        with engine.connect() as conn:
            # 分割SQL语句（以分号分隔）
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    print(f"执行SQL: {statement[:100]}...")
                    conn.execute(text(statement))
            
            conn.commit()
        
        print(f"迁移成功: {sql_file_path}")
        return True
        
    except Exception as e:
        print(f"迁移失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python run_migration.py <sql_file_path>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    success = run_migration(sql_file)
    sys.exit(0 if success else 1)