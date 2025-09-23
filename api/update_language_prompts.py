import sqlite3
import os

# 连接数据库
db_path = 'ai_roleplay.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 查看当前角色的system_prompt
    print("=== 当前角色的system_prompt ===")
    cursor.execute("SELECT id, name, system_prompt FROM characters")
    characters = cursor.fetchall()
    
    for char_id, name, system_prompt in characters:
        print(f"\n角色ID: {char_id}")
        print(f"角色名: {name}")
        print(f"System Prompt: {system_prompt[:300]}...")
        print("-" * 80)
    
    # 移除固定的中文回复指令
    print("\n=== 开始移除固定的语言指令 ===")
    
    # 移除包含中文回复指令的部分
    patterns_to_remove = [
        " IMPORTANT: Always respond in Chinese (中文) when the user speaks Chinese.",
        " IMPORTANT: Always respond in Chinese (中文) when the user speaks Chinese. 重要提示：当用户使用中文时，请始终用中文回复。",
        "IMPORTANT: Always respond in Chinese (中文) when the user speaks Chinese.",
        "重要提示：当用户使用中文时，请始终用中文回复。",
        "If the user communicates in Chinese, you must reply in Chinese while maintaining your professional character."
    ]
    
    for char_id, name, system_prompt in characters:
        original_prompt = system_prompt
        updated_prompt = system_prompt
        
        # 移除所有语言相关的指令
        for pattern in patterns_to_remove:
            updated_prompt = updated_prompt.replace(pattern, "")
        
        # 清理多余的空格和换行
        updated_prompt = updated_prompt.strip()
        updated_prompt = ' '.join(updated_prompt.split())
        
        if updated_prompt != original_prompt:
            cursor.execute("""
                UPDATE characters 
                SET system_prompt = ?, 
                    updated_at = datetime('now') 
                WHERE id = ?
            """, (updated_prompt, char_id))
            print(f"已更新角色: {name} ({char_id})")
            print(f"原始长度: {len(original_prompt)}, 更新后长度: {len(updated_prompt)}")
        else:
            print(f"角色 {name} ({char_id}) 无需更新")
    
    # 提交更改
    conn.commit()
    print("\n=== 数据库更新完成 ===")
    
    # 验证更新结果
    print("\n=== 验证更新结果 ===")
    cursor.execute("SELECT id, name, system_prompt FROM characters")
    updated_characters = cursor.fetchall()
    
    for char_id, name, system_prompt in updated_characters:
        has_chinese_instruction = "Always respond in Chinese" in system_prompt
        print(f"角色: {name} - 包含中文指令: {has_chinese_instruction}")
        if has_chinese_instruction:
            print(f"  警告: {name} 仍包含固定中文指令")
    
except Exception as e:
    print(f'错误: {e}')
    conn.rollback()
finally:
    conn.close()
    print("\n数据库连接已关闭")