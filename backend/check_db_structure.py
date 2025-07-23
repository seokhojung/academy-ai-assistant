import sqlite3

conn = sqlite3.connect('academy.db')
cursor = conn.cursor()

print('=== 모든 테이블 구조 확인 ===')
tables = ['student', 'teacher', 'material', 'lecture']
for table in tables:
    cursor.execute(f'PRAGMA table_info({table})')
    columns = cursor.fetchall()
    cursor.execute(f'SELECT * FROM {table} LIMIT 1')
    sample = cursor.fetchone()
    print(f'\n{table.upper()} 테이블:')
    print(f'  컬럼 수: {len(columns)}')
    print(f'  실제 row 길이: {len(sample) if sample else 0}')
    for i, col in enumerate(columns):
        print(f'  {i}: {col[1]} ({col[2]})')
conn.close() 