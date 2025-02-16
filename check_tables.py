import sqlite3

def check_tables():
    conn = sqlite3.connect('carbon_footprint.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables dans la base de données :")
    for table in tables:
        print(table[0])
    
    conn.close()

if __name__ == '__main__':
    check_tables() 