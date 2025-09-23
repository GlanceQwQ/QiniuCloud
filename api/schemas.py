from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# 用户相关模式
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: UserResponse

# 角色相关模式
class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    system_prompt: str = Field(..., min_length=10, max_length=2000)
    greeting: str = Field(..., min_length=5, max_length=500)
    avatar_url: Optional[str] = None
    is_public: bool = True

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    system_prompt: Optional[str] = Field(None, min_length=10, max_length=2000)
    greeting: Optional[str] = Field(None, min_length=5, max_length=500)
    avatar_url: Optional[str] = None
    is_public: Optional[bool] = None

class CharacterResponse(CharacterBase):
    id: str
    creator_id: str
    chat_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    
    class Config:
        from_attributes = True

class CharacterListResponse(BaseModel):
    characters: List[CharacterResponse]
    total: int
    page: int
    limit: int

# 会话相关模式
class ConversationBase(BaseModel):
    character_id: str
    session_prompt: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(BaseModel):
    id: str
    user_id: Optional[str]
    character_id: str
    summary: Optional[str]
    session_prompt: Optional[str]
    last_message_at: datetime
    created_at: datetime
    character: CharacterResponse
    
    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    limit: int

# 消息相关模式
class MessageBase(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=4000)

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    stream: Optional[bool] = False

class ConversationMessageCreate(BaseModel):
    character_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    session_prompt: Optional[str] = None

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    limit: int

# 聊天响应模式
class ChatResponse(BaseModel):
    type: str  # "token" | "complete"
    content: str
    conversation_id: str
    message_id: Optional[str] = None

# 通用响应模式
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None