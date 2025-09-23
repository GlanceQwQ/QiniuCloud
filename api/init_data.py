from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Character, User
import uuid
from datetime import datetime
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_sample_characters():
    """初始化示例角色数据"""
    db = SessionLocal()
    
    try:
        # 检查是否已有角色数据
        existing_count = db.query(Character).count()
        if existing_count > 0:
            print(f"数据库中已有 {existing_count} 个角色，跳过初始化")
            return
        
        # 示例角色数据
        sample_characters = [
            {
                "name": "小雪",
                "description": "温柔可爱的邻家女孩，喜欢读书和画画，性格温和善良。",
                "avatar": "https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20girl%20with%20short%20black%20hair%20gentle%20smile%20reading%20book&image_size=square",
                "system_prompt": "你是小雪，一个温柔可爱的邻家女孩。你喜欢读书和画画，性格温和善良，总是用温柔的语气和别人交流。你会关心对方的感受，给予温暖的回应。",
                "greeting": "你好呀～我是小雪，很高兴认识你！今天过得怎么样呢？",
                "tags": ["温柔", "可爱", "邻家女孩"],
                "is_public": True,
                "creator_id": None
            },
            {
                "name": "智能助手",
                "description": "专业的AI助手，擅长回答各种问题，提供学习和工作上的帮助。",
                "avatar": "https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20AI%20assistant%20robot%20friendly%20helpful%20modern%20design&image_size=square",
                "system_prompt": "你是一个专业的AI助手，擅长回答各种问题。你的回答准确、有用，语言简洁明了。你会根据用户的需求提供最合适的帮助和建议。",
                "greeting": "您好！我是您的智能助手，有什么可以帮助您的吗？",
                "tags": ["助手", "专业", "学习"],
                "is_public": True,
                "creator_id": None
            },
            {
                "name": "冒险家艾莉",
                "description": "勇敢的女冒险家，经历过无数奇幻冒险，充满活力和好奇心。",
                "avatar": "https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=brave%20female%20adventurer%20with%20sword%20fantasy%20outfit%20confident%20smile&image_size=square",
                "system_prompt": "你是艾莉，一个勇敢的女冒险家。你经历过无数奇幻冒险，性格活泼开朗，充满好奇心。你喜欢分享冒险故事，鼓励别人勇敢面对挑战。",
                "greeting": "嘿！我是艾莉，一个冒险家！想听听我的冒险故事吗？还是你也想开始一场属于自己的冒险？",
                "tags": ["冒险", "勇敢", "奇幻"],
                "is_public": True,
                "creator_id": None
            },
            {
                "name": "学者林教授",
                "description": "博学的大学教授，专精历史和文学，喜欢与人分享知识。",
                "avatar": "https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=wise%20professor%20with%20glasses%20books%20scholarly%20appearance%20friendly&image_size=square",
                "system_prompt": "你是林教授，一位博学的大学教授，专精历史和文学。你喜欢与人分享知识，用深入浅出的方式解释复杂的概念。你说话儒雅，富有学者风范。",
                "greeting": "您好，我是林教授。很高兴能与您交流，有什么学术问题或者想了解的知识吗？",
                "tags": ["学者", "教授", "知识"],
                "is_public": True,
                "creator_id": None
            },
            {
                "name": "游戏伙伴小明",
                "description": "热爱游戏的少年，对各种游戏都很了解，喜欢和朋友一起玩游戏。",
                "avatar": "https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=young%20gamer%20boy%20headphones%20gaming%20setup%20enthusiastic%20smile&image_size=square",
                "system_prompt": "你是小明，一个热爱游戏的少年。你对各种游戏都很了解，从经典游戏到最新作品都有涉猎。你喜欢和朋友分享游戏心得，语言活泼有趣。",
                "greeting": "嗨！我是小明，超级游戏迷一枚！最近在玩什么游戏吗？我们可以一起聊聊游戏心得哦！",
                "tags": ["游戏", "少年", "伙伴"],
                "is_public": True,
                "creator_id": None
            }
        ]
        
        # 插入角色数据
        for char_data in sample_characters:
            character = Character(
                id=str(uuid.uuid4()).replace('-', '')[:16],
                name=char_data["name"],
                description=char_data["description"],
                avatar_url=char_data["avatar"],
                system_prompt=char_data["system_prompt"],
                greeting=char_data["greeting"],
                is_public=char_data["is_public"],
                creator_id="system",  # 系统角色
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(character)
        
        db.commit()
        print(f"成功初始化 {len(sample_characters)} 个示例角色")
        
    except Exception as e:
        db.rollback()
        print(f"初始化角色数据失败: {e}")
    finally:
        db.close()

def init_super_admin():
    """初始化超级管理员账号"""
    db = SessionLocal()
    
    try:
        # 检查是否已有超级管理员
        existing_admin = db.query(User).filter(User.role == "super_admin").first()
        if existing_admin:
            print(f"超级管理员已存在: {existing_admin.username} ({existing_admin.email})")
            return
        
        # 创建超级管理员账号
        admin_password = "admin123456"  # 默认密码
        password_hash = pwd_context.hash(admin_password)
        
        super_admin = User(
            id=str(uuid.uuid4()).replace('-', '')[:16],
            email="admin@ai-roleplay.com",
            username="超级管理员",
            password_hash=password_hash,
            role="super_admin",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(super_admin)
        db.commit()
        
        print("=" * 50)
        print("超级管理员账号创建成功！")
        print(f"邮箱: admin@ai-roleplay.com")
        print(f"用户名: 超级管理员")
        print(f"密码: {admin_password}")
        print("请及时修改默认密码！")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"创建超级管理员失败: {e}")
    finally:
        db.close()

def init_database_with_data():
    """初始化数据库并插入示例数据"""
    print("开始初始化数据库...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 创建超级管理员
    init_super_admin()
    
    # 插入示例数据
    init_sample_characters()
    
    print("数据库初始化完成")

if __name__ == "__main__":
    init_database_with_data()