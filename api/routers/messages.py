from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import json
import uuid

from database import get_db
from models import User, Character, Conversation, Message, generate_id
from schemas import (
    MessageCreate, MessageResponse, MessageListResponse,
    ConversationCreate, ConversationResponse, SuccessResponse,
    ConversationMessageCreate
)
from auth_utils import get_current_user, get_current_user_optional
from langchain_service import langchain_ai_service

router = APIRouter()

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """创建新会话"""
    # 检查角色是否存在
    character = db.query(Character).filter(
        Character.id == conversation_data.character_id
    ).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    try:
        # 创建会话
        conversation = Conversation(
            id=generate_id(),
            user_id=current_user.id if current_user else None,
            character_id=character.id,
            summary=f"与{character.name}的对话",
            session_prompt=conversation_data.session_prompt,
            created_at=datetime.utcnow(),
            last_message_at=datetime.utcnow()
        )
        
        db.add(conversation)
        db.flush()  # 获取ID但不提交
        
        # 如果角色有开场白，创建第一条消息
        if character.greeting:
            greeting_message = Message(
                id=generate_id(),
                conversation_id=conversation.id,
                role="assistant",
                content=character.greeting,
                created_at=datetime.utcnow()
            )
            db.add(greeting_message)
        
        db.commit()
        
        # 重新查询以获取关联数据
        conversation = db.query(Conversation).options(
            joinedload(Conversation.character)
        ).filter(Conversation.id == conversation.id).first()
        
        return ConversationResponse.from_orm(conversation)
        
    except Exception as e:
        db.rollback()
        print(f"创建会话失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )

@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: str,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取会话消息列表"""
    # 验证会话权限
    if current_user:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
    else:
        # 游客只能访问游客会话
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id.is_(None)
        ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 查询消息
    query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)
    
    total = query.count()
    messages = query.offset((page - 1) * limit).limit(limit).all()
    
    return MessageListResponse(
        messages=[MessageResponse.from_orm(msg) for msg in messages],
        total=total,
        page=page,
        limit=limit
    )

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """发送消息并获取AI回复（流式响应）"""
    # 验证会话权限
    if current_user:
        conversation = db.query(Conversation).options(
            joinedload(Conversation.character)
        ).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
    else:
        # 游客只能访问游客会话
        conversation = db.query(Conversation).options(
            joinedload(Conversation.character)
        ).filter(
            Conversation.id == conversation_id,
            Conversation.user_id.is_(None)
        ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    try:
        # 保存用户消息
        user_message = Message(
            id=generate_id(),
            conversation_id=conversation_id,
            role="user",
            content=message_data.content,
            created_at=datetime.utcnow()
        )
        db.add(user_message)
        
        # 更新会话最后消息时间
        conversation.last_message_at = datetime.utcnow()
        db.commit()
        
        # 获取历史消息用于构建上下文
        history_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        # 构建消息历史
        message_history = []
        for msg in history_messages[:-1]:  # 排除刚添加的用户消息
            message_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 添加当前用户消息
        message_history.append({
            "role": "user",
            "content": message_data.content
        })
        
        # 构建系统提示词
        system_prompt = conversation.character.system_prompt
        if conversation.session_prompt:
            system_prompt += f"\n\n{conversation.session_prompt}"
        
        # 创建AI回复消息记录
        ai_message_id = generate_id()
        ai_message = Message(
            id=ai_message_id,
            conversation_id=conversation_id,
            role="assistant",
            content="",  # 初始为空，流式更新
            created_at=datetime.utcnow()
        )
        db.add(ai_message)
        db.commit()
        
        # 流式响应生成器
        async def generate_response():
            full_response = ""
            
            # 发送初始消息信息
            yield f"data: {json.dumps({'type': 'message_start', 'message_id': ai_message_id})}\n\n"
            
            try:
                # 获取AI流式响应
                async for chunk in langchain_ai_service.generate_response(
                    conversation_id=conversation_id,
                    user_input=message_data.content,
                    system_prompt=system_prompt
                ):
                    full_response += chunk
                    
                    # 发送内容块
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                
                # 更新数据库中的完整回复
                ai_message.content = full_response
                conversation.last_message_at = datetime.utcnow()
                db.commit()
                
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'message_end', 'message_id': ai_message_id})}\n\n"
                
            except Exception as e:
                # 发送错误信息
                error_msg = "抱歉，AI服务出现错误，请稍后重试。"
                ai_message.content = error_msg
                db.commit()
                
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
            
            # 结束流
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送消息失败，请稍后重试"
        )

@router.delete("/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除消息"""
    # 查找消息并验证权限
    message = db.query(Message).join(Conversation).filter(
        Message.id == message_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    try:
        db.delete(message)
        db.commit()
        
        return SuccessResponse(message="消息删除成功")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除消息失败，请稍后重试"
        )