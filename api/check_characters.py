import sqlite3

# 连接数据库
conn = sqlite3.connect('ai_roleplay.db')
cursor = conn.cursor()

# 查询角色信息
cursor.execute('SELECT id, name FROM characters LIMIT 5')
rows = cursor.fetchall()

print('数据库中的角色列表:')
for row in rows:
    print(f'ID: {row[0]}, 名称: {row[1]}')

conn.close()