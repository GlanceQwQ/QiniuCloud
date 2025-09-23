from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional
from database import get_db
from models import User, Conversation, Character
from schemas import ConversationListResponse, ConversationResponse, SuccessResponse
from auth_utils import get_current_user

router = APIRouter()

@router.get("/", response_model=ConversationListResponse)
async def get_conversations(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    character_id: Optional[str] = Query(None, description="角色ID过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的会话列表"""
    query = db.query(Conversation).options(
        joinedload(Conversation.character)
    ).filter(Conversation.user_id == current_user.id)
    
    # 按角色过滤
    if character_id:
        query = query.filter(Conversation.character_id == character_id)
    
    # 按最后消息时间排序
    query = query.order_by(desc(Conversation.last_message_at))
    
    # 分页
    total = query.count()
    conversations = query.offset((page - 1) * limit).limit(limit).all()
    
    return ConversationListResponse(
        conversations=[ConversationResponse.from_orm(conv) for conv in conversations],
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会话详情"""
    conversation = db.query(Conversation).options(
        joinedload(Conversation.character)
    ).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    return ConversationResponse.from_orm(conversation)

@router.delete("/{conversation_id}", response_model=SuccessResponse)
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除会话"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    try:
        db.delete(conversation)
        db.commit()
        
        return SuccessResponse(message="会话删除成功")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除会话失败，请稍后重试"
        )

@router.put("/{conversation_id}/summary", response_model=SuccessResponse)
async def update_conversation_summary(
    conversation_id: str,
    summary: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新会话摘要"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    try:
        conversation.summary = summary
        db.commit()
        
        return SuccessResponse(message="会话摘要更新成功")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新会话摘要失败，请稍后重试"
        )