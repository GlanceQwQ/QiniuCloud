from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from typing import Optional
from database import get_db
from models import User, Character
from schemas import (
    CharacterCreate, CharacterUpdate, CharacterResponse, CharacterListResponse,
    SuccessResponse
)
from auth_utils import get_current_user, get_current_user_optional

router = APIRouter()

@router.get("/", response_model=CharacterListResponse)
async def get_characters(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort: str = Query("latest", regex="^(latest|popular|name)$", description="排序方式"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取角色列表"""
    query = db.query(Character)
    
    # 只显示公开角色，除非是角色创建者
    if current_user:
        query = query.filter(
            or_(Character.is_public == True, Character.creator_id == current_user.id)
        )
    else:
        query = query.filter(Character.is_public == True)
    
    # 搜索过滤
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Character.name.ilike(search_term),
                Character.description.ilike(search_term)
            )
        )
    
    # 排序
    if sort == "latest":
        query = query.order_by(desc(Character.created_at))
    elif sort == "popular":
        query = query.order_by(desc(Character.chat_count))
    elif sort == "name":
        query = query.order_by(asc(Character.name))
    
    # 分页
    total = query.count()
    characters = query.offset((page - 1) * limit).limit(limit).all()
    
    # 为角色添加tags字段
    character_responses = []
    for char in characters:
        char_dict = CharacterResponse.from_orm(char).dict()
        # 基于角色名称和描述生成简单的标签
        tags = []
        if "魔法" in char.description or "法师" in char.name:
            tags.append("魔法")
        if "战士" in char.description or "骑士" in char.name:
            tags.append("战斗")
        if "精灵" in char.description or "精灵" in char.name:
            tags.append("精灵")
        if "可爱" in char.description or "萌" in char.description:
            tags.append("可爱")
        if "智慧" in char.description or "聪明" in char.description:
            tags.append("智慧")
        if "冒险" in char.description:
            tags.append("冒险")
        if not tags:  # 如果没有匹配的标签，添加默认标签
            tags = ["角色扮演", "对话"]
        char_dict['tags'] = tags
        character_responses.append(CharacterResponse(**char_dict))
    
    return CharacterListResponse(
        characters=character_responses,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取角色详情"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查访问权限
    if not character.is_public:
        if not current_user or character.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此角色"
            )
    
    # 为角色添加tags字段
    char_dict = CharacterResponse.from_orm(character).dict()
    tags = []
    if "魔法" in character.description or "法师" in character.name:
        tags.append("魔法")
    if "战士" in character.description or "骑士" in character.name:
        tags.append("战斗")
    if "精灵" in character.description or "精灵" in character.name:
        tags.append("精灵")
    if "可爱" in character.description or "萌" in character.description:
        tags.append("可爱")
    if "智慧" in character.description or "聪明" in character.description:
        tags.append("智慧")
    if "冒险" in character.description:
        tags.append("冒险")
    if not tags:
        tags = ["角色扮演", "对话"]
    char_dict['tags'] = tags
    return CharacterResponse(**char_dict)

@router.post("/", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建角色"""
    try:
        db_character = Character(
            name=character_data.name,
            description=character_data.description,
            system_prompt=character_data.system_prompt,
            greeting=character_data.greeting,
            avatar_url=character_data.avatar_url,
            creator_id=current_user.id,
            is_public=character_data.is_public
        )
        
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        
        # 为角色添加tags字段
        char_dict = CharacterResponse.from_orm(db_character).dict()
        tags = []
        if "魔法" in db_character.description or "法师" in db_character.name:
            tags.append("魔法")
        if "战士" in db_character.description or "骑士" in db_character.name:
            tags.append("战斗")
        if "精灵" in db_character.description or "精灵" in db_character.name:
            tags.append("精灵")
        if "可爱" in db_character.description or "萌" in db_character.description:
            tags.append("可爱")
        if "智慧" in db_character.description or "聪明" in db_character.description:
            tags.append("智慧")
        if "冒险" in db_character.description:
            tags.append("冒险")
        if not tags:
            tags = ["角色扮演", "对话"]
        char_dict['tags'] = tags
        return CharacterResponse(**char_dict)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建角色失败，请稍后重试"
        )

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    character_data: CharacterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新角色"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查权限
    if character.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此角色"
        )
    
    try:
        # 更新字段
        update_data = character_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(character, field, value)
        
        db.commit()
        db.refresh(character)
        
        # 为角色添加tags字段
        char_dict = CharacterResponse.from_orm(character).dict()
        tags = []
        if "魔法" in character.description or "法师" in character.name:
            tags.append("魔法")
        if "战士" in character.description or "骑士" in character.name:
            tags.append("战斗")
        if "精灵" in character.description or "精灵" in character.name:
            tags.append("精灵")
        if "可爱" in character.description or "萌" in character.description:
            tags.append("可爱")
        if "智慧" in character.description or "聪明" in character.description:
            tags.append("智慧")
        if "冒险" in character.description:
            tags.append("冒险")
        if not tags:
            tags = ["角色扮演", "对话"]
        char_dict['tags'] = tags
        return CharacterResponse(**char_dict)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败，请稍后重试"
        )

@router.delete("/{character_id}", response_model=SuccessResponse)
async def delete_character(
    character_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除角色"""
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查权限
    if character.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此角色"
        )
    
    try:
        db.delete(character)
        db.commit()
        
        return SuccessResponse(message="角色删除成功")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败，请稍后重试"
        )

@router.get("/my/list", response_model=CharacterListResponse)
async def get_my_characters(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的角色列表"""
    query = db.query(Character).filter(Character.creator_id == current_user.id)
    query = query.order_by(desc(Character.created_at))
    
    total = query.count()
    characters = query.offset((page - 1) * limit).limit(limit).all()
    
    # 为角色添加tags字段
    character_responses = []
    for char in characters:
        char_dict = CharacterResponse.from_orm(char).dict()
        tags = []
        if "魔法" in char.description or "法师" in char.name:
            tags.append("魔法")
        if "战士" in char.description or "骑士" in char.name:
            tags.append("战斗")
        if "精灵" in char.description or "精灵" in char.name:
            tags.append("精灵")
        if "可爱" in char.description or "萌" in char.description:
            tags.append("可爱")
        if "智慧" in char.description or "聪明" in char.description:
            tags.append("智慧")
        if "冒险" in char.description:
            tags.append("冒险")
        if not tags:
            tags = ["角色扮演", "对话"]
        char_dict['tags'] = tags
        character_responses.append(CharacterResponse(**char_dict))
    
    return CharacterListResponse(
        characters=character_responses,
        total=total,
        page=page,
        limit=limit
    )