from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings
import logging

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite特定配置
    echo=settings.debug  # 开发环境下打印SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库配置
def init_database():
    """初始化数据库配置"""
    # 启用WAL模式以提高并发性能
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.execute(text("PRAGMA synchronous=NORMAL;"))
        conn.execute(text("PRAGMA cache_size=10000;"))
        conn.execute(text("PRAGMA temp_store=MEMORY;"))
        conn.commit()
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 初始化示例数据
    from init_data import init_sample_characters
    init_sample_characters()
    
    print("数据库初始化完成")

# 创建所有表
def create_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    init_database()