from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

def generate_id():
    """生成唯一ID"""
    return str(uuid.uuid4()).replace('-', '')[:16]

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(16), primary_key=True, default=generate_id)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # user, admin, super_admin
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    characters = relationship("Character", back_populates="creator")
    conversations = relationship("Conversation", back_populates="user")

class Character(Base):
    """角色表"""
    __tablename__ = "characters"
    
    id = Column(String(16), primary_key=True, default=generate_id)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    greeting = Column(Text, nullable=False)
    avatar_url = Column(String(500))
    creator_id = Column(String(16), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True, index=True)
    chat_count = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    creator = relationship("User", back_populates="characters")
    conversations = relationship("Conversation", back_populates="character")

class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"
    
    id = Column(String(16), primary_key=True, default=generate_id)
    user_id = Column(String(16), ForeignKey("users.id"), nullable=True, index=True)
    character_id = Column(String(16), ForeignKey("characters.id"), nullable=False, index=True)
    summary = Column(Text)
    session_prompt = Column(Text)
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="conversations")
    character = relationship("Character", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(String(16), primary_key=True, default=generate_id)
    conversation_id = Column(String(16), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 添加角色检查约束
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_message_role"),
    )
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")