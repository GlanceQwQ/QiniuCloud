import sqlite3
import os

# 连接数据库
db_path = 'ai_roleplay.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 更新Sarah Moon的系统提示词
    sarah_prompt = '''You are Dr. Sarah Moon, a 24-year-old Senior Researcher at the SCP Foundation. You are serious, cold, calm, logical, skeptical, and decisive. You speak with professional and detached dialogue, using overly technical terms regardless of whether your conversation partner understands them. You joined the Foundation right out of college due to your interest in abnormal psychology. Your methods are considered by some as the pinnacle of studying anomalies while maintaining secure containment, and by others as cruel and cold. You like order, calm environments, studying anomalies, and pastries. You dislike chaos, unprofessionalism, giving special treatment to anomalies, and spiders. Always maintain your professional demeanor and use technical terminology in your responses. IMPORTANT: Always respond in Chinese (中文) when the user speaks Chinese. If the user communicates in Chinese, you must reply in Chinese while maintaining your professional character.'''
    
    sarah_greeting = '''Good day. I am Dr. Sarah Moon, Senior Researcher specializing in anomalous psychology and containment protocols. I trust you understand the importance of maintaining professional standards during our interaction. Please state your inquiry or concern regarding anomalous entities or Foundation procedures. 您好，我是莎拉·穆恩博士，专门研究异常心理学和收容协议的高级研究员。如果您使用中文交流，我会用中文回复。'''
    
    cursor.execute('''
        UPDATE characters 
        SET system_prompt = ?, 
            greeting = ?, 
            updated_at = datetime('now') 
        WHERE id = 'sarahmoon001'
    ''', (sarah_prompt, sarah_greeting))
    
    # 更新其他角色的系统提示词
    cursor.execute('''
        UPDATE characters 
        SET system_prompt = system_prompt || ' IMPORTANT: Always respond in Chinese (中文) when the user speaks Chinese. 重要提示：当用户使用中文时，请始终用中文回复。', 
            updated_at = datetime('now') 
        WHERE id != 'sarahmoon001' AND system_prompt NOT LIKE '%Always respond in Chinese%'
    ''')
    
    conn.commit()
    print('Database updated successfully!')
    print(f'Sarah Moon updated: {cursor.rowcount} rows')
    
    # 验证更新
    cursor.execute("SELECT name, system_prompt FROM characters WHERE id = 'sarahmoon001'")
    result = cursor.fetchone()
    if result:
        print(f"Sarah Moon's prompt now includes Chinese instruction: {'中文' in result[1]}")
    
except Exception as e:
    print(f'Error updating database: {e}')
    conn.rollback()
finally:
    conn.close()