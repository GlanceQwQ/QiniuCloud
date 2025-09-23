import sqlite3

# 连接数据库
conn = sqlite3.connect('ai_roleplay.db')
cursor = conn.cursor()

# 查询指定角色
character_id = 'd204cc07f5834d8b'
cursor.execute('SELECT id, name, description, creator_id FROM characters WHERE id = ?', (character_id,))
result = cursor.fetchone()

print(f'角色ID: {character_id}')
print(f'角色存在: {result is not None}')
if result:
    print(f'角色信息: ID={result[0]}, 名称={result[1]}, 描述={result[2]}, 创建者={result[3]}')
else:
    print('角色不存在')
    # 查看所有角色
    cursor.execute('SELECT id, name FROM characters LIMIT 5')
    all_chars = cursor.fetchall()
    print('\n现有角色:')
    for char in all_chars:
        print(f'  {char[0]} - {char[1]}')

conn.close()